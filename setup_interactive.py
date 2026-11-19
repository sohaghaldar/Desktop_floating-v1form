# -*- coding: utf-8 -*-
"""
Desktop Floating Spider - Interactive Installer & Setup Assistant
Checks dependencies, asks for user permission, installs required packages,
creates Desktop shortcuts with custom cyber icons, and launches the pet.
"""

import os
import sys
import subprocess
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def print_banner():
    print("=" * 66)
    print("      🕷️  DESKTOP FLOATING SPIDER — SETUP & INSTALLER  🕷️")
    print("   Physics-Driven Cyber Pet Ecosystem for Windows, Mac & Linux")
    print("=" * 66)
    print()

def ask_user_permission(prompt_text, default_yes=True):
    default_hint = "[Y/n]" if default_yes else "[y/N]"
    try:
        ans = input(f"{prompt_text} {default_hint}: ").strip().lower()
        if not ans:
            return default_yes
        return ans in ['y', 'yes', 'ha', 'hae', '1', 'true']
    except (KeyboardInterrupt, EOFError):
        print("\n[!] Setup cancelled by user.")
        sys.exit(0)

def check_and_install_dependencies():
    print("[1/3] Checking Python Dependencies...")
    required = ["PIL", "pystray"]
    missing = []

    for pkg in required:
        try:
            if pkg == "PIL":
                import PIL
            elif pkg == "pystray":
                import pystray
            print(f"  ✓ {pkg} is already installed.")
        except ImportError:
            missing.append(pkg)
            print(f"  ✗ {pkg} is missing.")

    if missing:
        print()
        print(f"Required package(s) needed: {', '.join(missing)}")
        allow = ask_user_permission("Do you want to automatically install them via pip now?", default_yes=True)
        if allow:
            print("\n>> Installing dependencies via pip... Please wait...")
            req_file = os.path.join(ROOT_DIR, "requirements.txt")
            if os.path.exists(req_file):
                cmd = [sys.executable, "-m", "pip", "install", "-r", req_file]
            else:
                cmd = [sys.executable, "-m", "pip", "install", "Pillow>=9.0.0", "pystray>=0.19.4"]
            
            ret = subprocess.call(cmd)
            if ret == 0:
                print("  ✓ All dependencies installed successfully!\n")
            else:
                print("  [!] Error installing dependencies via pip. Please check your internet connection.\n")
        else:
            print("  [-] Skipped package installation by user request.\n")
    else:
        print("  ✓ All required dependencies are present!\n")

def create_desktop_shortcut():
    if sys.platform != "win32":
        return

    print("[2/3] Desktop Shortcut Setup...")
    allow = ask_user_permission("Do you want to create a 'Desktop Floating' shortcut on your Desktop?", default_yes=True)
    if not allow:
        print("  [-] Skipped desktop shortcut creation.\n")
        return

    try:
        desktop_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
        if not os.path.exists(desktop_dir):
            desktop_dir = os.path.expanduser("~/Desktop")

        shortcut_path = os.path.join(desktop_dir, "Desktop Floating.lnk")
        icon_path = os.path.join(ROOT_DIR, "assets", "desktop_floating.ico")
        target_script = os.path.join(ROOT_DIR, "desktop_spider.py")
        
        # Look for compiled .exe first if present
        dist_exe = os.path.join(ROOT_DIR, "dist", "DesktopFloatingSpider.exe")
        single_exe = os.path.join(ROOT_DIR, "DesktopFloatingSpider.exe")
        
        if os.path.exists(dist_exe):
            target_path = dist_exe
            arguments = ""
        elif os.path.exists(single_exe):
            target_path = single_exe
            arguments = ""
        else:
            # Use pythonw.exe so no black command prompt appears
            py_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(py_dir, "pythonw.exe")
            if not os.path.exists(pythonw):
                pythonw = sys.executable
            target_path = pythonw
            arguments = f'"{target_script}"'

        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.Arguments = '{arguments}'
$Shortcut.WorkingDirectory = "{ROOT_DIR}"
$Shortcut.IconLocation = "{icon_path}, 0"
$Shortcut.Description = "Desktop Floating Spider — Interactive Pet"
$Shortcut.Save()
'''
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True, stdout=subprocess.DEVNULL)
        print(f"  ✓ Desktop shortcut created at: {shortcut_path}\n")
    except Exception as e:
        print(f"  [!] Notice: Could not create desktop shortcut automatically: {e}\n")

def launch_pet():
    print("[3/3] Launch Desktop Pet...")
    allow = ask_user_permission("Do you want to launch Desktop Floating Spider now?", default_yes=True)
    if allow:
        print("\n>> Launching Desktop Floating Spider in background...")
        target_script = os.path.join(ROOT_DIR, "desktop_spider.py")
        if sys.platform == "win32":
            py_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(py_dir, "pythonw.exe")
            target_exe = pythonw if os.path.exists(pythonw) else sys.executable
            subprocess.Popen([target_exe, target_script], cwd=ROOT_DIR)
        else:
            subprocess.Popen([sys.executable, target_script], cwd=ROOT_DIR)
        print("  ✓ Spider launched! Enjoy your desktop companion.\n")
    else:
        print("  [-] You can start it anytime with 'run_spider.bat' or the Desktop shortcut.\n")

def main():
    print_banner()
    check_and_install_dependencies()
    create_desktop_shortcut()
    launch_pet()
    print("=" * 66)
    print("                  ✨ SETUP COMPLETE! ✨")
    print("=" * 66)

if __name__ == "__main__":
    main()
