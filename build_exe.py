# -*- coding: utf-8 -*-
"""
PyInstaller Build Automation for Desktop Floating Spider
Builds single-file and directory distributions for Windows.
"""

import os
import sys
import subprocess
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("=" * 60)
    print(" Building Desktop Floating Spider Standalone Executable (.exe)")
    print("=" * 60)

    icon_path = os.path.join(ROOT_DIR, "assets", "desktop_floating.ico")
    main_script = os.path.join(ROOT_DIR, "desktop_spider.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name", "DesktopFloatingSpider",
        "--icon", icon_path,
        "--add-data", f"{os.path.join(ROOT_DIR, 'assets')};assets",
        "--add-data", f"{os.path.join(ROOT_DIR, 'locales')};locales",
        "--add-data", f"{os.path.join(ROOT_DIR, 'settings.json')};.",
        "--add-data", f"{os.path.join(ROOT_DIR, 'VERSION')};.",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "pystray",
        "--hidden-import", "pystray._win32",
        "--onefile",
        main_script
    ]

    print("Running PyInstaller command:")
    print(" ".join(cmd))
    print()

    ret = subprocess.call(cmd, cwd=ROOT_DIR)
    if ret != 0:
        print("\n[!] PyInstaller build failed!")
        sys.exit(ret)

    dist_exe = os.path.join(ROOT_DIR, "dist", "DesktopFloatingSpider.exe")
    if os.path.exists(dist_exe):
        size_mb = os.path.getsize(dist_exe) / (1024 * 1024)
        print(f"\n✓ Successfully compiled: {dist_exe} ({size_mb:.2f} MB)")
    else:
        print("\n[!] Executable not found in dist/")

if __name__ == "__main__":
    build()
