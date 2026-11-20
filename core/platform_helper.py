# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Cross-Platform OS Abstraction Layer
Supports Windows, Linux, and macOS natively.
"""

import sys
import os
import time
import threading
import subprocess
import tempfile
import atexit

from core.config import IS_WINDOWS, IS_MACOS, IS_LINUX, parse_hotkey_combo

if IS_WINDOWS:
    try:
        import winsound
    except Exception:
        winsound = None
    try:
        import ctypes
        import ctypes.wintypes

        # Initialize OS-level Dark Mode preference (uxtheme ordinal 135)
        try:
            uxtheme = ctypes.windll.uxtheme
            kernel32 = ctypes.windll.kernel32
            kernel32.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            kernel32.GetProcAddress.restype = ctypes.c_void_p
            p135 = kernel32.GetProcAddress(ctypes.c_void_p(uxtheme._handle), ctypes.c_void_p(135))
            if p135:
                ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int)(p135)(2)  # 2 = ForceDark
        except Exception:
            pass
    except Exception:
        pass
else:
    winsound = None
    try:
        import ctypes
    except Exception:
        pass

_instance_lock_handle = None


def enforce_single_instance():
    """Acquire a process lock without terminating another process."""
    global _instance_lock_handle
    if IS_WINDOWS:
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
            kernel32.CreateMutexW.restype = ctypes.wintypes.HANDLE
            handle = kernel32.CreateMutexW(None, True, "DesktopSpiderOverlaySingleInstanceMutex_v2")
            if not handle:
                return False
            if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                user32 = ctypes.windll.user32
                found_hwnd = None

                def _enum_cb(h, l):
                    nonlocal found_hwnd
                    length = user32.GetWindowTextLengthW(h)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(h, buf, length + 1)
                        t = buf.value
                        if "Desktop Spider" in t or "ডেস্কটপ স্পাইডার" in t or "Desktop Pet Ecosystem" in t:
                            found_hwnd = h
                            return False
                    return True

                try:
                    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
                    user32.EnumWindows(WNDENUMPROC(_enum_cb), 0)
                    if found_hwnd:
                        user32.ShowWindow(found_hwnd, 9)  # SW_RESTORE
                        user32.SetForegroundWindow(found_hwnd)
                except Exception:
                    pass
                kernel32.CloseHandle(handle)
                return False
            _instance_lock_handle = handle
            return True
        except Exception:
            # If native mutex setup fails, allow startup rather than killing processes.
            return True

    try:
        import fcntl
        lock_path = os.path.join(tempfile.gettempdir(), "desktop_spider_companion.lock")
        _instance_lock_handle = open(lock_path, "a+")
        try:
            fcntl.flock(_instance_lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, OSError):
            _instance_lock_handle.close()
            _instance_lock_handle = None
            return False
        _instance_lock_handle.seek(0)
        _instance_lock_handle.truncate()
        _instance_lock_handle.write(str(os.getpid()))
        _instance_lock_handle.flush()
        return True
    except Exception:
        # A lock failure must not risk terminating an unrelated process.
        return True


def _release_instance_lock():
    global _instance_lock_handle
    if _instance_lock_handle is not None:
        try:
            if IS_WINDOWS:
                ctypes.windll.kernel32.ReleaseMutex(_instance_lock_handle)
                ctypes.windll.kernel32.CloseHandle(_instance_lock_handle)
            else:
                _instance_lock_handle.close()
        except Exception:
            pass
        _instance_lock_handle = None


atexit.register(_release_instance_lock)

class PlatformHelper:
    """Cross-Platform OS Abstraction Layer for Windows, Linux, and macOS."""
    _active_keys = set()
    _last_user_time = time.time()

    @classmethod
    def get_screen_bounds(cls, root):
        """Returns (x, y, w, h) for the desktop display area."""
        if IS_WINDOWS:
            try:
                u32 = ctypes.windll.user32
                sx = u32.GetSystemMetrics(76)
                sy = u32.GetSystemMetrics(77)
                sw = u32.GetSystemMetrics(78)
                sh = u32.GetSystemMetrics(79)
                if sw > 0 and sh > 0:
                    return sx, sy, sw, sh
            except Exception:
                pass
        try:
            root.update_idletasks()
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            return 0, 0, sw, sh
        except Exception:
            return 0, 0, 1920, 1080

    @classmethod
    def setup_window_transparency(cls, root, canvas, transparent_color="#010101"):
        """Configures full-screen borderless transparent window across platforms."""
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        if IS_WINDOWS:
            try:
                root.attributes("-transparentcolor", transparent_color)
                root.config(bg=transparent_color)
            except Exception:
                pass
        elif IS_MACOS:
            try:
                root.attributes("-transparent", True)
            except Exception:
                try: root.attributes("-alpha", 0.98)
                except Exception: pass
            root.config(bg="")
        else: # Linux
            try:
                root.attributes("-alpha", 0.98)
            except Exception:
                pass
            root.config(bg=transparent_color)

    @classmethod
    def make_click_through(cls, root):
        """Enables transparent click-through so user can click windows behind pet."""
        if IS_WINDOWS:
            try:
                u32 = ctypes.windll.user32
                hwnd = u32.GetParent(root.winfo_id()) or root.winfo_id()
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                WS_EX_TRANSPARENT = 0x00000020
                WS_EX_TOOLWINDOW = 0x00000080
                WS_EX_APPWINDOW = 0x00040000
                style = u32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                new_style = (style | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
                u32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                cls.ensure_topmost(root, hwnd)
                return hwnd
            except Exception as e:
                print("Windows click-through setup warning:", e)
                return None
        return None

    @classmethod
    def ensure_topmost(cls, root, hwnd=None):
        """Ensures overlay stays on top across all OSs."""
        try:
            if IS_WINDOWS and hwnd:
                HWND_TOPMOST = -1
                SWP_FLAGS = 0x0001 | 0x0002 | 0x0010 | 0x0040
                ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS)
        except Exception:
            pass
        try:
            root.lift()
            root.attributes("-topmost", True)
        except Exception:
            pass

    @classmethod
    def set_app_user_model_id(cls, app_id="antigravity.desktoppet.spider.ecosystem.v2"):
        """Sets Windows AppUserModelID so taskbar groups properly and displays the custom icon."""
        if IS_WINDOWS:
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except Exception:
                pass

    @classmethod
    def apply_dark_titlebar(cls, window):
        """Enforces Windows 10/11 immersive dark titlebar on a Tk/Toplevel window with frame redraw."""
        if not IS_WINDOWS:
            return
        try:
            window.update_idletasks()
            hwnd = int(window.wm_frame(), 16) if hasattr(window, "wm_frame") else (
                ctypes.windll.user32.GetParent(window.winfo_id()) or window.winfo_id()
            )
            # Only Windows 11 (build >= 22000) supports native immersive dark titlebar properly.
            # On Windows 10 (build < 22000), DWM attribute 20 causes an ugly black highlight box behind the title text.
            win_build = sys.getwindowsversion().build if hasattr(sys, "getwindowsversion") else 0
            if win_build >= 22000:
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
                )
                # DWMWA_CAPTION_COLOR = 35, DWMWA_TEXT_COLOR = 36
                dark_bg = ctypes.c_int(0x00160D09)   # #090d16 in BGR
                text_col = ctypes.c_int(0x00F8BD38)  # #38bdf8 in BGR
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(dark_bg), ctypes.sizeof(dark_bg))
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(text_col), ctypes.sizeof(text_col))
            else:
                # On Windows 10, explicitly ensure attribute 20 is OFF so caption text renders natively with transparent background
                val_off = ctypes.c_int(0)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 20, ctypes.byref(val_off), ctypes.sizeof(val_off)
                )

            # Redraw non-client frame
            SWP_FLAGS = 0x0020 | 0x0002 | 0x0001 | 0x0004 | 0x0010  # FRAMECHANGED | NOMOVE | NOSIZE | NOZORDER | NOACTIVATE
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_FLAGS)
        except Exception:
            pass

    @classmethod
    def force_taskbar_presence(cls, window):
        """Forces a top-level window to appear cleanly on the Windows Taskbar."""
        if not IS_WINDOWS:
            return
        try:
            window.update_idletasks()
            hwnd = int(window.wm_frame(), 16) if hasattr(window, "wm_frame") else window.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            ex = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_ex = (ex & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_ex)
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
        except Exception:
            pass

    @classmethod
    def get_mouse_pos(cls, root=None):
        """Universal cross-platform mouse pointer position."""
        if IS_WINDOWS:
            try:
                pt = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                return pt.x, pt.y
            except Exception:
                pass
        if root:
            try:
                x, y = root.winfo_pointerxy()
                if -100 <= x <= 10000 and -100 <= y <= 10000:
                    return x, y
            except Exception:
                pass
        return 0, 0

    @classmethod
    def get_cursor_pos(cls, root=None):
        """Alias for get_mouse_pos."""
        return cls.get_mouse_pos(root)

    @classmethod
    def set_cursor_pos(cls, x, y):
        """Shoves / repositions mouse cursor (playful attack mechanic)."""
        if IS_WINDOWS:
            try:
                ctypes.windll.user32.SetCursorPos(int(x), int(y))
            except Exception:
                pass
        elif IS_LINUX:
            try:
                subprocess.run(["xdotool", "mousemove", str(int(x)), str(int(y))],
                               capture_output=True, timeout=0.1)
            except Exception:
                pass

    @classmethod
    def get_system_idle_seconds(cls):
        """Returns seconds since last keyboard or mouse input."""
        if IS_WINDOWS:
            try:
                class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [("cbSize", ctypes.wintypes.UINT), ("dwTime", ctypes.wintypes.DWORD)]
                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                    tick = ctypes.windll.kernel32.GetTickCount()
                    return max(0.0, (tick - lii.dwTime) / 1000.0)
            except Exception:
                pass
        elif IS_LINUX:
            try:
                out = subprocess.check_output(["xprintidle"], timeout=0.2).decode().strip()
                if out.isdigit():
                    return float(out) / 1000.0
            except Exception:
                pass
        return max(0.0, time.time() - cls._last_user_time)

    @classmethod
    def is_hotkey_down(cls, hk_str):
        """Checks customizable hotkey state cross-platform."""
        if IS_WINDOWS:
            try:
                need_shift, need_ctrl, need_alt, vk = parse_hotkey_combo(hk_str)
                if not vk:
                    return False
                u32 = ctypes.windll.user32
                shift_pressed = bool(u32.GetAsyncKeyState(0x10) & 0x8000)
                ctrl_pressed = bool(u32.GetAsyncKeyState(0x11) & 0x8000)
                alt_pressed = bool(u32.GetAsyncKeyState(0x12) & 0x8000)
                key_pressed = bool(u32.GetAsyncKeyState(vk) & 0x8000)
                if need_shift != shift_pressed: return False
                if need_ctrl != ctrl_pressed: return False
                if need_alt != alt_pressed: return False
                return key_pressed
            except Exception:
                return False
        else:
            combo = hk_str.upper().strip()
            return combo in cls._active_keys

    @classmethod
    def is_user_typing(cls, now, last_keyboard_time):
        """Checks if user is currently typing in another app right at this instant."""
        if IS_WINDOWS:
            try:
                u32 = ctypes.windll.user32
                common_vks = [0x08, 0x09, 0x0D, 0x20, 0x25, 0x26, 0x27, 0x28, 0x2E] + list(range(0x30, 0x3A)) + list(range(0x41, 0x5B))
                for vk in common_vks:
                    if u32.GetAsyncKeyState(vk) & 0x8000:
                        return True
                return False
            except Exception:
                pass
        return False

    @classmethod
    def is_autostart_enabled(cls):
        """Check autostart state across Windows, Linux, and macOS."""
        if IS_WINDOWS:
            startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
            return os.path.exists(os.path.join(startup_dir, "DesktopPet_AutoStart.vbs"))
        elif IS_LINUX:
            desktop_file = os.path.expanduser("~/.config/autostart/desktop-pet-ecosystem.desktop")
            return os.path.exists(desktop_file)
        elif IS_MACOS:
            plist_file = os.path.expanduser("~/Library/LaunchAgents/com.desktoppet.ecosystem.plist")
            return os.path.exists(plist_file)
        return False

    @classmethod
    def set_autostart(cls, enable=True, target_script=None):
        """Configures autostart on Windows, Linux, and macOS."""
        if not target_script:
            target_script = os.path.abspath(__file__)
        work_dir = os.path.dirname(target_script)
        if IS_WINDOWS:
            startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
            vbs_path = os.path.join(startup_dir, "DesktopPet_AutoStart.vbs")
            if enable:
                content = f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.CurrentDirectory = "{work_dir}"\nWshShell.Run "pythonw.exe """ & "{target_script}""" & "", 0, False\n'
                try:
                    with open(vbs_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    print("Windows autostart error:", e)
            else:
                if os.path.exists(vbs_path):
                    try: os.remove(vbs_path)
                    except Exception: pass
        elif IS_LINUX:
            auto_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(auto_dir, exist_ok=True)
            desktop_path = os.path.join(auto_dir, "desktop-pet-ecosystem.desktop")
            if enable:
                content = f"[Desktop Entry]\nType=Application\nVersion=1.0\nName=Desktop Pet Ecosystem\nComment=Interactive Animated Desktop Companion\nExec=python3 \"{target_script}\"\nPath={work_dir}\nTerminal=false\nCategories=Utility;Amusement;\n"
                try:
                    with open(desktop_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    print("Linux autostart error:", e)
            else:
                if os.path.exists(desktop_path):
                    try: os.remove(desktop_path)
                    except Exception: pass
        elif IS_MACOS:
            agent_dir = os.path.expanduser("~/Library/LaunchAgents")
            os.makedirs(agent_dir, exist_ok=True)
            plist_path = os.path.join(agent_dir, "com.desktoppet.ecosystem.plist")
            if enable:
                content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.desktoppet.ecosystem</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{target_script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>{work_dir}</string>
</dict>
</plist>'''
                try:
                    with open(plist_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception as e:
                    print("macOS autostart error:", e)
            else:
                if os.path.exists(plist_path):
                    try: os.remove(plist_path)
                    except Exception: pass

    @classmethod
    def play_audio(cls, freq1, dur1, freq2=None, dur2=None):
        """Play subtle sound in background daemon thread without GUI lag across all platforms."""
        def _run():
            try:
                if IS_WINDOWS and winsound:
                    winsound.Beep(int(freq1), int(dur1))
                    if freq2 and dur2:
                        winsound.Beep(int(freq2), int(dur2))
                elif IS_MACOS:
                    subprocess.run(["osascript", "-e", "beep 1"], capture_output=True, timeout=0.5)
                elif IS_LINUX:
                    sys.stdout.write("\a")
                    sys.stdout.flush()
            except Exception:
                pass
        threading.Thread(target=_run, daemon=True).start()

def play_audio(freq1, dur1, freq2=None, dur2=None):
    PlatformHelper.play_audio(freq1, dur1, freq2, dur2)

def is_hotkey_down(hk_str):
    return PlatformHelper.is_hotkey_down(hk_str)

