import win32api
import win32con
import win32gui
import win32process
import win32security
from win32com.client import GetObject
import struct
import time
import vulkan as vk

class SpeedMem:
    """Класс для быстрого чтения и записи памяти процесса на Windows 10/11 x64."""
    
    def __init__(self, process_name: str):
        """Инициализация с именем процесса (например, 'notepad.exe')."""
        self.process_name = process_name
        self.process_handle = None
        self.pid = self._get_pid()
        self._open_process()

    def _get_pid(self) -> int:
        """Получить ID процесса по его имени."""
        wmi = GetObject('winmgmts:')
        processes = wmi.ExecQuery(f'SELECT * FROM Win32_Process WHERE Name = "{self.process_name}"')
        for process in processes:
            return process.ProcessId
        raise ValueError(f"Процесс '{self.process_name}' не найден")

    def _open_process(self):
        """Открыть процесс с полным доступом."""
        privileges = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
        h_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), privileges)
        win32security.AdjustTokenPrivileges(h_token, False, [(win32security.LookupPrivilegeValue(None, win32security.SE_DEBUG_NAME), win32security.SE_PRIVILEGE_ENABLED)])
        
        access = win32con.PROCESS_VM_READ | win32con.PROCESS_VM_WRITE | win32con.PROCESS_VM_OPERATION
        self.process_handle = win32api.OpenProcess(access, False, self.pid)
        if not self.process_handle:
            raise RuntimeError("Не удалось открыть процесс")

    def read_memory(self, address: int, size: int) -> bytes:
        """Прочитать 'size' байт из памяти по адресу 'address'."""
        try:
            buffer = win32process.ReadProcessMemory(self.process_handle, address, size)
            return buffer
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения памяти по адресу {hex(address)}: {e}")

    def write_memory(self, address: int, data: bytes):
        """Записать 'data' байт в память по адресу 'address'."""
        try:
            win32process.WriteProcessMemory(self.process_handle, address, data)
        except Exception as e:
            raise RuntimeError(f"Ошибка записи памяти по адресу {hex(address)}: {e}")

    def read_int32(self, address: int) -> int:
        """Прочитать 32-битное целое число из памяти."""
        data = self.read_memory(address, 4)
        return struct.unpack('<I', data)[0]

    def write_int32(self, address: int, value: int):
        """Записать 32-битное целое число в память."""
        data = struct.pack('<I', value)
        self.write_memory(address, data)

    def close(self):
        """Закрыть дескриптор процесса."""
        if self.process_handle:
            win32api.CloseHandle(self.process_handle)
            self.process_handle = None

    def __del__(self):
        """Гарантировать закрытие дескриптора при удалении объекта."""
        self.close()

class OverlayWindow:
    """Класс для создания высокопроизводительного оверлейного окна с Vulkan."""
    
    def __init__(self, title: str, width: int = 300, height: int = 200):
        """Инициализация окна с заголовком, шириной и высотой."""
        self.title = title
        self.width = width
        self.height = height
        self.hwnd = None
        self.instance = None
        self.surface = None
        self.physical_device = None
        self.device = None
        self.swapchain = None
        self.running = False
        self._create_window()
        self._init_vulkan()

    def _create_window(self):
        """Создать прозрачное оверлейное окно."""
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = 'SpeedMemOverlayVK'
        wc.lpfnWndProc = self._wnd_proc
        win32gui.RegisterClass(wc)

        ex_style = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
        style = win32con.WS_POPUP | win32con.WS_VISIBLE

        self.hwnd = win32gui.CreateWindowEx(
            ex_style,
            wc.lpszClassName,
            self.title,
            style,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            self.width,
            self.height,
            0, 0, 0, None
        )

        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_ALPHA)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)

    def _init_vulkan(self):
        """Инициализация Vulkan для рендеринга."""
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="SpeedMem Overlay",
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName="No Engine",
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_API_VERSION_1_0
        )

        extensions = [vk.VK_KHR_SURFACE_EXTENSION_NAME, vk.VK_KHR_WIN32_SURFACE_EXTENSION_NAME]
        self.instance = vk.vkCreateInstance(
            vk.VkInstanceCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
                pApplicationInfo=app_info,
                enabledExtensionCount=len(extensions),
                ppEnabledExtensionNames=extensions
            )
        )

        surface_info = vk.VkWin32SurfaceCreateInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR,
            hinstance=win32api.GetModuleHandle(None),
            hwnd=self.hwnd
        )
        self.surface = vk.vkCreateWin32SurfaceKHR(self.instance, surface_info)

        physical_devices = vk.vkEnumeratePhysicalDevices(self.instance)
        self.physical_device = physical_devices[0]

        queue_family_index = 0
        device_info = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=1,
            pQueueCreateInfos=[
                vk.VkDeviceQueueCreateInfo(
                    sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
                    queueFamilyIndex=queue_family_index,
                    queueCount=1,
                    pQueuePriorities=[1.0]
                )
            ],
            enabledExtensionCount=1,
            ppEnabledExtensionNames=[vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
        )
        self.device = vk.vkCreateDevice(self.physical_device, device_info)

        swapchain_info = vk.VkSwapchainCreateInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            surface=self.surface,
            minImageCount=2,
            imageFormat=vk.VK_FORMAT_B8G8R8A8_UNORM,
            imageColorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR,
            imageExtent=vk.VkExtent2D(width=self.width, height=self.height),
            imageArrayLayers=1,
            imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            preTransform=vk.VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR,
            compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=vk.VK_PRESENT_MODE_FIFO_KHR,
            clipped=vk.VK_TRUE
        )
        self.swapchain = vk.vkCreateSwapchainKHR(self.device, swapchain_info)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """Обработка сообщений окна."""
        if msg == win32con.WM_DESTROY:
            self.running = False
            win32gui.PostQuitMessage(0)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def update(self):
        """Отрисовка оверлея с помощью Vulkan."""
        if not self.running:
            self.running = True
            try:
                while self.running:
                    if win32gui.PeekMessage(self.hwnd, win32con.WM_QUIT, win32con.WM_QUIT, win32con.PM_REMOVE):
                        self.running = False
                    time.sleep(0.001)
            finally:
                self.close()

    def close(self):
        """Закрыть окно и освободить ресурсы Vulkan."""
        if self.swapchain:
            vk.vkDestroySwapchainKHR(self.device, self.swapchain)
            self.swapchain = None
        if self.device:
            vk.vkDestroyDevice(self.device)
            self.device = None
        if self.surface:
            vk.vkDestroySurfaceKHR(self.instance, self.surface)
            self.surface = None
        if self.instance:
            vk.vkDestroyInstance(self.instance)
            self.instance = None
        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)
            self.hwnd = None

    def __del__(self):
        """Гарантировать освобождение ресурсов при удалении."""
        self.close()

if __name__ == "__main__":
    try:
        mem = SpeedMem("notepad.exe")
        address = 0x7FF712345678
        value = mem.read_int32(address)
        print(f"Прочитано: {value}")
        mem.write_int32(address, value + 1)
        print(f"Записано: {value + 1}")
        mem.close()

        overlay = OverlayWindow("SpeedMem Vulkan Overlay")
        print("Оверлейное окно создано. Нажмите Ctrl+C для закрытия.")
        overlay.update()
    except Exception as e:
        print(f"Ошибка: {e}")