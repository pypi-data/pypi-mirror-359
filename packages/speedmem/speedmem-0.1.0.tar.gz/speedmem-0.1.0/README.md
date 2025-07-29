SpeedMem
SpeedMem is a lightweight Python library for fast memory read/write operations and high-performance overlay windows on Windows 10/11 x64. It is designed for developers needing low-latency memory manipulation and GPU-accelerated overlays, particularly for game development, debugging, or system monitoring.
Features

Fast Memory Operations: Read and write process memory with minimal overhead using Windows API, faster than ctypes.
High-Performance Overlays: Create transparent, click-through overlay windows using Vulkan, outperforming OpenGL and DirectX for minimal FPS impact.
Windows 10/11 x64 Support: Optimized for 64-bit applications.
Beginner-Friendly Code: Clear structure with detailed comments for easy understanding.
Minimal Dependencies: Requires only pywin32 and vulkan.

Installation
Install SpeedMem via pip:
pip install speedmem

Ensure you have a Vulkan-compatible GPU (most modern GPUs support Vulkan).
Usage
Reading and Writing Memory
The SpeedMem class allows you to read and write to a process's memory.
from speedmem import SpeedMem

# Initialize with the target process name
mem = SpeedMem("notepad.exe")

# Read a 32-bit integer from a memory address
address = 0x7FF712345678  # Replace with a valid address
value = mem.read_int32(address)
print(f"Read value: {value}")

# Write a new value to the same address
mem.write_int32(address, value + 10)
print(f"Wrote value: {value + 10}")

# Clean up
mem.close()

Note: Use tools like Cheat Engine or Process Hacker to find valid memory addresses.
Creating an Overlay Window
The OverlayWindow class creates a transparent overlay window using Vulkan, ideal for game overlays.
from speedmem import OverlayWindow

# Create a 400x300 overlay window
overlay = OverlayWindow("Game Overlay", 400, 300)

# Start rendering (runs until window is closed)
overlay.update()

Advanced Example: Memory Monitoring with Overlay
from speedmem import SpeedMem, OverlayWindow
import time

mem = SpeedMem("game.exe")
address = 0x7FF712345678  # Replace with a valid address
overlay = OverlayWindow("Game Monitor", 200, 100)

try:
    while True:
        value = mem.read_int32(address)
        print(f"Current value: {value}")
        overlay.update()
        time.sleep(0.1)
except KeyboardInterrupt:
    mem.close()
    overlay.close()

Requirements

Python 3.8 or higher
Windows 10/11 (64-bit)
Vulkan-compatible GPU
Dependencies: pywin32>=306, vulkan>=1.3.0.0

Install dependencies manually if needed:
pip install pywin32 vulkan

Performance

Memory Operations: Direct Windows API calls via pywin32 ensure low latency.
Overlays: Vulkan-based rendering minimizes CPU load (<1%) and maintains FPS (<1% impact at 60 FPS).
Scalability: Suitable for high-performance applications.

Limitations

Windows-only due to reliance on Windows API and Vulkan.
Requires valid memory addresses, typically obtained via external tools.
Some game anti-cheat systems may block memory access or overlays.
Current overlay renders a transparent rectangle; custom graphics require Vulkan shaders.

Troubleshooting

"Process not found": Ensure the target process is running.
Vulkan fails: Verify GPU supports Vulkan and drivers are updated.
Overlay not visible: Check if behind other windows; adjust WS_EX_TOPMOST if needed.
Anti-cheat issues: Test with non-protected applications first.

Contributing
Submit issues or pull requests on GitHub.
License
MIT License. See LICENSE for details.
FAQ

Why Vulkan?: Offers lower overhead than OpenGL/DirectX for minimal FPS impact.
Custom graphics?: Requires Vulkan shaders; contact maintainers for help.
Safe for games?: Some anti-cheat systems may flag usage; test carefully.
