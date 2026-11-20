"""
================================================================================
🕷️ Desktop Pet Ecosystem (Desktop Spider & Creatures)
Cross-Platform Python Overlay Companion (Windows, Linux, macOS)
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import urllib.request
import urllib.parse
import sys
import math
import time
import random
import os
import sys
import threading
import atexit

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
try:
    os.chdir(ROOT_DIR)
except Exception:
    pass

# Ensure stdout and stderr never raise NoneType errors under pythonw or GUI launchers
if sys.stdout is None:
    try:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass
if sys.stderr is None:
    try:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass

APP_VERSION = "2.6.0"


def _as_bool(value, default=False):
    """Read bool settings stored as JSON booleans or legacy text values."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off", ""}:
            return False
    return default

IS_WINDOWS = (sys.platform == "win32")
IS_MACOS = (sys.platform == "darwin")
IS_LINUX = sys.platform.startswith("linux")

if IS_WINDOWS:
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('antigravity.desktopspider.pet.2.6')
    except Exception:
        pass

if IS_WINDOWS:
    try:
        import winsound
    except Exception:
        winsound = None
    try:
        import ctypes
        import ctypes.wintypes
    except Exception:
        pass
else:
    winsound = None
    try:
        import ctypes
    except Exception:
        pass

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Force Windows 10/11 Dark Mode for Win32 popups and menus
if IS_WINDOWS:
    try:
        ctypes.windll.uxtheme[135](2)
    except Exception:
        pass

# Enable per-monitor DPI awareness on Windows
if IS_WINDOWS:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ==============================================================================
# CORE SYSTEM & PLATFORM MODULES (Modular Architecture)
# ==============================================================================
from core.config import (
    APP_VERSION,
    IS_WINDOWS,
    IS_MACOS,
    IS_LINUX,
    ROOT_DIR,
    SETTINGS_FILE,
    LOCALES_DIR,
    THEMES,
    SPIDER_MODELS,
    DEFAULT_SETTINGS,
    load_config,
    save_config_value,
    save_full_settings,
    parse_hotkey_combo,
    get_vk_code,
)

from core.platform_helper import (
    PlatformHelper,
    is_hotkey_down,
    enforce_single_instance,
    kill_running_instance,
    play_audio,
)

# Set custom AppUserModelID early so taskbar groups properly and displays the custom pet icon
if IS_WINDOWS:
    PlatformHelper.set_app_user_model_id("antigravity.desktoppet.spider.ecosystem.v2")

from core.i18n import (
    I18n,
    I18nManager,
    WORLD_LANGUAGES,
)

from core.updater import (
    GitHubAutoUpdater,
)

from core.ui_widgets import (
    ModernSlider,
    HotkeyRecorderButton,
)

# ==============================================================================
# MODULAR CREATURE COMPANIONS (Each in its own python file in creatures/)
# ==============================================================================
from creatures.spider import (
    Insect,
    BabySpider,
)

from creatures.butterfly import (
    ButterflyLifeCycle,
    BUTTERFLY_THEMES,
)

from creatures.chameleon import (
    ChameleonCreature,
)

from creatures.fireflies import (
    FireflySwarm,
)

from creatures.galaxy import (
    CelestialDragon,
)

from creatures.jellyfish import (
    CosmicJellyfish,
    JELLYFISH_PALETTES,
)

from creatures.bird import (
    RoyalCrestedBird,
    BIRD_PLUMAGE_THEMES,
)

def clean_os_title(text):
    """Strips surrogate emoji characters for native OS titlebars to prevent Windows GDI font glitches."""
    if not text:
        return "Desktop Floating"
    import re
    cleaned = re.sub(r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\ufe0f]', '', str(text)).strip()
    cleaned = re.sub(r'^\s*[-—:]\s*', '', cleaned)
    return cleaned or "Desktop Floating"


class DesktopSpiderApp:
    def __init__(self):
        PlatformHelper.set_app_user_model_id("antigravity.desktoppet.spider.ecosystem.v2")
        self.root = tk.Tk()
        self.root.title("Desktop Pet Ecosystem")
        ico_path = os.path.join(ROOT_DIR, "assets", "app_icon.ico")
        png_path = os.path.join(ROOT_DIR, "assets", "app_icon.png")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass
        if os.path.exists(png_path):
            try:
                from PIL import ImageTk
                self.icon_photo = ImageTk.PhotoImage(file=png_path)
                self.root.iconphoto(True, self.icon_photo)
            except Exception:
                pass

        # Virtual Screen for Dual/Multi-Monitors (Cross-Platform)
        self.screen_x, self.screen_y, self.screen_w, self.screen_h = PlatformHelper.get_screen_bounds(self.root)
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+{self.screen_x}+{self.screen_y}")

        self.TRANSPARENT_COLOR = "#010101"
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        PlatformHelper.setup_window_transparency(self.root, self.canvas, self.TRANSPARENT_COLOR)
        self.root.update()
        self.hwnd = PlatformHelper.make_click_through(self.root)

        # Cross-platform hotkey bindings for Linux & macOS
        if not IS_WINDOWS:
            def _on_kp(e):
                combo = []
                if e.state & 0x0001: combo.append("SHIFT")
                if e.state & 0x0004: combo.append("CTRL")
                if e.state & 0x0008: combo.append("ALT")
                k = e.keysym.upper()
                if k not in ["SHIFT_L", "SHIFT_R", "CONTROL_L", "CONTROL_R", "ALT_L", "ALT_R"]:
                    combo.append(k)
                    PlatformHelper._active_keys.add("+".join(combo))
                    PlatformHelper._last_user_time = time.time()
            def _on_kr(e):
                PlatformHelper._active_keys.clear()
            self.root.bind("<KeyPress>", _on_kp)
            self.root.bind("<KeyRelease>", _on_kr)

        # Load config
        self.config = load_config()
        self.species = self.config.get("CREATURE_SPECIES", "spider")
        self.SPOKE_DURATION = float(self.config.get("SPOKE_DURATION", 4.5))
        self.RING_WEAVE_DURATION = float(self.config.get("RING_WEAVE_DURATION", 10.0))
        self.butterfly = ButterflyLifeCycle(self)
        self.chameleon = ChameleonCreature(self)
        self.fireflies = FireflySwarm(self)
        self.dragon = CelestialDragon(self)
        self.jellyfish = CosmicJellyfish(self)
        self.bird = RoyalCrestedBird(self)
        self.updater = GitHubAutoUpdater(self)
        if self.config.get("AUTO_CHECK_UPDATES", True):
            self.updater.check_for_updates_async(silent=True)
        self.i18n = I18n(self.config.get("LANGUAGE", "bn"))
        self.hotkeys = dict(self.config.get("HOTKEYS", {}))
        self._pressed_hotkeys = set()
        self._new_hotkey_presses = set()
        self.last_keyboard_time = time.time()
        self.last_key_press_time = 0.0

        self.WEB_RADIUS = int(self.config.get("WEB_RADIUS", 130))
        self.PANIC_RADIUS = float(self.config.get("PANIC_RADIUS", 220))
        self.REWEAVE_INTERVAL = float(self.config.get("REWEAVE_INTERVAL_SECONDS", 120))
        self.EATING_DURATION = float(self.config.get("EATING_DURATION_SECONDS", 5))
        self.BUG_INTERVAL = float(self.config.get("BUG_SPAWN_INTERVAL", 20))
        self.SOUND_ENABLED = _as_bool(self.config.get("SOUND_ENABLED", False), False)
        self.REMINDER_INTERVAL = float(self.config.get("REMINDER_INTERVAL_MINUTES", 30)) * 60.0
        self.BUNGEE_AUTO_ENABLED = bool(self.config.get("BUNGEE_AUTO_ENABLED", True))
        self.BUNGEE_DROP_DISTANCE = float(self.config.get("BUNGEE_DROP_DISTANCE", 480))
        self.WEAVE_DURATION = float(self.config.get("WEAVE_DURATION", 6.5))
        self.web_thickness = float(self.config.get("WEB_THREAD_THICKNESS", 2.2))

        # Ensure coordinates are safely positioned on the visible primary display
        primary_w = self.root.winfo_screenwidth() or 1440
        primary_h = self.root.winfo_screenheight() or 900

        raw_x = self.config.get("HOME_X", "AUTO")
        raw_y = self.config.get("HOME_Y", "AUTO")
        if raw_x == "AUTO" or raw_y == "AUTO":
            self.HOME_X = float(primary_w * 0.55)
            self.HOME_Y = float(primary_h * 0.28)
        else:
            try:
                self.HOME_X = float(raw_x)
                self.HOME_Y = float(raw_y)
            except Exception:
                self.HOME_X = float(primary_w * 0.55)
                self.HOME_Y = float(primary_h * 0.28)

        # Multi-monitor virtual desktop bounds check (safely supports secondary & multi displays)
        vx, vy, vw, vh = 0, 0, primary_w, primary_h
        if IS_WINDOWS:
            try:
                import ctypes
                u32 = ctypes.windll.user32
                vx = u32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
                vy = u32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
                vw = u32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
                vh = u32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
            except Exception:
                pass
        vw = max(vw, primary_w)
        vh = max(vh, primary_h)

        # Only fallback if completely outside any connected monitor
        if self.HOME_X > (vx + vw + 100) or self.HOME_X < (vx - 100):
            self.HOME_X = float(primary_w * 0.55)
        if self.HOME_Y > (vy + vh + 100) or self.HOME_Y < (vy - 100):
            self.HOME_Y = float(primary_h * 0.28)

        raw_top_x = self.config.get("ENTRY_TOP_X", "AUTO")
        if raw_top_x == "AUTO":
            self.ENTRY_TOP_X = self.HOME_X
        else:
            try:
                self.ENTRY_TOP_X = float(raw_top_x)
                if self.ENTRY_TOP_X > (vx + vw + 100) or self.ENTRY_TOP_X < (vx - 100):
                    self.ENTRY_TOP_X = self.HOME_X
            except Exception:
                self.ENTRY_TOP_X = self.HOME_X

        raw_silk_len = self.config.get("ENTRANCE_SILK_LENGTH", "AUTO")
        if raw_silk_len == "AUTO":
            self.ENTRANCE_SILK_LENGTH = None
        else:
            self.ENTRANCE_SILK_LENGTH = float(raw_silk_len)

        self.theme_idx = int(self.config.get("THEME_INDEX", 0)) % len(THEMES)
        self.theme = THEMES[self.theme_idx]

        # Spider anatomical model & sizing
        self.model_idx = int(self.config.get("SPIDER_MODEL_INDEX", 0)) % len(SPIDER_MODELS)
        self.spider_scale = float(self.config.get("SPIDER_SIZE_SCALE", 1.0))
        self.spider_speed = float(self.config.get("SPIDER_SPEED", 6.0))
        self.SHOVE_FORCE = float(self.config.get("SHOVE_FORCE", 35.0))
        self.settings_window = None
        self.model_var = None
        self.theme_var = None

        # Web geometry
        self.num_spokes = 12
        self.spoke_angles = [i * (2 * math.pi / self.num_spokes) for i in range(self.num_spokes)]
        self.ring_ratios = [0.24, 0.43, 0.62, 0.81, 1.00]
        self.recompute_web_geometry()

        # Web elastic vibration
        self.web_vibration = 0.0
        self.vibration_phase = 0.0

        # Spider physical state (starts at custom ceiling entry X above monitor)
        self.x = self.get_entrance_top_x()
        self.y = float(self.screen_y - 45.0) # Start above monitor edge
        self.vx = 0.0
        self.vy = 0.0
        self.angle = math.pi # Facing downwards as it descends on silk
        self.target_angle = math.pi
        self.walk_phase = 0.0

        # State machine:
        # 'ENTRANCE', 'WEAVING', 'RESTING', 'FLEEING', 'RETURNING', 'HUNTING', 'EATING', 'BUNGEE', 'CURIOUS'
        self.state = 'ENTRANCE'

        self.weave_phase = 'SPOKE_OUT'
        self.current_spoke_idx = 0
        self.current_ring_idx = 0
        self.current_segment_idx = 0
        self.sub_step = 0
        self.web_built = False
        self.web_complete_time = 0.0

        self.waypoint_timer = time.time()
        self.last_waypoint_tracker = (-1, -1, -1)

        # Insect
        self.insect = None
        self.last_bug_spawn_time = time.time()
        self.eating_start_time = 0.0

        # Egg Sac lifecycle
        self.egg_state = 'NORMAL'
        self.egg_birth_time = time.time()
        self.babies = []

        # Bungee jump state
        self.bungee_start_time = 0.0
        self.bungee_drop_target = 0.0
        self.last_bungee_time = time.time()

        # Entrance descent phase ('DROP' -> drops snappy to monitor center; 'WIGGLE' -> wiggles legs; 'REEL_SILK' -> reels thread into tail; 'DASH' -> dashes to nest)
        self.entrance_phase = 'DROP'
        self.entrance_wiggle_start = 0.0
        self.entrance_drop_speed = 8.0
        self.silk_top_y = float(self.screen_y)

        # Curiosity & Angry Shove Mode state (2-minute cooldown between shoves)
        self.curious_phase = 'APPROACH' # 'APPROACH', 'ORBIT', 'SHIVER', 'SHOVE_1', 'SHOVE_2'
        self.curious_phase_start = 0.0
        self.curious_orbit_angle = 0.0
        self.screen_shake_time = 0.0
        self.screen_shake_intensity = 0.0
        self.is_screen_shaking = False
        self.SHOVE_COOLDOWN = float(self.config.get("SHOVE_INTERVAL_SECONDS", 30.0))
        self.last_shove_time = time.time() - self.SHOVE_COOLDOWN + 12.0
        if not hasattr(self, "hwnd"):
            self.hwnd = None
        self.impact_x = 0.0
        self.impact_y = 0.0
        self.rumble_active = False

        # Auto-clean tray on exit
        atexit.register(self.quit_app)

        # Health Reminder Banner
        self.last_reminder_time = time.time()
        self.reminder_active = False
        self.reminder_end_time = 0.0

        # Onboarding / What's New Hint Banner
        self.onboarding_active = False
        self.onboarding_type = None
        self.onboarding_end_time = 0.0
        first_run_done = self.config.get("FIRST_RUN_SHOWN", False)
        last_seen_ver = self.config.get("LAST_SEEN_VERSION", "0.0.0")

        if not first_run_done:
            self.onboarding_active = True
            self.onboarding_type = "FIRST_RUN"
            self.onboarding_end_time = time.time() + 14.0
            self.config["FIRST_RUN_SHOWN"] = True
            self.config["LAST_SEEN_VERSION"] = APP_VERSION
            save_config_value("FIRST_RUN_SHOWN", True)
            save_config_value("LAST_SEEN_VERSION", APP_VERSION)
        elif str(last_seen_ver) != str(APP_VERSION):
            self.onboarding_active = True
            self.onboarding_type = "UPDATE"
            self.onboarding_end_time = time.time() + 12.0
            self.config["LAST_SEEN_VERSION"] = APP_VERSION
            save_config_value("LAST_SEEN_VERSION", APP_VERSION)

        # Interactive Drag / Move Mode
        self.move_mode = False
        self.last_tilde_pressed = False

        # Mouse tracking
        self.last_mouse_x = -9999
        self.last_mouse_y = -9999
        self.last_mouse_move_time = time.time()
        self.last_panic_time = 0.0

        # Setup System Tray Icon
        self.tray_icon = None
        self.setup_tray_icon()

        # Automatically open the Desktop Control Panel on launch
        self.open_settings_panel = self.open_settings_window
        self.root.after(350, self.open_settings_window)

        self.update_loop()

    def summon_pet_to_center(self):
        """Immediately teleports/summons whatever pet is active straight to the center of the primary screen."""
        primary_w = self.root.winfo_screenwidth() or 1440
        primary_h = self.root.winfo_screenheight() or 900
        cx = float(primary_w // 2)
        cy = float(primary_h // 2 - 50)

        self.HOME_X = cx
        self.HOME_Y = cy
        self.ENTRY_TOP_X = cx
        self.x = cx
        self.y = cy
        self.angle = 0.0

        if hasattr(self, 'butterfly') and self.butterfly:
            try:
                self.butterfly.x = cx
                self.butterfly.y = cy
                self.butterfly.state = "FLYING"
            except Exception:
                pass

        if hasattr(self, 'chameleon') and self.chameleon:
            try:
                self.chameleon.x = cx
                self.chameleon.y = cy
                self.chameleon.state = "RESTING"
            except Exception:
                pass

        if hasattr(self, 'dragon') and self.dragon:
            try:
                self.dragon.x = cx
                self.dragon.y = cy
            except Exception:
                pass

        if hasattr(self, 'jellyfish') and self.jellyfish:
            try:
                self.jellyfish.x = cx
                self.jellyfish.y = cy
            except Exception:
                pass

        if hasattr(self, 'bird') and self.bird:
            try:
                self.bird.x = cx
                self.bird.y = cy
                self.bird.state = "PERCHED"
            except Exception:
                pass

        self.recompute_web_geometry()
        if self.species == 'spider':
            self.rebuild_web()

        save_config_value("HOME_X", int(self.HOME_X))
        save_config_value("HOME_Y", int(self.HOME_Y))
        save_config_value("ENTRY_TOP_X", int(self.ENTRY_TOP_X))
        print(f"[✓] Summoned pet to primary screen center ({int(cx)}, {int(cy)})")

    def rebuild_web(self, animate=True):
        """Cleanly destroys old web, recomputes geometry, and weaves or instantly redraws web."""
        self.destroy_web()
        self.recompute_web_geometry()
        self.x = self.HOME_X
        self.y = self.HOME_Y
        if animate:
            self.state = 'WEAVING'
            self.weave_start_time = time.time()
            self.web_built = False
        else:
            self.redraw_full_web()
            self.state = 'RESTING'

    def setup_tray_icon(self):
        """Creates an authentic Windows System Tray notification icon."""
        try:
            import pystray
            from PIL import Image, ImageDraw

            def create_icon_image():
                icon_png_path = os.path.join(ROOT_DIR, "assets", "app_icon.png")
                if os.path.exists(icon_png_path):
                    try:
                        return Image.open(icon_png_path).resize((64, 64), Image.Resampling.LANCZOS)
                    except Exception:
                        pass
                # 100% Transparent background fallback
                img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(img)

                TEAL = (0, 245, 212, 255)
                CYAN = (0, 187, 249, 255)
                WHITE = (255, 255, 255, 255)
                PINK = (255, 0, 85, 255)
                DARK = (15, 23, 42, 220)

                # 8 Jointed Legs reaching outward in Google Flow style
                leg_coords = [
                    [(28, 26), (18, 14), (10, 18)],
                    [(36, 26), (46, 14), (54, 18)],
                    [(27, 29), (12, 24), (6, 32)],
                    [(37, 29), (52, 24), (58, 32)],
                    [(27, 33), (12, 38), (8, 48)],
                    [(37, 33), (52, 38), (56, 48)],
                    [(29, 37), (18, 50), (14, 58)],
                    [(35, 37), (46, 50), (50, 58)],
                ]

                for pts in leg_coords:
                    draw.line(pts, fill=DARK, width=4)
                    draw.line(pts, fill=TEAL, width=2)
                    draw.ellipse([pts[1][0]-1.5, pts[1][1]-1.5, pts[1][0]+1.5, pts[1][1]+1.5], fill=WHITE)

                # Abdomen
                draw.ellipse([24, 31, 40, 51], fill=DARK)
                draw.ellipse([25, 32, 39, 50], fill=TEAL, outline=WHITE, width=1)
                draw.line([(32, 34), (32, 48)], fill=WHITE, width=2)

                # Thorax
                draw.ellipse([26, 21, 38, 33], fill=DARK)
                draw.ellipse([27, 22, 37, 32], fill=CYAN, outline=WHITE, width=1)

                # Pedipalps
                draw.line([(29, 22), (26, 17)], fill=WHITE, width=2)
                draw.line([(35, 22), (38, 17)], fill=WHITE, width=2)

                # Glowing Eyes
                draw.ellipse([28, 24, 31, 27], fill=PINK)
                draw.ellipse([33, 24, 36, 27], fill=PINK)
                draw.point([(29, 25), (34, 25)], fill=WHITE)

                return img

            def build_menu():
                hk = self.hotkeys
                species_badge = self.i18n.t(f"species_{self.species}", self.species.capitalize())
                model_name = self.get_model_display_name(self.model_idx)
                theme_name = self.get_theme_display_name(self.theme_idx)
                sound_icon = "🔊" if self.SOUND_ENABLED else "🔇"
                sound_status = f"[{self.i18n.t('status_on', 'ON')}]" if self.SOUND_ENABLED else f"[{self.i18n.t('status_off', 'OFF')}]"
                move_icon = "📍" if self.move_mode else "🔒"
                move_status = f"[{self.i18n.t('status_moving', 'DRAGGING')}]" if self.move_mode else f"[{self.i18n.t('status_locked', 'LOCKED')}]"
                items = [
                    pystray.MenuItem(f"🐾 {self.i18n.t('tray_switch_species', 'Switch Creature')}: {species_badge} [{hk.get('SPECIES', 'Shift+M')}]", lambda: self.root.after(0, self.switch_species)),
                    pystray.MenuItem(f"{self.i18n.t('tray_settings', 'Live Settings & Customizer')} [{hk.get('SETTINGS', 'Shift+P')}]", lambda: self.root.after(0, self.open_settings_window), default=True),
                ]
                if self.species == "butterfly":
                    th = self.butterfly.theme
                    th_raw = th.get('bengali') if self.i18n.lang == "bn" else th.get('name')
                    th_name = f"{th.get('icon','🦋')} {th_raw}"
                    items.extend([
                        pystray.Menu.SEPARATOR,
                        pystray.MenuItem(f"🎨 {self.i18n.t('tray_wing_theme', 'Wing Theme')}: {th_name} [{hk.get('THEME', 'Shift+T')}]", lambda: self.root.after(0, self.butterfly.cycle_theme)),
                        pystray.MenuItem(f"🥚 {self.i18n.t('tray_relocate_cocoon', 'Relocate Cocoon / Egg')} [{hk.get('MOVE', 'Shift+`')}]", lambda: self.root.after(0, self.butterfly.set_cocoon_spot_from_cursor)),
                        pystray.MenuItem(f"⏩ {self.i18n.t('tray_advance_stage', 'Advance Stage')} [{hk.get('ADVANCE', 'Shift+E')}]", lambda: self.root.after(0, self.butterfly.advance_stage)),
                        pystray.MenuItem(f"🔄 {self.i18n.t('tray_restart_lifecycle', 'Restart Life Cycle')} [{hk.get('RESTART', 'Shift+C')}]", lambda: self.root.after(0, self.butterfly.restart_lifecycle)),
                        pystray.MenuItem(f"✨ {self.i18n.t('tray_fairy_dust', 'Fairy Dust Burst')} [{hk.get('BUG', 'Shift+F')}]", lambda: self.root.after(0, self.butterfly.trigger_flight_sparkle)),
                    ])
                elif self.species == "bird":
                    th = self.bird.theme
                    items.extend([
                        pystray.Menu.SEPARATOR,
                        pystray.MenuItem(f"🪶 {self.i18n.t('tray_bird_theme', 'Plumage Theme')}: {th.get('name','Theme')} [{hk.get('THEME', 'Shift+T')}]", lambda: self.root.after(0, self.bird.cycle_theme)),
                        pystray.MenuItem(f"🪺 {self.i18n.t('tray_bird_nest', 'Relocate Nest')} [{hk.get('MOVE', 'Shift+`')}]", lambda: self.root.after(0, self.bird.set_nest_spot_from_cursor)),
                        pystray.MenuItem(f"🎵 {self.i18n.t('tray_bird_song', 'Bird Call & Flight')} [{hk.get('BUG', 'Shift+F')}]", lambda: self.root.after(0, self.bird.trigger_song_flight)),
                        pystray.MenuItem(f"🏠 {self.i18n.t('tray_bird_return', 'Return to Nest')} [{hk.get('BUNGEE', 'Shift+B')}]", lambda: self.root.after(0, self.bird.return_to_nest)),
                    ])
                elif self.species == "chameleon":
                    th = self.chameleon.theme
                    th_raw = th.get('bengali') if self.i18n.lang == "bn" else th.get('name')
                    th_name = f"🦎 {th_raw}"
                    items.extend([
                        pystray.Menu.SEPARATOR,
                        pystray.MenuItem(f"🎨 {self.i18n.t('tray_gecko_theme', 'Camouflage Theme')}: {th_name} [{hk.get('THEME', 'Shift+T')}]", lambda: self.root.after(0, self.chameleon.cycle_color)),
                        pystray.MenuItem(f"📍 {self.i18n.t('tray_relocate_gecko', 'Relocate Gecko')} [{hk.get('MOVE', 'Shift+`')}]", lambda: self.root.after(0, self.chameleon.set_spot_from_cursor)),
                        pystray.MenuItem(f"👅 {self.i18n.t('tray_gecko_hunt', 'Ballistic Tongue Zap')} [{hk.get('BUG', 'Shift+F')}]", lambda: self.root.after(0, self.chameleon.trigger_hunt)),
                    ])
                else: # Default spider actions
                    items.extend([
                        pystray.MenuItem(f"🕷 {self.i18n.t('tray_switch_model', 'Switch Model')}: {model_name} [{hk.get('MODEL', 'Shift+W')}]", lambda: self.root.after(0, self.cycle_spider_model)),
                        pystray.Menu.SEPARATOR,
                        pystray.MenuItem(f"{self.i18n.t('tray_restart', 'Restart / Rappel Down')} [{hk.get('RESTART', 'Shift+C')}]", lambda: self.root.after(0, self.start_entrance)),
                        pystray.MenuItem(f"{self.i18n.t('tray_set_entry', 'Set Ceiling Entry Point')} [{hk.get('ENTRY', 'Shift+Q')}]", lambda: self.root.after(0, self.set_entry_point_from_cursor)),
                        pystray.MenuItem(f"🎨 {self.i18n.t('tray_switch_theme', 'Switch Theme')}: {theme_name} [{hk.get('THEME', 'Shift+T')}]", lambda: self.root.after(0, self.switch_theme)),
                        pystray.MenuItem(f"{self.i18n.t('tray_spawn_insect', 'Spawn Insect')} [{hk.get('BUG', 'Shift+F')}]", lambda: self.root.after(0, self.spawn_insect)),
                        pystray.MenuItem(f"{self.i18n.t('tray_bungee', 'Bungee Jump')} [{hk.get('BUNGEE', 'Shift+B')}]", lambda: self.root.after(0, self.start_bungee_jump)),
                        pystray.MenuItem(f"{self.i18n.t('tray_hatch', 'Hatch Babies')} [{hk.get('BABIES', 'Shift+H')}]", lambda: self.root.after(0, self.hatch_eggs)),
                    ])

                items.extend([
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(f"{self.i18n.t('tray_health', 'Health Break')} [{hk.get('REMINDER', 'Shift+R')}]", lambda: self.root.after(0, self.show_health_reminder)),
                    pystray.MenuItem(f"{sound_icon} {self.i18n.t('tray_sound', 'Sound Toggle')}: {sound_status} [{hk.get('SOUND', 'Shift+S')}]", lambda: self.root.after(0, self.toggle_sound)),
                    pystray.MenuItem(f"{move_icon} {self.i18n.t('tray_move_web', 'Move Web')}: {move_status} [{hk.get('MOVE', 'Shift+`')}]", lambda: self.root.after(0, self.toggle_move_mode)),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(f"🔄 {self.i18n.t('tray_check_update', 'Check for Updates')}", lambda: self.root.after(0, lambda: self.updater.check_for_updates_async(silent=False))),
                    pystray.MenuItem(f"{self.i18n.t('tray_exit', 'Exit Desktop Spider')} [Shift+ESC]", lambda: self.root.after(0, self.quit_app))
                ])
                return pystray.Menu(*items)
            self.build_menu = build_menu
            menu = build_menu()
            self.tray_icon = pystray.Icon('DesktopSpider', create_icon_image(), 'Desktop Spider Overlay', menu)
            self.tray_icon.run_detached()
            
            # Hook right click and left click to show sleek black context menu
            orig_notify = getattr(self.tray_icon, '_on_notify', None)
            if orig_notify:
                def custom_notify(wparam, lparam):
                    if lparam in (0x0205, 0x007B): # WM_RBUTTONUP, WM_CONTEXTMENU
                        self.root.after(0, self.show_dark_popup_menu)
                        return
                    elif lparam == 0x0202: # WM_LBUTTONUP
                        self.root.after(0, self.open_settings_window)
                        return
                    orig_notify(wparam, lparam)
                self.tray_icon._on_notify = custom_notify
            print("System Tray Icon initialized successfully in Windows Taskbar!")
        except Exception as e:
            print("System Tray setup warning:", e)
            self.tray_icon = None

    def is_autostart_enabled(self):
        return PlatformHelper.is_autostart_enabled()

    def set_autostart(self, enable=True):
        PlatformHelper.set_autostart(enable, os.path.abspath(__file__))
        save_config_value("AUTO_START", enable)

    def set_spoke_duration(self, dur_val, commit=True):
        self.SPOKE_DURATION = max(1.0, min(20.0, float(dur_val)))
        if commit:
            save_config_value("SPOKE_DURATION", f"{self.SPOKE_DURATION:.1f}")

    def set_ring_weave_duration(self, dur_val, commit=True):
        self.RING_WEAVE_DURATION = max(2.0, min(40.0, float(dur_val)))
        if commit:
            save_config_value("RING_WEAVE_DURATION", f"{self.RING_WEAVE_DURATION:.1f}")

    def switch_species(self, new_species=None):
        """Cycles through or selects one of the 6 desktop creatures:
        Spider, Butterfly, Chameleon, Fireflies, Dragon, Jellyfish."""
        species_list = ["spider", "butterfly", "chameleon", "fireflies", "dragon", "jellyfish", "bird"]
        if new_species is None:
            idx = species_list.index(self.species) if self.species in species_list else 0
            self.species = species_list[(idx + 1) % len(species_list)]
        else:
            self.species = new_species

        save_config_value("CREATURE_SPECIES", self.species)

        # Clear all creature canvas layers
        self.canvas.delete("web")
        self.canvas.delete("spider")
        self.canvas.delete("active_thread")
        self.canvas.delete("dewdrop")
        self.canvas.delete("hub")
        self.canvas.delete("baby")
        self.canvas.delete("insect")
        self.canvas.delete("entrance_silk")
        self.canvas.delete("bungee_silk")
        self.canvas.delete("butterfly_creature")
        self.canvas.delete("chameleon_creature")
        self.canvas.delete("firefly_creature")
        self.canvas.delete("dragon_creature")
        self.canvas.delete("jellyfish_creature")
        self.canvas.delete("bird_creature")

        if self.species == "spider":
            self.start_entrance()
            if self.SOUND_ENABLED: play_audio(800, 40, 500, 50)
        elif self.species == "butterfly":
            self.butterfly.set_stage("FLYING")
        elif self.species == "chameleon":
            if self.SOUND_ENABLED: play_audio(550, 40, 750, 50)
        elif self.species == "fireflies":
            self.fireflies.trigger_flash()
        elif self.species == "dragon":
            self.dragon.trigger_breath()
        elif self.species == "jellyfish":
            self.jellyfish.trigger_ripple()
        elif self.species == "bird":
            self.bird.trigger_song_flight()
            if self.SOUND_ENABLED: play_audio(900, 40, 1300, 60)

        print(f"[*] Active Desktop Creature: {self.species.upper()}")

    def toggle_sound(self):
        self.SOUND_ENABLED = not self.SOUND_ENABLED
        save_config_value("SOUND_ENABLED", self.SOUND_ENABLED)
        print(f"Sound Enabled: {self.SOUND_ENABLED}")
        if self.SOUND_ENABLED:
            play_audio(1200, 40)
        if hasattr(self, 'tray_icon') and self.tray_icon and hasattr(self, 'build_menu'):
            try:
                self.tray_icon.menu = self.build_menu()
            except Exception:
                pass

    def is_hotkey_just_pressed(self, combo):
        """Return true only on the first frame of a hotkey press."""
        return str(combo).strip().upper() in self._new_hotkey_presses

    def poll_hotkey_edges(self):
        """Track all configured chords together so releases are noticed in every species."""
        combos = {str(combo).strip().upper() for combo in self.hotkeys.values()}
        combos.update(("SHIFT+ESC", "SHIFT+E"))
        currently_down = {combo for combo in combos if is_hotkey_down(combo)}
        self._new_hotkey_presses = currently_down - self._pressed_hotkeys
        self._pressed_hotkeys = currently_down

    def toggle_move_mode(self):
        self.move_mode = not self.move_mode
        if self.move_mode:
            print("Move Mode ON: Move mouse to reposition web!")
        else:
            save_config_value("HOME_X", int(self.HOME_X))
            save_config_value("HOME_Y", int(self.HOME_Y))
            print(f"Web locked at ({int(self.HOME_X)}, {int(self.HOME_Y)})")
        if hasattr(self, 'tray_icon') and self.tray_icon and hasattr(self, 'build_menu'):
            try:
                self.tray_icon.menu = self.build_menu()
            except Exception:
                pass

    def quit_app(self):
        try:
            cfg = load_config()
            cfg["HOTKEYS"] = self.hotkeys
            cfg["LANGUAGE"] = self.i18n.lang
            cfg["CREATURE_SPECIES"] = self.species
            cfg["THEME_INDEX"] = self.theme_idx
            cfg["SPIDER_MODEL_INDEX"] = self.model_idx
            cfg["SPIDER_SIZE_SCALE"] = self.spider_scale
            cfg["SPIDER_SPEED"] = self.spider_speed
            cfg["SOUND_ENABLED"] = self.SOUND_ENABLED
            cfg["HOME_X"] = int(self.HOME_X)
            cfg["HOME_Y"] = int(self.HOME_Y)
            cfg["ENTRY_TOP_X"] = int(self.ENTRY_TOP_X)
            if hasattr(self, 'chameleon'):
                cfg["GECKO_COLOR_INDEX"] = getattr(self.chameleon, 'color_idx', 0)
                cfg["GECKO_SCALE"] = getattr(self.chameleon, 'scale', 1.15)
                cfg["GECKO_X"] = getattr(self.chameleon, 'x', None)
                cfg["GECKO_Y"] = getattr(self.chameleon, 'y', None)
            if hasattr(self, 'butterfly'):
                cfg["BUTTERFLY_THEME_INDEX"] = getattr(self.butterfly, 'theme_idx', 0)
                cfg["BUTTERFLY_SCALE"] = getattr(self.butterfly, 'scale', 1.15)
                cfg["BUTTERFLY_FLIGHT_SPEED"] = getattr(self.butterfly, 'flight_speed', 1.0)
                cfg["BUTTERFLY_CRAWL_SPEED"] = getattr(self.butterfly, 'crawl_speed', 1.8)
                cfg["COCOON_X"] = getattr(self.butterfly, 'cocoon_x', None)
                cfg["COCOON_Y"] = getattr(self.butterfly, 'cocoon_y', None)
            if hasattr(self, 'bird'):
                cfg["BIRD_THEME_INDEX"] = getattr(self.bird, 'theme_idx', 1)
                cfg["BIRD_NEST_X"] = getattr(self.bird, 'nest_x', None)
                cfg["BIRD_NEST_Y"] = getattr(self.bird, 'nest_y', None)
            save_full_settings(cfg)
        except Exception:
            pass
        if hasattr(self, 'tray_icon') and self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass
        os._exit(0)

    def make_click_through(self):
        self.hwnd = PlatformHelper.make_click_through(self.root)
        self.ensure_topmost()

    def ensure_topmost(self):
        """Forces the overlay window to stay permanently above all new tabs, apps, and windows."""
        PlatformHelper.ensure_topmost(self.root, getattr(self, 'hwnd', None))

    def get_system_idle_seconds(self):
        """Returns seconds since last user interaction on either KEYBOARD or MOUSE."""
        return PlatformHelper.get_system_idle_seconds()

    def get_mouse_pos(self):
        return PlatformHelper.get_mouse_pos(self.root)

    def trigger_vibration(self, intensity=1.0):
        """Triggers elastic spring vibration on the spider web."""
        self.web_vibration = min(2.5, self.web_vibration + intensity)

    def trigger_screen_shake(self, intensity=22.0, impact_x=None, impact_y=None):
        """Triggers kinetic impact rumble without annoying full-screen scanlines."""
        self.screen_shake_time = time.time()
        self.screen_shake_intensity = intensity
        self.impact_x = float(impact_x if impact_x is not None else self.x)
        self.impact_y = float(impact_y if impact_y is not None else self.y)
        self.rumble_active = True

    def update_screen_shake(self, now):
        """Renders subtle impact pulse, cursor buzz, and hardware rumble without full-screen lines."""
        self.canvas.delete("screen_shake_fx")
        elapsed = now - self.screen_shake_time
        duration = 0.35
        if elapsed < duration:
            factor = (1.0 - (elapsed / duration))
            # 1. Kinetic Cursor Rumble (tactile micro-buzz right at new position)
            if getattr(self, 'rumble_active', False) and hasattr(self, 'impact_x'):
                jit_cx = int((random.random() - 0.5) * 5.0 * factor)
                jit_cy = int((random.random() - 0.5) * 5.0 * factor)
                PlatformHelper.set_cursor_pos(int(self.impact_x + jit_cx), int(self.impact_y + jit_cy))

            # 2. Compact impact spark ring right at the headbutt point (radius max 35px, NOT across the whole screen)
            ix, iy = getattr(self, 'impact_x', self.x), getattr(self, 'impact_y', self.y)
            r = elapsed * 120.0
            if r > 3 and r < 40:
                self.canvas.create_oval(ix - r, iy - r, ix + r, iy + r,
                                        outline=self.theme['egg_sac_glow'], width=max(1.0, 1.8 * factor), tags="screen_shake_fx")

            # 3. Hardware Window Shake via SetWindowPos (HWND_TOPMOST preserved)
            jit_x = int((random.random() - 0.5) * self.screen_shake_intensity * 1.8 * factor)
            jit_y = int((random.random() - 0.5) * self.screen_shake_intensity * 1.5 * factor)
            if IS_WINDOWS and hasattr(self, 'hwnd') and self.hwnd:
                try:
                    HWND_TOPMOST = -1
                    ctypes.windll.user32.SetWindowPos(
                        self.hwnd, HWND_TOPMOST,
                        self.screen_x + jit_x, self.screen_y + jit_y,
                        0, 0, 0x0001 | 0x0010
                    )
                except Exception:
                    pass
                self.is_screen_shaking = True
        elif getattr(self, 'is_screen_shaking', False):
            # Cleanly restore exact monitor origin with HWND_TOPMOST
            if IS_WINDOWS and hasattr(self, 'hwnd') and self.hwnd:
                try:
                    HWND_TOPMOST = -1
                    ctypes.windll.user32.SetWindowPos(
                        self.hwnd, HWND_TOPMOST,
                        self.screen_x, self.screen_y,
                        0, 0, 0x0001 | 0x0010
                    )
                except Exception:
                    pass
            if hasattr(self, 'impact_x') and getattr(self, 'rumble_active', False):
                PlatformHelper.set_cursor_pos(int(self.impact_x), int(self.impact_y))
            self.is_screen_shaking = False
            self.rumble_active = False

    def recompute_web_geometry(self):
        self.spoke_points = []
        for a in self.spoke_angles:
            px = self.HOME_X + math.cos(a) * self.WEB_RADIUS
            py = self.HOME_Y + math.sin(a) * self.WEB_RADIUS
            self.spoke_points.append((px, py))

    def redraw_full_web(self):
        """Immediately draws the full finished, perfectly connected web with rich thread thickness."""
        self.canvas.delete("web")
        self.canvas.delete("active_thread")
        self.canvas.delete("hub")
        self.canvas.delete("dewdrop")

        spoke_w = max(1.6, self.web_thickness * 1.15)
        ring_w = max(1.2, self.web_thickness * 0.95)

        # 1. Guaranteed radial spoke lines from Center Hub to Outer Edge
        self.recompute_web_geometry()
        for px, py in self.spoke_points:
            self.canvas.create_line(
                self.HOME_X, self.HOME_Y, px, py,
                fill=self.theme['web'], width=spoke_w, tags="web"
            )

        # 2. Concentric Curved Spiral Rings (All rings, including outer perimeter, droop with graceful catenary curve)
        for r_idx, r_ratio in enumerate(self.ring_ratios):
            R = self.WEB_RADIUS * r_ratio
            droop = 0.88
            for i in range(self.num_spokes):
                i_next = (i + 1) % self.num_spokes
                a1 = self.spoke_angles[i]
                a2 = self.spoke_angles[i_next]
                diff = a2 - a1
                if diff < 0:
                    diff += 2 * math.pi
                a_mid = a1 + diff / 2
                p1 = (self.HOME_X + math.cos(a1) * R, self.HOME_Y + math.sin(a1) * R)
                p_mid = (self.HOME_X + math.cos(a_mid) * (R * droop), self.HOME_Y + math.sin(a_mid) * (R * droop))
                p2 = (self.HOME_X + math.cos(a2) * R, self.HOME_Y + math.sin(a2) * R)
                self.canvas.create_line(
                    p1[0], p1[1], p_mid[0], p_mid[1], p2[0], p2[1],
                    smooth=True, fill=self.theme['web'], width=ring_w, tags="web"
                )

        # 3. Center Hub (Always drawn solidly when web is built)
        hub_r = max(5, int(5 * (self.web_thickness / 2.0)))
        self.canvas.create_oval(
            self.HOME_X - hub_r, self.HOME_Y - hub_r, self.HOME_X + hub_r, self.HOME_Y + hub_r,
            fill=self.theme['hub'], outline="#ffffff", width=max(1.2, self.web_thickness * 0.7), tags="hub"
        )
        self.web_built = True
        self.web_complete_time = time.time()

    def draw_web(self):
        self.redraw_full_web()

    def get_model_display_name(self, idx):
        m = SPIDER_MODELS[idx % len(SPIDER_MODELS)]
        return self.i18n.t(m.get("name_key", f"model_{idx}"), m.get("id", f"Model {idx}"))

    def get_theme_display_name(self, idx):
        t = THEMES[idx % len(THEMES)]
        return self.i18n.t(t.get("name_key", f"theme_{idx}"), f"Theme {idx}")

    def set_spider_model(self, idx):
        self.model_idx = int(idx) % len(SPIDER_MODELS)
        save_config_value("SPIDER_MODEL_INDEX", self.model_idx)
        self.draw_spider(0)
        if hasattr(self, 'model_var') and self.model_var:
            self.model_var.set(self.get_model_display_name(self.model_idx))
        print(f"[*] Active Spider Model: {self.get_model_display_name(self.model_idx)}")

    def cycle_spider_model(self):
        new_idx = (self.model_idx + 1) % len(SPIDER_MODELS)
        self.set_spider_model(new_idx)
        if self.SOUND_ENABLED:
            play_audio(550 + new_idx * 120, 50)

    def set_spider_scale(self, scale_val, commit=True):
        self.spider_scale = max(0.4, min(2.0, float(scale_val)))
        if commit:
            save_config_value("SPIDER_SIZE_SCALE", f"{self.spider_scale:.2f}")
        self.draw_spider(0)

    def set_spider_speed(self, speed_val, commit=True):
        self.spider_speed = max(2.0, min(25.0, float(speed_val)))
        if commit:
            save_config_value("SPIDER_SPEED", f"{self.spider_speed:.1f}")

    def set_shove_cooldown(self, cooldown_val, commit=True):
        self.SHOVE_COOLDOWN = max(5.0, min(300.0, float(cooldown_val)))
        if commit:
            save_config_value("SHOVE_INTERVAL_SECONDS", f"{int(self.SHOVE_COOLDOWN)}")

    def set_shove_force(self, force_val, commit=True):
        self.SHOVE_FORCE = max(10.0, min(120.0, float(force_val)))
        if commit:
            save_config_value("SHOVE_FORCE", f"{int(self.SHOVE_FORCE)}")

    def set_web_radius(self, radius_val, commit=True):
        self.WEB_RADIUS = int(float(radius_val))
        if commit:
            save_config_value("WEB_RADIUS", self.WEB_RADIUS)
        self.recompute_web_geometry()
        if self.web_built:
            self.draw_web()

    def set_entrance_silk_length(self, length_val, commit=True):
        self.ENTRANCE_SILK_LENGTH = float(length_val)
        if commit:
            save_config_value("ENTRANCE_SILK_LENGTH", f"{int(self.ENTRANCE_SILK_LENGTH)}")

    def set_weave_duration(self, dur_val, commit=True):
        self.WEAVE_DURATION = max(2.0, min(15.0, float(dur_val)))
        if commit:
            save_config_value("WEAVE_DURATION", f"{self.WEAVE_DURATION:.1f}")

    def set_web_thickness(self, thick_val, commit=True):
        self.web_thickness = max(1.0, min(4.5, float(thick_val)))
        if commit:
            save_config_value("WEB_THREAD_THICKNESS", f"{self.web_thickness:.1f}")
        if self.web_built:
            self.draw_web()

    def set_bungee_distance(self, dist_val, commit=True):
        self.BUNGEE_DROP_DISTANCE = float(dist_val)
        if commit:
            save_config_value("BUNGEE_DROP_DISTANCE", int(self.BUNGEE_DROP_DISTANCE))

    def set_theme_index(self, idx):
        self.theme_idx = int(idx) % len(THEMES)
        self.theme = THEMES[self.theme_idx]
        save_config_value("THEME_INDEX", self.theme_idx)
        self.canvas.itemconfig("web", fill=self.theme['web'])
        self.canvas.itemconfig("hub", fill=self.theme['hub'])
        self.canvas.itemconfig("dewdrop", fill=self.theme['dewdrop'])
        self.draw_spider(0)
        if hasattr(self, 'theme_var') and self.theme_var:
            self.theme_var.set(self.get_theme_display_name(self.theme_idx))

    def test_mouse_headbutt(self):
        """Forces the spider to immediately hunt down and headbutt the cursor for live testing."""
        now = time.time()
        self.state = 'CURIOUS'
        self.curious_phase = 'APPROACH'
        self.curious_phase_start = now
        self.last_shove_time = now - self.SHOVE_COOLDOWN
        if self.SOUND_ENABLED:
            play_audio(440, 60)

    def reset_to_defaults(self):
        self.set_spider_model(0)
        self.set_spider_scale(1.0)
        self.set_spider_speed(6.0)
        self.set_shove_cooldown(30.0)
        self.set_shove_force(35.0)
        self.set_web_radius(130)
        self.set_entrance_silk_length(450.0)
        self.BUNGEE_DROP_DISTANCE = 480.0
        save_config_value("BUNGEE_DROP_DISTANCE", 480)
        self.set_theme_index(0)
        self.SOUND_ENABLED = _as_bool(DEFAULT_SETTINGS.get("SOUND_ENABLED", False), False)
        save_config_value("SOUND_ENABLED", self.SOUND_ENABLED)
        if hasattr(self, 'scale_slider') and self.scale_slider: self.scale_slider.set(1.0)
        if hasattr(self, 'speed_slider') and self.speed_slider: self.speed_slider.set(6.0)
        if hasattr(self, 'shove_slider') and self.shove_slider: self.shove_slider.set(30)
        if hasattr(self, 'force_slider') and self.force_slider: self.force_slider.set(35)
        if hasattr(self, 'web_slider') and self.web_slider: self.web_slider.set(130)
        if hasattr(self, 'silk_slider') and self.silk_slider: self.silk_slider.set(450)
        if hasattr(self, 'bungee_slider') and self.bungee_slider: self.bungee_slider.set(480)
        if hasattr(self, 'sound_var') and self.sound_var: self.sound_var.set(self.SOUND_ENABLED)

    def set_language(self, lang_code):
        if self.i18n.load(lang_code):
            save_config_value("LANGUAGE", lang_code)
            had_lb = bool(hasattr(self, 'lang_browser_window') and self.lang_browser_window and self.lang_browser_window.winfo_exists())
            had_settings = bool(hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists())

            if had_lb:
                try:
                    self.lang_browser_window.destroy()
                except Exception:
                    pass
                self.lang_browser_window = None

            if had_settings:
                try:
                    self.settings_window.destroy()
                except Exception:
                    pass
                self.settings_window = None
                self.open_settings_window()

            if had_lb:
                self.open_language_browser()

            if hasattr(self, 'tray_icon') and self.tray_icon:
                try:
                    self.tray_icon.menu = self.build_menu()
                except Exception:
                    pass

    def open_language_browser(self):
        """Interactive, non-blocking World Language Library & Downloader."""
        if hasattr(self, 'lang_browser_window') and self.lang_browser_window and self.lang_browser_window.winfo_exists():
            self.lang_browser_window.lift()
            self.lang_browser_window.focus_force()
            return

        top = tk.Toplevel(self.root)
        self.lang_browser_window = top
        top.title(clean_os_title(self.i18n.t("lb_title", "Global Language Library & Downloader")))
        top.geometry("540x660")
        top.minsize(460, 520)
        top.resizable(True, True)
        top.configure(bg="#090d16")
        top.attributes("-topmost", True)

        def _on_lb_close():
            try:
                top.destroy()
            except Exception:
                pass
            self.lang_browser_window = None
        top.protocol("WM_DELETE_WINDOW", _on_lb_close)

        ico_path = os.path.join(ROOT_DIR, "assets", "app_icon.ico")
        if os.path.exists(ico_path):
            try:
                top.iconbitmap(ico_path)
            except Exception:
                pass
        if hasattr(self, 'icon_photo') and self.icon_photo:
            try:
                top.iconphoto(True, self.icon_photo)
            except Exception:
                pass
        PlatformHelper.force_taskbar_presence(top)
        PlatformHelper.apply_dark_titlebar(top)

        # Header Frame
        hdr = tk.Frame(top, bg="#131c2e", relief="solid", bd=1)
        hdr.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(hdr, text=self.i18n.t("lb_title", "🌐 Global Language Library & Downloader"), font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 2))
        tk.Label(hdr, text=self.i18n.t("lb_subtitle", "Switch languages instantly with zero lag, or download new languages in the background."), font=("Segoe UI", 8), fg="#94a3b8", bg="#131c2e").pack(anchor="w", padx=12, pady=(0, 8))

        # Status label for async progress
        status_lbl = tk.Label(top, text="", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#090d16")
        status_lbl.pack(fill="x", padx=14, pady=2)

        # Style ttk scrollbar
        style = ttk.Style(top)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Dark.Vertical.TScrollbar",
                        gripcount=0,
                        background="#1e293b",
                        darkcolor="#090d16",
                        lightcolor="#334155",
                        troughcolor="#090d16",
                        bordercolor="#090d16",
                        arrowcolor="#38bdf8")
        style.map("Dark.Vertical.TScrollbar",
                  background=[('active', '#38bdf8'), ('pressed', '#0284c7')])

        # Canvas with Dark ttk Scrollbar
        canvas = tk.Canvas(top, bg="#090d16", highlightthickness=0)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview, style="Dark.Vertical.TScrollbar")
        list_frame = tk.Frame(canvas, bg="#090d16")

        list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win_id, width=e.width))

        canvas.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=6)
        scrollbar.pack(side="right", fill="y", padx=(0, 14), pady=6)

        def _on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        top.bind("<MouseWheel>", _on_mousewheel)

        def populate_languages():
            for widget in list_frame.winfo_children():
                widget.destroy()

            installed = self.i18n.get_available_languages()
            cur_lang = self.i18n.lang

            for code, name in WORLD_LANGUAGES:
                is_inst = code in installed
                is_active = (code == cur_lang)

                row = tk.Frame(list_frame, bg="#131c2e", relief="solid", bd=1)
                row.pack(fill="x", pady=3, padx=2)

                info_f = tk.Frame(row, bg="#131c2e")
                info_f.pack(side="left", fill="both", expand=True, padx=10, pady=8)

                tk.Label(info_f, text=name, font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#131c2e").pack(anchor="w")
                if is_active:
                    status_text = self.i18n.t("lb_status_active", "● Active Language")
                    badge_fg = "#00f5d4"
                elif is_inst:
                    status_text = self.i18n.t("lb_status_ready", "✓ Installed & Ready")
                    badge_fg = "#10b981"
                else:
                    status_text = self.i18n.t("lb_status_download", "⬇ Download Needed (~2 KB)")
                    badge_fg = "#94a3b8"
                tk.Label(info_f, text=status_text, font=("Segoe UI", 8), fg=badge_fg, bg="#131c2e").pack(anchor="w")

                act_f = tk.Frame(row, bg="#131c2e")
                act_f.pack(side="right", padx=10, pady=8)

                if is_active:
                    tk.Label(act_f, text=self.i18n.t("lb_active_badge", "Active ✓"), font=("Segoe UI", 9, "bold"), fg="#00f5d4", bg="#131c2e", padx=8).pack()
                elif is_inst:
                    def _make_switch_cmd(c=code):
                        def _sw():
                            self.set_language(c)
                        return _sw
                    tk.Button(act_f, text=self.i18n.t("lb_btn_activate", "Activate"), command=_make_switch_cmd(),
                              font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="#ffffff",
                              activebackground="#0369a1", bd=0, padx=8, pady=3, cursor="hand2").pack()
                else:
                    btn_dl = tk.Button(act_f, text=self.i18n.t("lb_btn_download", "⬇ Download"), font=("Segoe UI", 8, "bold"),
                                       bg="#10b981", fg="#ffffff", activebackground="#059669",
                                       bd=0, padx=8, pady=3, cursor="hand2")
                    def _make_dl_cmd(b=btn_dl, c=code, n=name):
                        def _dl():
                            b.config(text=self.i18n.t("lb_btn_waiting", "⏳ Please wait..."), state="disabled", bg="#475569")
                            status_lbl.config(text=f"🌐 {self.i18n.t('lb_downloading', 'Downloading & translating')} '{n}', {self.i18n.t('lb_btn_waiting', 'please wait...')}", fg="#facc15")
                            def _on_prog(cur, tot):
                                if top.winfo_exists():
                                    pct = int((cur / tot) * 100)
                                    status_lbl.config(text=f"🌐 {self.i18n.t('lb_downloading', 'Downloading')}: {n} ({pct}%)...", fg="#38bdf8")
                            def _on_succ(sc, sn):
                                if top.winfo_exists():
                                    status_lbl.config(text=f"✅ '{sn}' {self.i18n.t('lb_download_succ', 'Downloaded successfully!')}", fg="#10b981")
                                    self.root.after(0, populate_languages)
                            def _on_err(err):
                                if top.winfo_exists():
                                    status_lbl.config(text=f"❌ {self.i18n.t('lb_download_err', 'Download error:')} {err}", fg="#ef4444")
                                    b.config(text=self.i18n.t("lb_retry", "Retry"), state="normal", bg="#dc2626")
                            self.i18n.download_language_async(c, n, on_progress=lambda c, t: self.root.after(0, _on_prog, c, t),
                                                              on_success=lambda sc, sn: self.root.after(0, _on_succ, sc, sn),
                                                              on_error=lambda er: self.root.after(0, _on_err, er))
                        return _dl
                    btn_dl.config(command=_make_dl_cmd())
                    btn_dl.pack()

            # Custom ISO code row at bottom
            custom_row = tk.Frame(list_frame, bg="#0d1526", relief="solid", bd=1)
            custom_row.pack(fill="x", pady=8, padx=2)
            tk.Label(custom_row, text=self.i18n.t("lb_custom_lbl", "Custom Language Code (e.g. 'el', 'ro', 'cs'):"), font=("Segoe UI", 8), fg="#cbd5e1", bg="#0d1526").pack(anchor="w", padx=8, pady=(6, 2))
            c_input_f = tk.Frame(custom_row, bg="#0d1526")
            c_input_f.pack(fill="x", padx=8, pady=(0, 6))
            c_entry = tk.Entry(c_input_f, width=12, font=("Segoe UI", 9), bg="#090d16", fg="#38bdf8", insertbackground="#38bdf8")
            c_entry.pack(side="left", padx=(0, 8))
            def _dl_custom():
                code = c_entry.get().strip().lower()
                if not code: return
                status_lbl.config(text=f"🌐 '{code}' {self.i18n.t('lb_downloading', 'Downloading & creating...')}", fg="#facc15")
                def _on_succ(sc, sn):
                    if top.winfo_exists():
                        status_lbl.config(text=f"✅ '{sn}' {self.i18n.t('lb_download_succ', 'Added successfully!')}", fg="#10b981")
                        self.root.after(0, populate_languages)
                def _on_err(err):
                    if top.winfo_exists():
                        status_lbl.config(text=f"❌ {self.i18n.t('lb_download_err', 'Error:')} {err}", fg="#ef4444")
                self.i18n.download_language_async(code, code.upper(),
                                                  on_progress=lambda c, t: self.root.after(0, lambda: status_lbl.config(text=f"{self.i18n.t('lb_downloading', 'Downloading')} ({int(c/t*100)}%)...")),
                                                  on_success=lambda sc, sn: self.root.after(0, _on_succ, sc, sn),
                                                  on_error=lambda er: self.root.after(0, _on_err, er))
            tk.Button(c_input_f, text=self.i18n.t("lb_custom_btn", "Download"), command=_dl_custom, font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="#ffffff", bd=0, padx=8, pady=2, cursor="hand2").pack(side="left")

        populate_languages()

    download_and_add_language_dialog = open_language_browser

    def show_dark_popup_menu(self):
        """Displays a sleek, deep black context menu at current mouse cursor with live ON/OFF status badges."""
        try:
            px, py = PlatformHelper.get_cursor_pos(self.root)
            menu = tk.Menu(self.root, tearoff=0, bg="#090d16", fg="#f8fafc",
                           activebackground="#0284c7", activeforeground="#ffffff",
                           bd=1, relief="solid", font=("Segoe UI", 9))
            
            hk = self.hotkeys
            species_badge = self.i18n.t(f"species_{self.species}", self.species.capitalize())
            model_name = self.get_model_display_name(self.model_idx)
            theme_name = self.get_theme_display_name(self.theme_idx)
            sound_icon = "🔊" if self.SOUND_ENABLED else "🔇"
            sound_status = f"[{self.i18n.t('status_on', 'ON')}]" if self.SOUND_ENABLED else f"[{self.i18n.t('status_off', 'OFF')}]"
            move_icon = "📍" if self.move_mode else "🔒"
            move_status = f"[{self.i18n.t('status_moving', 'DRAGGING')}]" if self.move_mode else f"[{self.i18n.t('status_locked', 'LOCKED')}]"

            menu.add_command(label=f"🐾 {self.i18n.t('tray_switch_species', 'Switch Creature')}: {species_badge} [{hk.get('SPECIES', 'Shift+M')}]", command=self.switch_species)
            menu.add_command(label=f"{self.i18n.t('tray_settings')} [{hk.get('SETTINGS', 'Shift+P')}]", command=self.open_settings_window)

            if self.species == "butterfly":
                th = self.butterfly.theme
                th_raw = th.get('bengali') if self.i18n.lang == "bn" else th.get('name')
                th_name = f"{th.get('icon','🦋')} {th_raw}"
                menu.add_separator()
                menu.add_command(label=f"🎨 {self.i18n.t('tray_wing_theme', 'Wing Theme')}: {th_name} [{hk.get('THEME', 'Shift+T')}]", command=self.butterfly.cycle_theme)
                menu.add_command(label=f"🥚 {self.i18n.t('tray_relocate_cocoon', 'Relocate Cocoon / Egg')} [{hk.get('MOVE', 'Shift+`')}]", command=self.butterfly.set_cocoon_spot_from_cursor)
                menu.add_command(label=f"⏩ {self.i18n.t('tray_advance_stage', 'Advance Stage')} [{hk.get('ADVANCE', 'Shift+E')}]", command=self.butterfly.advance_stage)
                menu.add_command(label=f"🔄 {self.i18n.t('tray_restart_lifecycle', 'Restart Life Cycle')} [{hk.get('RESTART', 'Shift+C')}]", command=self.butterfly.restart_lifecycle)
                menu.add_command(label=f"✨ {self.i18n.t('tray_fairy_dust', 'Fairy Dust Burst')} [{hk.get('BUG', 'Shift+F')}]", command=self.butterfly.trigger_flight_sparkle)
            elif self.species == "bird":
                th = self.bird.theme
                menu.add_separator()
                menu.add_command(label=f"🪶 {self.i18n.t('tray_bird_theme', 'Plumage Theme')}: {th.get('name','Theme')} [{hk.get('THEME', 'Shift+T')}]", command=self.bird.cycle_theme)
                menu.add_command(label=f"🪺 {self.i18n.t('tray_bird_nest', 'Relocate Nest')} [{hk.get('MOVE', 'Shift+`')}]", command=self.bird.set_nest_spot_from_cursor)
                menu.add_command(label=f"🎵 {self.i18n.t('tray_bird_song', 'Bird Call & Flight')} [{hk.get('BUG', 'Shift+F')}]", command=self.bird.trigger_song_flight)
                menu.add_command(label=f"🏠 {self.i18n.t('tray_bird_return', 'Return to Nest')} [{hk.get('BUNGEE', 'Shift+B')}]", command=self.bird.return_to_nest)
            elif self.species == "chameleon":
                th = self.chameleon.theme
                th_raw = th.get('bengali') if self.i18n.lang == "bn" else th.get('name')
                th_name = f"🦎 {th_raw}"
                menu.add_separator()
                menu.add_command(label=f"🎨 {self.i18n.t('tray_gecko_theme', 'Camouflage Theme')}: {th_name} [{hk.get('THEME', 'Shift+T')}]", command=self.chameleon.cycle_color)
                menu.add_command(label=f"📍 {self.i18n.t('tray_relocate_gecko', 'Relocate Gecko')} [{hk.get('MOVE', 'Shift+`')}]", command=self.chameleon.set_spot_from_cursor)
                menu.add_command(label=f"👅 {self.i18n.t('tray_gecko_hunt', 'Ballistic Tongue Zap')} [{hk.get('BUG', 'Shift+F')}]", command=self.chameleon.trigger_hunt)
            else: # Default spider actions
                menu.add_command(label=f"🕷 {self.i18n.t('tray_switch_model')}: {model_name} [{hk.get('MODEL', 'Shift+W')}]", command=self.cycle_spider_model)
                menu.add_separator()
                menu.add_command(label=f"{self.i18n.t('tray_restart')} [{hk.get('RESTART', 'Shift+C')}]", command=self.start_entrance)
                menu.add_command(label=f"{self.i18n.t('tray_set_entry')} [{hk.get('ENTRY', 'Shift+Q')}]", command=self.set_entry_point_from_cursor)
                menu.add_command(label=f"🎨 {self.i18n.t('tray_switch_theme')}: {theme_name} [{hk.get('THEME', 'Shift+T')}]", command=self.switch_theme)
                menu.add_command(label=f"{self.i18n.t('tray_spawn_insect')} [{hk.get('BUG', 'Shift+F')}]", command=self.spawn_insect)
                menu.add_command(label=f"{self.i18n.t('tray_bungee')} [{hk.get('BUNGEE', 'Shift+B')}]", command=self.start_bungee_jump)
                menu.add_command(label=f"{self.i18n.t('tray_hatch')} [{hk.get('BABIES', 'Shift+H')}]", command=self.hatch_eggs)

            menu.add_separator()
            menu.add_command(label=f"{self.i18n.t('tray_health')} [{hk.get('REMINDER', 'Shift+R')}]", command=self.show_health_reminder)
            menu.add_command(label=f"{sound_icon} {self.i18n.t('tray_sound')}: {sound_status} [{hk.get('SOUND', 'Shift+S')}]", command=self.toggle_sound)
            menu.add_command(label=f"{move_icon} {self.i18n.t('tray_move_web')}: {move_status} [{hk.get('MOVE', 'Shift+`')}]", command=self.toggle_move_mode)
            menu.add_separator()
            menu.add_command(label=f"{self.i18n.t('tray_exit')} [Shift+ESC]", command=self.quit_app)
            
            menu.tk_popup(px, py)
        except Exception as e:
            print("Dark popup menu error:", e)

    def open_settings_window(self):
        """Opens a modern, pitch-black themed Live Settings & Customizer control panel."""
        if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.deiconify()
            self.settings_window.lift()
            self.settings_window.focus_force()
            PlatformHelper.force_taskbar_presence(self.settings_window)
            return

        top = tk.Toplevel(self.root)
        self.settings_window = top
        top.title(clean_os_title(self.i18n.t("win_title", "Desktop Spider — Live Settings & Customizer")))
        top.geometry("580x760")
        top.minsize(480, 600)
        top.resizable(True, True)
        top.configure(bg="#090d16")
        top.attributes("-topmost", True)

        ico_path = os.path.join(ROOT_DIR, "assets", "app_icon.ico")
        if os.path.exists(ico_path):
            try:
                top.iconbitmap(ico_path)
            except Exception:
                pass
        if hasattr(self, 'icon_photo') and self.icon_photo:
            try:
                top.iconphoto(True, self.icon_photo)
            except Exception:
                pass
        PlatformHelper.force_taskbar_presence(top)
        PlatformHelper.apply_dark_titlebar(top)

        # Configure custom cyber dark ttk scrollbar (eliminates native white scrollbar completely!)
        style = ttk.Style(top)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Dark.Vertical.TScrollbar",
                        gripcount=0,
                        background="#1e293b",
                        darkcolor="#090d16",
                        lightcolor="#334155",
                        troughcolor="#090d16",
                        bordercolor="#090d16",
                        arrowcolor="#38bdf8")
        style.map("Dark.Vertical.TScrollbar",
                  background=[('active', '#38bdf8'), ('pressed', '#0284c7')])

        canvas = tk.Canvas(top, bg="#090d16", highlightthickness=0)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview, style="Dark.Vertical.TScrollbar")
        frame = tk.Frame(canvas, bg="#090d16")

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        content_window = canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(content_window, width=e.width))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            if canvas.winfo_exists():
                if getattr(event, "num", None) == 4:
                    canvas.yview_scroll(-3, "units")
                elif getattr(event, "num", None) == 5:
                    canvas.yview_scroll(3, "units")
                else:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        top.bind("<MouseWheel>", _on_mousewheel)
        top.bind("<Button-4>", _on_mousewheel)
        top.bind("<Button-5>", _on_mousewheel)

        def on_close():
            try:
                top.destroy()
            except Exception:
                pass
            self.settings_window = None
        top.protocol("WM_DELETE_WINDOW", on_close)

        PAD_X = 16

        # --- HEADER ---
        header_frame = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        header_frame.pack(fill="x", padx=PAD_X, pady=(12, 8))
        tk.Label(header_frame, text=self.i18n.t("header_title", "Desktop Spider Live Control Panel"), font=("Segoe UI", 13, "bold"), fg="#38bdf8", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 2))
        tk.Label(header_frame, text=self.i18n.t("header_sub", "Changes apply immediately live on desktop!"), font=("Segoe UI", 9), fg="#94a3b8", bg="#131c2e").pack(anchor="w", padx=12, pady=(0, 8))

        # --- CARD 0: LANGUAGE & LOCALIZATION ---
        card0 = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card0.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card0, text=self.i18n.t("card_lang", "Language & Localization"), font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))
        lang_row = tk.Frame(card0, bg="#131c2e")
        lang_row.pack(fill="x", padx=12, pady=(2, 8))
        
        avail_langs = self.i18n.get_available_languages()
        cur_lang_code = self.i18n.lang
        self.lang_var = tk.StringVar(value=avail_langs.get(cur_lang_code, cur_lang_code.upper()))
        
        def on_lang_select(choice_name):
            for code, name in avail_langs.items():
                if name == choice_name:
                    self.set_language(code)
                    break
                    
        lang_menu = tk.OptionMenu(lang_row, self.lang_var, *avail_langs.values(), command=on_lang_select)
        lang_menu.config(bg="#090d16", fg="#f8fafc", activebackground="#0284c7", activeforeground="#ffffff", highlightthickness=0, font=("Segoe UI", 9))
        lang_menu["menu"].config(bg="#090d16", fg="#f8fafc", activebackground="#0284c7", font=("Segoe UI", 9))
        lang_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        tk.Button(lang_row, text=self.i18n.t("btn_add_lang", "Add / Download New Language..."), command=self.open_language_browser,
                  bg="#0284c7", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10,
                  wraplength=185, justify="center").pack(side="right", fill="y")

        # --- CARD 0: DESKTOP CREATURE ECOSYSTEM (6 ANIMATED PETS) ---
        card0 = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card0.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card0, text=self.i18n.t("card_species", "🐾 Desktop Creature & Species"), font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))

        species_data = [
            ("spider", self.i18n.t("species_spider", "🕷️ Spider")),
            ("butterfly", self.i18n.t("species_butterfly", "🦋 Butterfly")),
            ("chameleon", self.i18n.t("species_chameleon", "🦎 Chameleon")),
            ("fireflies", self.i18n.t("species_fireflies", "💡 Fireflies")),
            ("dragon", self.i18n.t("species_dragon", "🐉 Dragon")),
            ("jellyfish", self.i18n.t("species_jellyfish", "🪼 Jellyfish")),
            ("bird", self.i18n.t("species_bird", "🦚 Royal Crested Bird")),
        ]

        grid_sp = tk.Frame(card0, bg="#131c2e")
        grid_sp.pack(fill="x", padx=12, pady=(0, 6))

        for idx, (sp_code, sp_title) in enumerate(species_data):
            r = idx // 2
            c = idx % 2
            is_active = (self.species == sp_code)
            btn = tk.Button(
                grid_sp, text=sp_title,
                font=("Segoe UI", 9, "bold" if is_active else "normal"),
                bg="#0284c7" if is_active else "#1e293b", fg="#ffffff",
                activebackground="#0369a1", bd=0, padx=8, pady=7, cursor="hand2",
                wraplength=205, justify="center", height=2,
                command=lambda sc=sp_code: [self.switch_species(sc), refresh_ui()]
            )
            btn.grid(row=r, column=c, sticky="ew", padx=3, pady=3)
            grid_sp.columnconfigure(c, weight=1)

        # Summon Pet to Center Screen Button
        summon_btn = tk.Button(
            card0,
            text=self.i18n.t("btn_summon_center", "🎯 স্ক্রিনের মাঝে ফিরিয়ে আনুন (Summon Pet)"),
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7", fg="#ffffff",
            activebackground="#0369a1", bd=0, padx=12, pady=7, cursor="hand2",
            command=self.summon_pet_to_center
        )
        summon_btn.pack(fill="x", padx=12, pady=(4, 6))

        # Active Creature Special Controls
        ctl_frame = tk.Frame(card0, bg="#0d1526", bd=1, relief="solid")
        ctl_frame.pack(fill="x", padx=12, pady=(4, 8))

        if self.species == "butterfly":
            from creatures.butterfly import BUTTERFLY_THEMES
            stage_names = {
                "CATERPILLAR": self.i18n.t("stage_caterpillar", "🐛 Caterpillar"),
                "CATERPILLAR_EATING": self.i18n.t("stage_eating", "🍃 Eating Fresh Leaf"),
                "WALKING_TO_COCOON": self.i18n.t("stage_walking_cocoon", "🚶 Walking to Cocoon Spot"),
                "COCOON_ENTERING": self.i18n.t("stage_entering_cocoon", "🚪 Entering Silk Cocoon"),
                "CHRYSALIS": self.i18n.t("stage_chrysalis", "🌿 Chrysalis Cocoon"),
                "EMERGENCE": self.i18n.t("stage_emergence", "✨ Butterfly Emergence"),
                "FLYING": self.i18n.t("stage_flying", "🦋 Free Flight")
            }
            cur_stage_lbl = stage_names.get(self.butterfly.stage, self.butterfly.stage)
            tk.Label(ctl_frame, text=f"{self.i18n.t('lbl_butterfly_stage', 'Current Life Stage:')} {cur_stage_lbl}", font=("Segoe UI", 9, "bold"), fg="#10b981", bg="#0d1526", wraplength=440, justify="left").pack(anchor="w", padx=8, pady=(6, 4))

            # Action Buttons Row
            bf_act_frame = tk.Frame(ctl_frame, bg="#0d1526")
            bf_act_frame.pack(fill="x", padx=8, pady=(2, 6))
            bf_act_frame.columnconfigure(0, weight=1)
            bf_act_frame.columnconfigure(1, weight=1)
            bf_act_frame.columnconfigure(2, weight=1)

            btn_adv_txt = f"{self.i18n.t('btn_bf_advance', 'Advance')} [{self.hotkeys.get('ADVANCE', 'Shift+E')}]"
            tk.Button(
                bf_act_frame, text=btn_adv_txt,
                font=("Segoe UI", 8, "bold"), bg="#059669", fg="#ffffff", bd=0, padx=4, pady=5, cursor="hand2",
                command=lambda: [self.butterfly.advance_stage(), refresh_ui()]
            ).grid(row=0, column=0, sticky="ew", padx=2, pady=2)

            btn_rst_txt = f"{self.i18n.t('btn_bf_restart', 'Restart')} [{self.hotkeys.get('RESTART', 'Shift+C')}]"
            tk.Button(
                bf_act_frame, text=btn_rst_txt,
                font=("Segoe UI", 8), bg="#334155", fg="#ffffff", bd=0, padx=4, pady=5, cursor="hand2",
                command=lambda: [self.butterfly.restart_lifecycle(), refresh_ui()]
            ).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

            btn_reloc_txt = f"{self.i18n.t('btn_bf_relocate', 'Relocate Cocoon')} [{self.hotkeys.get('MOVE', 'Shift+`')}]"
            tk.Button(
                bf_act_frame, text=btn_reloc_txt,
                font=("Segoe UI", 8, "bold"), bg="#d97706", fg="#ffffff", bd=0, padx=4, pady=5, cursor="hand2",
                command=lambda: [self.butterfly.set_cocoon_spot_from_cursor(), refresh_ui()]
            ).grid(row=0, column=2, sticky="ew", padx=2, pady=2)

            # Direct Jump Stages Row
            bf_jump_frame = tk.Frame(ctl_frame, bg="#0d1526")
            bf_jump_frame.pack(fill="x", padx=8, pady=(0, 6))
            bf_jump_frame.columnconfigure(0, weight=1)
            bf_jump_frame.columnconfigure(1, weight=1)
            bf_jump_frame.columnconfigure(2, weight=1)

            st1_lbl = self.i18n.t("stage_caterpillar", "🐛 Caterpillar")
            st2_lbl = self.i18n.t("stage_chrysalis", "🌿 Chrysalis")
            st3_lbl = self.i18n.t("stage_flying", "🦋 Flying")

            tk.Button(
                bf_jump_frame, text=st1_lbl,
                font=("Segoe UI", 8, "bold" if self.butterfly.stage in ["CATERPILLAR", "CATERPILLAR_EATING", "WALKING_TO_COCOON"] else "normal"),
                bg="#15803d" if self.butterfly.stage in ["CATERPILLAR", "CATERPILLAR_EATING", "WALKING_TO_COCOON"] else "#1e293b",
                fg="#ffffff", bd=0, padx=2, pady=4, cursor="hand2",
                command=lambda: [self.butterfly.set_stage("CATERPILLAR"), refresh_ui()]
            ).grid(row=0, column=0, sticky="ew", padx=2, pady=2)

            tk.Button(
                bf_jump_frame, text=st2_lbl,
                font=("Segoe UI", 8, "bold" if self.butterfly.stage in ["COCOON_ENTERING", "CHRYSALIS", "EMERGENCE"] else "normal"),
                bg="#b45309" if self.butterfly.stage in ["COCOON_ENTERING", "CHRYSALIS", "EMERGENCE"] else "#1e293b",
                fg="#ffffff", bd=0, padx=2, pady=4, cursor="hand2",
                command=lambda: [self.butterfly.set_stage("CHRYSALIS"), refresh_ui()]
            ).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

            tk.Button(
                bf_jump_frame, text=st3_lbl,
                font=("Segoe UI", 8, "bold" if self.butterfly.stage == "FLYING" else "normal"),
                bg="#0284c7" if self.butterfly.stage == "FLYING" else "#1e293b",
                fg="#ffffff", bd=0, padx=2, pady=4, cursor="hand2",
                command=lambda: [self.butterfly.set_stage("FLYING"), refresh_ui()]
            ).grid(row=0, column=2, sticky="ew", padx=2, pady=2)

            # 4-Theme Selection Grid
            tk.Label(ctl_frame, text=self.i18n.t("lbl_wing_themes", "🎨 Wing Color Themes (4 Styles):"), font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#0d1526").pack(anchor="w", padx=8, pady=(6, 2))
            th_grid = tk.Frame(ctl_frame, bg="#0d1526")
            th_grid.pack(fill="x", padx=8, pady=(0, 6))
            th_grid.columnconfigure(0, weight=1)
            th_grid.columnconfigure(1, weight=1)

            for t_idx, th in enumerate(BUTTERFLY_THEMES):
                r_pos = t_idx // 2
                c_pos = t_idx % 2
                is_th_active = (self.butterfly.theme_idx == t_idx)
                raw_name = th.get('bengali') if self.i18n.lang == "bn" else th.get('name')
                th_name = f"{th.get('icon','🦋')} {raw_name}{' ✓' if is_th_active else ''}"
                btn_th = tk.Button(
                    th_grid, text=th_name,
                    font=("Segoe UI", 8, "bold" if is_th_active else "normal"),
                    bg=th.get('primary', '#0284c7') if is_th_active else "#1e293b",
                    fg="#ffffff",
                    activebackground=th.get('accent', '#38bdf8'),
                    bd=2 if is_th_active else 0, relief="solid" if is_th_active else "flat",
                    padx=6, pady=4, cursor="hand2",
                    command=lambda idx=t_idx: [self.butterfly.set_theme(idx), refresh_ui()]
                )
                btn_th.grid(row=r_pos, column=c_pos, sticky="ew", padx=2, pady=2)

            # Sliders
            tk.Label(ctl_frame, text=self.i18n.t("lbl_bf_scale", "Butterfly & Caterpillar Size Scale:"), font=("Segoe UI", 8), fg="#cbd5e1", bg="#0d1526").pack(anchor="w", padx=8, pady=(2, 0))
            bf_scale = ModernSlider(
                ctl_frame, from_=0.6, to=2.0, initial=self.butterfly.scale,
                step=0.05, unit="x", bg="#0d1526", accent="#38bdf8",
                command=lambda value: self.butterfly.set_scale(value, commit=False),
                on_commit=lambda value: self.butterfly.set_scale(value, commit=True)
            )
            bf_scale.pack(fill="x", padx=8, pady=(0, 4))

            tk.Label(ctl_frame, text=self.i18n.t("lbl_bf_flight_speed", "Butterfly Flight Speed:"), font=("Segoe UI", 8), fg="#cbd5e1", bg="#0d1526").pack(anchor="w", padx=8, pady=(2, 0))
            bf_flight_spd = ModernSlider(
                ctl_frame, from_=0.5, to=3.0, initial=self.butterfly.flight_speed,
                step=0.1, unit="x", bg="#0d1526", accent="#a855f7",
                command=lambda value: self.butterfly.set_flight_speed(value, commit=False),
                on_commit=lambda value: self.butterfly.set_flight_speed(value, commit=True)
            )
            bf_flight_spd.pack(fill="x", padx=8, pady=(0, 4))

            tk.Label(ctl_frame, text=self.i18n.t("lbl_bf_crawl_speed", "Caterpillar Crawl Speed:"), font=("Segoe UI", 8), fg="#cbd5e1", bg="#0d1526").pack(anchor="w", padx=8, pady=(2, 0))
            bf_crawl_spd = ModernSlider(
                ctl_frame, from_=1.0, to=4.0, initial=self.butterfly.crawl_speed,
                step=0.1, unit="x", bg="#0d1526", accent="#10b981",
                command=lambda value: self.butterfly.set_crawl_speed(value, commit=False),
                on_commit=lambda value: self.butterfly.set_crawl_speed(value, commit=True)
            )
            bf_crawl_spd.pack(fill="x", padx=8, pady=(0, 6))

        elif self.species == "chameleon":
            # Current Theme Display
            cur_th = self.chameleon.theme
            cur_th_title = cur_th.get('bengali') if self.i18n.lang == "bn" else cur_th.get('name')
            tk.Label(
                ctl_frame,
                text=f"{self.i18n.t('tray_gecko_theme', 'Camouflage Theme')}: 🦎 {cur_th_title}",
                font=("Segoe UI", 9, "bold"), fg="#10b981", bg="#0d1526"
            ).pack(anchor="w", padx=8, pady=(4, 4))

            # 4 Quick Theme Selector Buttons
            th_grid = tk.Frame(ctl_frame, bg="#0d1526")
            th_grid.pack(fill="x", padx=8, pady=(0, 6))
            th_grid.columnconfigure(0, weight=1)
            th_grid.columnconfigure(1, weight=1)

            for t_idx, th_info in enumerate(self.chameleon.colors):
                r = t_idx // 2
                c = t_idx % 2
                is_sel = (t_idx == self.chameleon.color_idx)
                th_lbl = th_info.get('bengali') if self.i18n.lang == "bn" else th_info.get('name')
                def make_th_cmd(idx=t_idx):
                    def _sel():
                        self.chameleon.color_idx = idx
                        self.chameleon.theme = self.chameleon.colors[idx]
                        if self.SOUND_ENABLED:
                            play_audio(650, 30)
                        refresh_ui()
                    return _sel
                btn_bg = "#059669" if is_sel else "#1e293b"
                btn_fg = "#ffffff" if is_sel else "#94a3b8"
                tk.Button(
                    th_grid, text=f"{'✓ ' if is_sel else ''}{th_lbl}",
                    font=("Segoe UI", 8), bg=btn_bg, fg=btn_fg, bd=0, padx=4, pady=3, cursor="hand2",
                    wraplength=190, justify="center", command=make_th_cmd()
                ).grid(row=r, column=c, sticky="ew", padx=2, pady=2)

            # Gecko Scale Slider
            tk.Label(ctl_frame, text=self.i18n.t("lbl_gecko_size", "Wall Gecko Size Scale:"), font=("Segoe UI", 8), fg="#cbd5e1", bg="#0d1526").pack(anchor="w", padx=8, pady=(4, 0))
            def on_gecko_scale(val, commit=False):
                self.chameleon.scale = float(val)
                if commit:
                    save_config_value("GECKO_SCALE", float(val))
            gecko_scale_slider = ModernSlider(
                ctl_frame, from_=0.7, to=1.8, initial=self.chameleon.scale,
                step=0.05, unit="x", bg="#0d1526", accent="#10b981",
                command=lambda val: on_gecko_scale(val, commit=False),
                on_commit=lambda val: on_gecko_scale(val, commit=True)
            )
            gecko_scale_slider.pack(fill="x", padx=8, pady=(0, 6))

            # Action Buttons: Tongue Zap & Relocate
            ch_act_frame = tk.Frame(ctl_frame, bg="#0d1526")
            ch_act_frame.pack(fill="x", padx=8, pady=(2, 6))
            ch_act_frame.columnconfigure(0, weight=1)
            ch_act_frame.columnconfigure(1, weight=1)
            tk.Button(
                ch_act_frame, text=self.i18n.t("btn_chameleon_snap", "👅 Ballistic Tongue Zap [Shift+F]"),
                font=("Segoe UI", 9, "bold"), bg="#be123c", fg="#ffffff", bd=0, padx=8, pady=4, cursor="hand2",
                wraplength=200, justify="center", height=2,
                command=self.chameleon.trigger_hunt
            ).grid(row=0, column=0, sticky="ew", padx=(0, 3), pady=2)
            tk.Button(
                ch_act_frame, text=self.i18n.t("tray_relocate_gecko", "📍 Relocate Gecko [Shift+`]"),
                font=("Segoe UI", 9), bg="#047857", fg="#ffffff", bd=0, padx=8, pady=4, cursor="hand2",
                wraplength=200, justify="center", height=2,
                command=lambda: [self.chameleon.set_spot_from_cursor(), refresh_ui()]
            ).grid(row=0, column=1, sticky="ew", padx=(3, 0), pady=2)

        elif self.species == "fireflies":
            tk.Button(
                ctl_frame, text=self.i18n.t("btn_fireflies_pulse", "✨ Synchronized Glow Flash [Shift+F]"),
                font=("Segoe UI", 9, "bold"), bg="#65a30d", fg="#ffffff", bd=0, padx=10, pady=5, cursor="hand2",
                command=self.fireflies.trigger_flash
            ).pack(fill="x", padx=8, pady=6)

        elif self.species == "dragon":
            tk.Button(
                ctl_frame, text=self.i18n.t("btn_dragon_breath", "🔥 Starlight Ember Breath [Shift+F]"),
                font=("Segoe UI", 9, "bold"), bg="#b45309", fg="#ffffff", bd=0, padx=10, pady=5, cursor="hand2",
                command=self.dragon.trigger_breath
            ).pack(fill="x", padx=8, pady=6)

        elif self.species == "jellyfish":
            tk.Button(
                ctl_frame, text=self.i18n.t("btn_jellyfish_pulse", "🌊 Bioluminescent Ripple [Shift+F]"),
                font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="#ffffff", bd=0, padx=10, pady=5, cursor="hand2",
                command=self.jellyfish.trigger_ripple
            ).pack(fill="x", padx=8, pady=6)
        elif self.species == "bird":
            btn_bird_row = tk.Frame(ctl_frame, bg="#0d1526")
            btn_bird_row.pack(fill="x", padx=6, pady=4)
            btn_bird_row.columnconfigure(0, weight=1)
            btn_bird_row.columnconfigure(1, weight=1)
            tk.Button(
                btn_bird_row, text=self.i18n.t("btn_bird_song", "🎵 Bird Call & Flight [Shift+F]"),
                font=("Segoe UI", 9, "bold"), bg="#d97706", fg="#ffffff", bd=0, padx=6, pady=4, cursor="hand2",
                wraplength=200, justify="center", height=2,
                command=self.bird.trigger_song_flight
            ).grid(row=0, column=0, padx=3, sticky="ew", pady=2)
            tk.Button(
                btn_bird_row, text=self.i18n.t("btn_bird_theme", "🪶 Plumage Theme [Shift+T]"),
                font=("Segoe UI", 9, "bold"), bg="#059669", fg="#ffffff", bd=0, padx=6, pady=4, cursor="hand2",
                wraplength=200, justify="center", height=2,
                command=self.bird.cycle_theme
            ).grid(row=0, column=1, padx=3, sticky="ew", pady=2)
            tk.Button(
                btn_bird_row, text=self.i18n.t("btn_bird_nest", "🪺 Relocate Nest [Shift+`]"),
                font=("Segoe UI", 9, "bold"), bg="#78350f", fg="#ffffff", bd=0, padx=6, pady=4, cursor="hand2",
                wraplength=200, justify="center", height=2,
                command=self.bird.set_nest_spot_from_cursor
            ).grid(row=1, column=0, columnspan=2, padx=3, sticky="ew", pady=2)

        elif self.species == "spider":
            spk_lbl = self.i18n.t("lbl_spoke", "Spoke")
            rng_lbl = self.i18n.t("lbl_rings", "Rings")
            act_lbl = self.i18n.t("mode_spider_active", "Silk Arachnid Mode Active")
            spk_info = f"{spk_lbl}: {self.SPOKE_DURATION}s | {rng_lbl}: {self.RING_WEAVE_DURATION}s"
            tk.Label(ctl_frame, text=f"🕷️ {act_lbl} ({spk_info})", font=("Segoe UI", 9), fg="#94a3b8", bg="#0d1526").pack(padx=8, pady=6)

        # Auto-Start with Windows Checkbox
        autostart_var = tk.BooleanVar(value=self.is_autostart_enabled())
        def on_autostart_toggle():
            self.set_autostart(autostart_var.get())

        chk_as = tk.Checkbutton(
            card0, text=self.i18n.t("chk_autostart", "🚀 Start Automatically with Windows (Silent Auto-Run)"),
            variable=autostart_var, command=on_autostart_toggle,
            font=("Segoe UI", 9), fg="#e2e8f0", bg="#131c2e", activebackground="#131c2e",
            activeforeground="#00f5d4", selectcolor="#0b111e"
        )
        chk_as.pack(anchor="w", padx=12, pady=(4, 10))

        def refresh_ui():
            try:
                top.destroy()
                self.open_settings_window()
            except Exception:
                pass

        # --- CARD 1: SPIDER MODEL & ANATOMY ---
        card1 = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card1.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card1, text=self.i18n.t("card_model", "Spider Model & Anatomy"), font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))

        tk.Label(card1, text=f"{self.i18n.t('lbl_model_select', 'Choose Model:')} [{self.hotkeys.get('MODEL', 'Shift+W')}]", font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12)
        model_names = [self.get_model_display_name(i) for i in range(len(SPIDER_MODELS))]
        self.model_var = tk.StringVar(value=self.get_model_display_name(self.model_idx))
        def on_model_select(choice):
            for i, m in enumerate(SPIDER_MODELS):
                if self.get_model_display_name(i) == choice:
                    self.set_spider_model(i)
                    break
        model_menu = tk.OptionMenu(card1, self.model_var, *model_names, command=on_model_select)
        model_menu.config(bg="#090d16", fg="#f8fafc", activebackground="#0284c7", activeforeground="#ffffff", highlightthickness=0, font=("Segoe UI", 9))
        model_menu["menu"].config(bg="#090d16", fg="#f8fafc", activebackground="#0284c7", font=("Segoe UI", 9))
        model_menu.pack(fill="x", padx=12, pady=(2, 6))

        tk.Label(card1, text=self.i18n.t("lbl_spider_scale", "Body Scale / Slimness:"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.scale_slider = ModernSlider(
            card1, from_=0.5, to=1.6, initial=self.spider_scale, step=0.05, unit="x", is_int=False,
            command=lambda v: self.set_spider_scale(v, commit=False),
            on_commit=lambda v: self.set_spider_scale(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.scale_slider.pack(fill="x", padx=12, pady=(0, 8))

        # --- CARD 2: SPEED & MOVEMENT ---
        card2 = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card2.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card2, text=self.i18n.t("card_speed", "Speed & Mobility"), font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))

        tk.Label(card2, text=self.i18n.t("lbl_crawl_speed", "Normal Crawl Speed:"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.speed_slider = ModernSlider(
            card2, from_=3.0, to=18.0, initial=self.spider_speed, step=0.5, unit=" px/s", is_int=False,
            command=lambda v: self.set_spider_speed(v, commit=False),
            on_commit=lambda v: self.set_spider_speed(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.speed_slider.pack(fill="x", padx=12, pady=(0, 8))

        # --- CARD 3: MOUSE HUNTING & ATTACK ---
        card3 = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card3.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card3, text=self.i18n.t("card_hunting", "Mouse Attack & Curiosity"), font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))

        tk.Label(card3, text=self.i18n.t("lbl_shove_interval", "Mouse Attack Timer (sec):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.shove_slider = ModernSlider(
            card3, from_=10, to=120, initial=int(self.SHOVE_COOLDOWN), step=5, unit="s", is_int=True,
            command=lambda v: self.set_shove_cooldown(v, commit=False),
            on_commit=lambda v: self.set_shove_cooldown(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.shove_slider.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(card3, text=self.i18n.t("lbl_shove_force", "Headbutt Shove Force (px):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.force_slider = ModernSlider(
            card3, from_=15, to=85, initial=int(self.SHOVE_FORCE), step=5, unit=" px", is_int=True,
            command=lambda v: self.set_shove_force(v, commit=False),
            on_commit=lambda v: self.set_shove_force(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.force_slider.pack(fill="x", padx=12, pady=(0, 8))

        # --- CARD 4: WEB, SILK & THEMES ---
        card4 = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card4.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card4, text=self.i18n.t("card_web", "Web, Silk & Themes"), font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))

        tk.Label(card4, text=self.i18n.t("lbl_web_radius", "Web Radius (px):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.web_slider = ModernSlider(
            card4, from_=70, to=220, initial=int(self.WEB_RADIUS), step=5, unit=" px", is_int=True,
            command=lambda v: self.set_web_radius(v, commit=False),
            on_commit=lambda v: self.set_web_radius(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.web_slider.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(card4, text=self.i18n.t("lbl_web_thickness", "Web Thread Thickness (px):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.thick_slider = ModernSlider(
            card4, from_=1.0, to=4.0, initial=self.web_thickness, step=0.2, unit=" px", is_int=False,
            command=lambda v: self.set_web_thickness(v, commit=False),
            on_commit=lambda v: self.set_web_thickness(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.thick_slider.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(card4, text=self.i18n.t("lbl_spoke_duration", "Spoke Lines Duration (sec):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.spoke_slider = ModernSlider(
            card4, from_=1.0, to=15.0, initial=self.SPOKE_DURATION, step=0.5, unit="s", is_int=False,
            command=lambda v: self.set_spoke_duration(v, commit=False),
            on_commit=lambda v: self.set_spoke_duration(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.spoke_slider.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(card4, text=self.i18n.t("lbl_ring_duration", "Spiral Rings Weaving Duration (sec):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.ring_slider = ModernSlider(
            card4, from_=2.0, to=30.0, initial=self.RING_WEAVE_DURATION, step=0.5, unit="s", is_int=False,
            command=lambda v: self.set_ring_weave_duration(v, commit=False),
            on_commit=lambda v: self.set_ring_weave_duration(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.ring_slider.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(card4, text=self.i18n.t("lbl_silk_length", "Ceiling Silk Length (px):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        cur_silk = float(self.ENTRANCE_SILK_LENGTH) if self.ENTRANCE_SILK_LENGTH else (self.screen_h * 0.5)
        self.silk_slider = ModernSlider(
            card4, from_=150, to=700, initial=int(cur_silk), step=10, unit=" px", is_int=True,
            command=lambda v: self.set_entrance_silk_length(v, commit=False),
            on_commit=lambda v: self.set_entrance_silk_length(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.silk_slider.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(card4, text=self.i18n.t("lbl_bungee_dist", "Bungee Drop Distance (px):"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(2, 0))
        self.bungee_slider = ModernSlider(
            card4, from_=200, to=700, initial=int(self.BUNGEE_DROP_DISTANCE), step=10, unit=" px", is_int=True,
            command=lambda v: self.set_bungee_distance(v, commit=False),
            on_commit=lambda v: self.set_bungee_distance(v, commit=True),
            bg="#131c2e", accent="#00f5d4"
        )
        self.bungee_slider.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(card4, text=self.i18n.t("lbl_theme", "Color Theme:"), font=("Segoe UI", 9), fg="#cbd5e1", bg="#131c2e").pack(anchor="w", padx=12, pady=(4, 0))
        theme_names = [self.get_theme_display_name(i) for i in range(len(THEMES))]
        self.theme_var = tk.StringVar(value=self.get_theme_display_name(self.theme_idx))
        def on_theme_select(choice):
            for i, t in enumerate(THEMES):
                if self.get_theme_display_name(i) == choice:
                    self.set_theme_index(i)
                    break
        theme_menu = tk.OptionMenu(card4, self.theme_var, *theme_names, command=on_theme_select)
        theme_menu.config(bg="#090d16", fg="#f8fafc", activebackground="#0284c7", activeforeground="#ffffff", highlightthickness=0, font=("Segoe UI", 9))
        theme_menu["menu"].config(bg="#090d16", fg="#f8fafc", activebackground="#0284c7", font=("Segoe UI", 9))
        theme_menu.pack(fill="x", padx=12, pady=(2, 6))

        self.sound_var = tk.BooleanVar(value=self.SOUND_ENABLED)
        def on_sound_toggle():
            self.SOUND_ENABLED = self.sound_var.get()
            save_config_value("SOUND_ENABLED", self.SOUND_ENABLED)
        sound_cb = tk.Checkbutton(card4, text=self.i18n.t("chk_sound", "Enable Sound Effects"), variable=self.sound_var,
                                  command=on_sound_toggle, bg="#131c2e", fg="#f8fafc", selectcolor="#090d16",
                                  activebackground="#131c2e", activeforeground="#38bdf8", font=("Segoe UI", 9))
        sound_cb.pack(anchor="w", padx=12, pady=(0, 8))

        # --- CARD 5: CUSTOM HOTKEYS ---
        card_hk = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card_hk.pack(fill="x", padx=PAD_X, pady=6)
        
        sp_title = self.i18n.t(f"species_{self.species}", self.species.capitalize())
        tk.Label(card_hk, text=f"{self.i18n.t('card_hotkeys', 'Custom Hotkey Settings')} ({sp_title})",
                 font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))
        tk.Label(card_hk, text=self.i18n.t("lbl_hotkey_tip", "Type any key combo (e.g. Shift+W, Ctrl+M, Alt+T, F6, or W):"),
                 font=("Segoe UI", 8), fg="#94a3b8", bg="#131c2e").pack(anchor="w", padx=12, pady=(0, 4))
        
        hk_grid = tk.Frame(card_hk, bg="#131c2e")
        hk_grid.pack(fill="x", padx=12, pady=(2, 6))
        
        hk_entries = {}
        if self.species == "butterfly":
            hk_labels = [
                ("SPECIES", self.i18n.t("hk_bf_species", "Creature Switch:")),
                ("SETTINGS", self.i18n.t("hk_bf_settings", "Settings Panel:")),
                ("ADVANCE", self.i18n.t("hk_bf_advance", "Advance Stage:")),
                ("RESTART", self.i18n.t("hk_bf_restart", "Restart Lifecycle:")),
                ("MOVE", self.i18n.t("hk_bf_move", "Relocate Cocoon / Egg:")),
                ("THEME", self.i18n.t("hk_bf_theme", "Wing Theme Switch:")),
                ("BUG", self.i18n.t("hk_bf_sparkle", "Fairy Dust / Fresh Leaf:")),
                ("SOUND", self.i18n.t("hk_bf_sound", "Sound Toggle:")),
                ("REMINDER", self.i18n.t("hk_bf_reminder", "Health Reminder:")),
                ("EXIT", self.i18n.t("hk_bf_exit", "Quit Application:")),
            ]
        elif self.species == "bird":
            hk_labels = [
                ("SPECIES", self.i18n.t("hk_species", "Creature Switch:")),
                ("SETTINGS", self.i18n.t("hk_settings", "Settings Panel:")),
                ("MOVE", self.i18n.t("hk_bird_move", "Relocate Nest:")),
                ("THEME", self.i18n.t("hk_bird_theme", "Plumage Theme:")),
                ("BUG", self.i18n.t("hk_bird_song", "Bird Call & Flight:")),
                ("BUNGEE", self.i18n.t("hk_bird_return", "Return to Nest:")),
                ("SOUND", self.i18n.t("hk_sound", "Sound Toggle:")),
                ("REMINDER", self.i18n.t("hk_reminder", "Health Reminder:")),
                ("EXIT", self.i18n.t("hk_bf_exit", "Quit Application:")),
            ]
        elif self.species == "chameleon":
            hk_labels = [
                ("SPECIES", self.i18n.t("hk_species", "Creature Switch:")),
                ("SETTINGS", self.i18n.t("hk_settings", "Settings Panel:")),
                ("THEME", self.i18n.t("hk_cham_theme", "Camouflage Color:")),
                ("BUG", self.i18n.t("hk_cham_hunt", "Tongue Zap Hunt:")),
                ("MOVE", self.i18n.t("hk_move_gecko", "Relocate Gecko:")),
                ("SOUND", self.i18n.t("hk_sound", "Sound Toggle:")),
                ("REMINDER", self.i18n.t("hk_reminder", "Health Reminder:")),
                ("EXIT", self.i18n.t("hk_bf_exit", "Quit Application:")),
            ]
        elif self.species in ["fireflies", "dragon", "jellyfish"]:
            hk_labels = [
                ("SPECIES", self.i18n.t("hk_species", "Creature Switch:")),
                ("SETTINGS", self.i18n.t("hk_settings", "Settings Panel:")),
                ("BUG", self.i18n.t(f"hk_{self.species}_pulse", "Action Trigger:")),
                ("SOUND", self.i18n.t("hk_sound", "Sound Toggle:")),
                ("REMINDER", self.i18n.t("hk_reminder", "Health Reminder:")),
                ("EXIT", self.i18n.t("hk_bf_exit", "Quit Application:")),
            ]
        else: # spider
            hk_labels = [
                ("SPECIES", self.i18n.t("hk_species", "Creature Switch:")),
                ("MODEL", self.i18n.t("hk_spider_model", "Model Switch:")),
                ("SETTINGS", self.i18n.t("hk_settings", "Settings Panel:")),
                ("RESTART", self.i18n.t("hk_spider_restart", "Rappel Restart:")),
                ("ENTRY", self.i18n.t("hk_spider_entry", "Set Ceiling Entry:")),
                ("THEME", self.i18n.t("hk_spider_theme", "Switch Theme:")),
                ("BUG", self.i18n.t("hk_spider_bug", "Spawn Insect:")),
                ("BUNGEE", self.i18n.t("hk_spider_bungee", "Bungee Jump:")),
                ("BABIES", self.i18n.t("hk_spider_babies", "Hatch Babies:")),
                ("REMINDER", self.i18n.t("hk_reminder", "Health Reminder:")),
                ("SOUND", self.i18n.t("hk_sound", "Sound Toggle:")),
                ("MOVE", self.i18n.t("hk_spider_move", "Move Web:")),
                ("EXIT", self.i18n.t("hk_bf_exit", "Quit Application:")),
            ]
        
        for idx, (hk_key, hk_lbl) in enumerate(hk_labels):
            row = idx // 2
            col = (idx % 2) * 2
            tk.Label(hk_grid, text=hk_lbl, font=("Segoe UI", 8), fg="#cbd5e1", bg="#131c2e").grid(row=row, column=col, sticky="w", pady=3, padx=(0, 4))
            default_hk = "Shift+E" if hk_key == "ADVANCE" else ("Shift+ESC" if hk_key == "EXIT" else "")
            val = str(self.hotkeys.get(hk_key, default_hk))
            btn_rec = HotkeyRecorderButton(hk_grid, initial_val=val, prompt_text=self.i18n.t("hk_prompt_press", "[Press Key...]"))
            btn_rec.grid(row=row, column=col+1, sticky="w", pady=3, padx=(0, 10))
            hk_entries[hk_key] = btn_rec
            
        def save_hotkeys_action():
            for k, btn_rec in hk_entries.items():
                val = btn_rec.get().strip()
                if val:
                    self.hotkeys[k] = val
            cfg = load_config()
            cfg["HOTKEYS"] = self.hotkeys
            save_full_settings(cfg)
            if hasattr(self, 'tray_icon') and self.tray_icon:
                try:
                    self.tray_icon.menu = self.build_menu()
                except Exception:
                    pass
            saved_msg = self.i18n.t("msg_hotkeys_saved", "Custom hotkeys saved successfully!")
            saved_title = self.i18n.t("title_hotkeys_saved", "Hotkeys Saved")
            messagebox.showinfo(saved_title, saved_msg, parent=self.settings_window)

        tk.Button(card_hk, text=self.i18n.t("btn_save_hotkeys", "Save Hotkeys"), command=save_hotkeys_action,
                  bg="#0ea5e9", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2).pack(anchor="e", padx=12, pady=(2, 8))

        # --- CARD 6: LIVE TEST ACTION BUTTONS ---
        card5 = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card5.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card5, text=self.i18n.t("card_test", "Instant Test Actions"), font=("Segoe UI", 10, "bold"), fg="#f59e0b", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))

        btn_grid = tk.Frame(card5, bg="#131c2e")
        btn_grid.pack(fill="x", padx=12, pady=(0, 8))

        tk.Button(btn_grid, text=self.i18n.t("btn_test_shove", "Test Mouse Headbutt Now"), command=self.test_mouse_headbutt,
                  bg="#dc2626", fg="#ffffff", activebackground="#b91c1c", font=("Segoe UI", 9, "bold"), relief="groove", bd=1).grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        tk.Button(btn_grid, text=self.i18n.t("btn_test_entrance", "Test Ceiling Rappel"), command=self.start_entrance,
                  bg="#0284c7", fg="#ffffff", activebackground="#0369a1", font=("Segoe UI", 9, "bold"), relief="groove", bd=1).grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        tk.Button(btn_grid, text=self.i18n.t("btn_test_bug", "Spawn Insect"), command=self.spawn_insect,
                  bg="#059669", fg="#ffffff", activebackground="#047857", font=("Segoe UI", 9), relief="groove", bd=1).grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        tk.Button(btn_grid, text=self.i18n.t("btn_test_bungee", "Bungee Jump"), command=self.start_bungee_jump,
                  bg="#7c3aed", fg="#ffffff", activebackground="#6d28d9", font=("Segoe UI", 9), relief="groove", bd=1).grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # Spider anatomy/mobility/web controls belong only to the spider.
        # Other species show their own controls in the active-creature card above.
        if self.species != "spider":
            for spider_card in (card1, card2, card3, card4, card5):
                spider_card.pack_forget()

        # --- CARD 7: SOFTWARE UPDATES & GITHUB ---
        card_upd = tk.Frame(frame, bg="#131c2e", relief="solid", bd=1)
        card_upd.pack(fill="x", padx=PAD_X, pady=6)
        tk.Label(card_upd, text=self.i18n.t("card_updater", "🔄 Software Updates & GitHub"), font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#131c2e").pack(anchor="w", padx=12, pady=(8, 4))
        
        upd_status_frame = tk.Frame(card_upd, bg="#131c2e")
        upd_status_frame.pack(fill="x", padx=12, pady=(2, 6))

        v_lbl = tk.Label(upd_status_frame, text=f"{self.i18n.t('lbl_version', 'Current Version:')} v{APP_VERSION}", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#131c2e")
        v_lbl.pack(side="left")

        status_lbl = tk.Label(card_upd, text="", font=("Segoe UI", 8), fg="#94a3b8", bg="#131c2e")
        status_lbl.pack(anchor="w", padx=12, pady=(0, 4))

        upd_btn_row = tk.Frame(card_upd, bg="#131c2e")
        upd_btn_row.pack(fill="x", padx=12, pady=(2, 8))

        def on_update_check_result(found, remote_ver, notes):
            if not card_upd.winfo_exists(): return
            if found:
                status_lbl.config(text=f"{self.i18n.t('lbl_update_found', '🚀 New version available:')} v{remote_ver}", fg="#22c55e")
                upd_btn.pack(side="right", padx=(4, 0))
            else:
                status_lbl.config(text=self.i18n.t("lbl_up_to_date", "✅ You are using the latest version!"), fg="#38bdf8")

        def start_check():
            status_lbl.config(text=self.i18n.t("lbl_checking_updates", "Checking GitHub for updates..."), fg="#facc15")
            self.updater.check_for_updates_async(on_result=on_update_check_result, silent=True)

        def start_apply_update():
            status_lbl.config(text="Downloading & applying update...", fg="#facc15")
            def on_prog(msg):
                if status_lbl.winfo_exists():
                    status_lbl.config(text=msg, fg="#facc15")
            def on_succ():
                if messagebox.askyesno("Update Installed", self.i18n.t("msg_update_success") + "\n\nRestart now?", parent=self.settings_window):
                    self.updater.restart_app()
            def on_err(err):
                if status_lbl.winfo_exists():
                    status_lbl.config(text=f"Error: {err}", fg="#ef4444")
            self.updater.apply_update_async(on_progress=on_prog, on_success=on_succ, on_error=on_err)

        check_btn = tk.Button(upd_btn_row, text=self.i18n.t("btn_check_update", "🔍 Check for Updates"),
                              font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="#ffffff", bd=0, padx=8, pady=3, cursor="hand2",
                              command=start_check)
        check_btn.pack(side="left")

        upd_btn = tk.Button(upd_btn_row, text=self.i18n.t("btn_update_now", "✨ Update Now"),
                            font=("Segoe UI", 8, "bold"), bg="#10b981", fg="#ffffff", bd=0, padx=8, pady=3, cursor="hand2",
                            command=start_apply_update)

        chk_auto_var = tk.BooleanVar(value=self.config.get("AUTO_CHECK_UPDATES", True))
        def on_auto_chk_toggle():
            self.config["AUTO_CHECK_UPDATES"] = chk_auto_var.get()
            save_config_value("AUTO_CHECK_UPDATES", chk_auto_var.get())
        tk.Checkbutton(card_upd, text=self.i18n.t("chk_auto_update", "Check for updates on startup"),
                       variable=chk_auto_var, command=on_auto_chk_toggle,
                       font=("Segoe UI", 8), fg="#cbd5e1", bg="#131c2e", activebackground="#131c2e", selectcolor="#090d16").pack(anchor="w", padx=10, pady=(0, 6))

        # --- FOOTER BUTTONS ---
        footer_frame = tk.Frame(frame, bg="#090d16")
        footer_frame.pack(fill="x", padx=PAD_X, pady=(10, 16))

        def save_all_and_close():
            for k, btn_rec in hk_entries.items():
                val = btn_rec.get().strip()
                if val:
                    self.hotkeys[k] = val
            cfg = load_config()
            cfg["HOTKEYS"] = self.hotkeys
            cfg["LANGUAGE"] = self.i18n.lang
            cfg["CREATURE_SPECIES"] = self.species
            cfg["THEME_INDEX"] = self.theme_idx
            cfg["SPIDER_MODEL_INDEX"] = self.model_idx
            cfg["SPIDER_SIZE_SCALE"] = self.spider_scale
            cfg["SPIDER_SPEED"] = self.spider_speed
            cfg["SHOVE_INTERVAL_SECONDS"] = self.SHOVE_COOLDOWN
            cfg["SHOVE_FORCE"] = self.SHOVE_FORCE
            cfg["WEB_RADIUS"] = self.WEB_RADIUS
            cfg["WEB_THREAD_THICKNESS"] = self.web_thickness
            cfg["SPOKE_DURATION"] = self.SPOKE_DURATION
            cfg["RING_WEAVE_DURATION"] = self.RING_WEAVE_DURATION
            cfg["SOUND_ENABLED"] = self.SOUND_ENABLED
            if hasattr(self, 'chameleon'):
                cfg["GECKO_COLOR_INDEX"] = getattr(self.chameleon, 'color_idx', 0)
                cfg["GECKO_SCALE"] = getattr(self.chameleon, 'scale', 1.15)
                cfg["GECKO_X"] = getattr(self.chameleon, 'x', None)
                cfg["GECKO_Y"] = getattr(self.chameleon, 'y', None)
            if hasattr(self, 'butterfly'):
                cfg["BUTTERFLY_THEME_INDEX"] = getattr(self.butterfly, 'theme_idx', 0)
                cfg["BUTTERFLY_SCALE"] = getattr(self.butterfly, 'scale', 1.15)
                cfg["BUTTERFLY_FLIGHT_SPEED"] = getattr(self.butterfly, 'flight_speed', 1.0)
                cfg["BUTTERFLY_CRAWL_SPEED"] = getattr(self.butterfly, 'crawl_speed', 1.8)
                cfg["COCOON_X"] = getattr(self.butterfly, 'cocoon_x', None)
                cfg["COCOON_Y"] = getattr(self.butterfly, 'cocoon_y', None)
            if hasattr(self, 'bird'):
                cfg["BIRD_THEME_INDEX"] = getattr(self.bird, 'theme_idx', 1)
                cfg["BIRD_NEST_X"] = getattr(self.bird, 'nest_x', None)
                cfg["BIRD_NEST_Y"] = getattr(self.bird, 'nest_y', None)
            save_full_settings(cfg)
            if hasattr(self, 'tray_icon') and self.tray_icon:
                try:
                    self.tray_icon.menu = self.build_menu()
                except Exception:
                    pass
            top.withdraw()

        top.protocol("WM_DELETE_WINDOW", save_all_and_close)

        tk.Button(footer_frame, text=self.i18n.t("btn_reset", "Reset to Defaults"), command=self.reset_to_defaults,
                  bg="#475569", fg="#f8fafc", activebackground="#334155", font=("Segoe UI", 9), relief="flat").pack(side="left", padx=4)
        tk.Button(footer_frame, text=self.i18n.t("btn_quit_app", "❌ অ্যাপ সম্পূর্ণ বন্ধ করুন (Quit Pet & App)"), command=self.quit_app,
                  bg="#ef4444", fg="#ffffff", activebackground="#dc2626", font=("Segoe UI", 9, "bold"), relief="flat").pack(side="left", padx=4)
        tk.Button(footer_frame, text=self.i18n.t("btn_save_close", "Save All & Close"), command=save_all_and_close,
                  bg="#10b981", fg="#ffffff", activebackground="#059669", font=("Segoe UI", 9, "bold"), relief="flat").pack(side="right", padx=4)

    def switch_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)
        self.theme = THEMES[self.theme_idx]
        save_config_value("THEME_INDEX", self.theme_idx)
        print(f"Theme switched to: {self.get_theme_display_name(self.theme_idx)}")
        self.canvas.itemconfig("web", fill=self.theme['web'])
        self.canvas.itemconfig("hub", fill=self.theme['hub'])
        self.canvas.itemconfig("dewdrop", fill=self.theme['dewdrop'])

    def destroy_web(self):
        self.canvas.delete("web")
        self.canvas.delete("hub")
        self.canvas.delete("active_thread")
        self.canvas.delete("cocoon")
        self.canvas.delete("insect")
        self.canvas.delete("dewdrop")
        self.canvas.delete("entrance_silk")
        self.canvas.delete("bungee_silk")
        self.web_built = False
        self.weave_phase = 'SPOKE_OUT'
        self.current_spoke_idx = 0
        self.current_ring_idx = 0
        self.current_segment_idx = 0
        self.sub_step = 0

    def reset_egg_sac(self):
        self.egg_state = 'NORMAL'
        self.egg_birth_time = time.time()
        self.babies = []

    def set_entry_point_from_cursor(self):
        """Sets the ceiling entry X coordinate where spider rappels down on restart/launch."""
        mx, my = self.get_mouse_pos()
        self.ENTRY_TOP_X = float(mx)
        save_config_value("ENTRY_TOP_X", int(self.ENTRY_TOP_X))
        print(f"[*] Ceiling Entry X position set to {int(self.ENTRY_TOP_X)} via Shift + Q!")
        if self.SOUND_ENABLED:
            play_audio(1200, 45, 1550, 60)
        self.start_entrance()

    def get_entrance_top_x(self):
        if hasattr(self, 'ENTRY_TOP_X') and self.ENTRY_TOP_X is not None:
            return float(self.ENTRY_TOP_X)
        return float(self.HOME_X)

    def draw_entrance_silk(self, top_x, top_y, bot_y):
        """Draws tapered silk thread: thin at ceiling, thicker near spider's spinnerets."""
        self.canvas.delete("entrance_silk")
        if bot_y <= top_y:
            return
        total_len = bot_y - top_y
        p1_y = top_y + total_len * 0.40
        p2_y = top_y + total_len * 0.75

        # Segment 1 (Top / Ceiling): Thin & delicate (width 1.0)
        self.canvas.create_line(top_x, top_y, top_x, p1_y,
                                fill=self.theme['web'], width=1.0, tags="entrance_silk")
        # Segment 2 (Middle): Medium thickness (width 1.6)
        self.canvas.create_line(top_x, p1_y, top_x, p2_y,
                                fill=self.theme['web'], width=1.6, tags="entrance_silk")
        # Segment 3 (Bottom near spider): Strong natural silk (width 2.3)
        self.canvas.create_line(top_x, p2_y, top_x, bot_y,
                                fill=self.theme['web'], width=2.3, tags="entrance_silk")

    def start_entrance(self):
        """Google Flow style opening: Spider drops snappy down to monitor center, wiggles legs playfully, reels silk into tail, then dashes to nest!"""
        if self.state == 'ENTRANCE':
            return
        self.destroy_web()
        self.web_complete_time = time.time()
        if self.egg_state != 'CARRYING_BABIES':
            self.reset_egg_sac()
        if self.insect:
            self.insect = None
        self.state = 'ENTRANCE'
        self.entrance_phase = 'DROP'
        self.entrance_wiggle_start = 0.0
        self.entrance_drop_speed = 8.0
        self.silk_top_y = float(self.screen_y)
        top_x = self.get_entrance_top_x()
        self.x = top_x
        self.y = float(self.screen_y - 45.0)
        self.vx = 0.0
        self.vy = 0.0
        self.target_angle = math.pi
        self.angle = math.pi
        self.waypoint_timer = time.time()
        if self.SOUND_ENABLED:
            play_audio(700, 35)

    def start_weaving_fresh(self):
        self.start_entrance()

    def spawn_insect(self):
        if self.web_built and not self.insect:
            self.insect = Insect((self.HOME_X, self.HOME_Y), self.WEB_RADIUS)
            self.last_bug_spawn_time = time.time()

    def start_bungee_jump(self):
        """Spider jumps down on an elastic silk thread, bounces, and climbs back up!"""
        if self.state in ['RESTING', 'CURIOUS']:
            self.state = 'BUNGEE'
            self.bungee_start_time = time.time()
            drop_dist = random.uniform(self.BUNGEE_DROP_DISTANCE - 50, self.BUNGEE_DROP_DISTANCE + 90)
            self.bungee_drop_target = min(self.screen_y + self.screen_h - 120, self.HOME_Y + drop_dist)
            self.last_bungee_time = time.time()
            self.trigger_vibration(1.0)
            if self.SOUND_ENABLED:
                play_audio(580, 40)

    def show_health_reminder(self):
        """Displays friendly health/water reminder."""
        self.reminder_active = True
        self.reminder_end_time = time.time() + 9.0
        self.last_reminder_time = time.time()
        self.reminder_idx = (getattr(self, 'reminder_idx', -1) + 1) % 4
        if self.SOUND_ENABLED:
            play_audio(880, 50, 1175, 70)

    def update_loop(self):
        now = time.time()

        # Web vibration physics decay
        if self.web_vibration > 0.01:
            self.web_vibration *= 0.93
            self.vibration_phase += 0.45

        # Check real-time keyboard typing activity (Cross-platform)
        is_typing_now = PlatformHelper.is_user_typing(now, self.last_keyboard_time)
        if is_typing_now:
            self.last_keyboard_time = now

        # User is typing if any key was pressed in last 6.0s or idle seconds is low
        user_is_typing = (now - self.last_keyboard_time < 6.0) or (self.get_system_idle_seconds() < 2.0)

        # Fully Customizable Hotkey Dispatch (Shift, Ctrl, Alt, or plain keys)
        hk = self.hotkeys
        self.poll_hotkey_edges()
        if self.is_hotkey_just_pressed("Shift+ESC") or self.is_hotkey_just_pressed(hk.get("EXIT", "Shift+ESC")):
            self.quit_app()
            return
        elif self.is_hotkey_just_pressed(hk.get('MOVE', 'Shift+`')):
            if self.species == 'butterfly':
                self.butterfly.set_cocoon_spot_from_cursor()
            elif self.species == 'bird':
                self.bird.set_nest_spot_from_cursor()
            elif self.species == 'chameleon':
                self.chameleon.set_spot_from_cursor()
            else:
                self.toggle_move_mode()
            time.sleep(0.25)
        elif self.is_hotkey_just_pressed(hk.get('SPECIES', 'Shift+M')):
            self.switch_species()
            time.sleep(0.35)
        elif self.species == "butterfly" and self.is_hotkey_just_pressed(hk.get('ADVANCE', 'Shift+E')):
            self.butterfly.advance_stage()
            time.sleep(0.3)
        elif self.species == "butterfly" and self.is_hotkey_just_pressed(hk.get('THEME', 'Shift+T')):
            self.butterfly.cycle_theme()
            time.sleep(0.28)
        elif self.species == "bird" and self.is_hotkey_just_pressed(hk.get('THEME', 'Shift+T')):
            self.bird.cycle_theme()
            time.sleep(0.28)
        elif self.species == "chameleon" and self.is_hotkey_just_pressed(hk.get('THEME', 'Shift+T')):
            self.chameleon.cycle_color()
            time.sleep(0.28)
        elif self.species == "bird" and self.is_hotkey_just_pressed(hk.get('BUNGEE', 'Shift+B')):
            self.bird.return_to_nest()
            time.sleep(0.3)
        elif self.species == "spider" and self.is_hotkey_just_pressed(hk.get('MODEL', 'Shift+W')):
            self.cycle_spider_model()
            time.sleep(0.28)
        elif self.is_hotkey_just_pressed(hk.get('SETTINGS', 'Shift+P')):
            self.open_settings_window()
            time.sleep(0.3)
        elif self.is_hotkey_just_pressed(hk.get('THEME', 'Shift+T')):
            self.switch_theme()
            time.sleep(0.25)
        elif self.is_hotkey_just_pressed(hk.get('RESTART', 'Shift+C')):
            if self.species == "spider":
                self.start_entrance()
            elif self.species == "butterfly":
                self.butterfly.restart_lifecycle()
            time.sleep(0.3)
        elif self.species == "spider" and self.is_hotkey_just_pressed(hk.get('ENTRY', 'Shift+Q')):
            self.set_entry_point_from_cursor()
            time.sleep(0.3)
        elif self.is_hotkey_just_pressed(hk.get('BUG', 'Shift+F')):
            if self.species == "spider":
                self.spawn_insect()
            elif self.species == "butterfly":
                self.butterfly.trigger_flight_sparkle()
            elif self.species == "chameleon":
                self.chameleon.trigger_hunt()
            elif self.species == "fireflies":
                self.fireflies.trigger_flash()
            elif self.species == "dragon":
                self.dragon.trigger_breath()
            elif self.species == "jellyfish":
                self.jellyfish.trigger_ripple()
            elif self.species == "bird":
                self.bird.trigger_song_flight()
            time.sleep(0.3)
        elif self.is_hotkey_just_pressed(hk.get('BUNGEE', 'Shift+B')):
            self.start_bungee_jump()
            time.sleep(0.3)
        elif self.species == "spider" and self.is_hotkey_just_pressed(hk.get('BABIES', 'Shift+H')):
            self.hatch_eggs()
            time.sleep(0.3)
        elif self.is_hotkey_just_pressed(hk.get('REMINDER', 'Shift+R')):
            self.show_health_reminder()
            time.sleep(0.3)
        elif self.is_hotkey_just_pressed(hk.get('SOUND', 'Shift+S')):
            self.toggle_sound()
            time.sleep(0.3)

        # Mouse tracking with jitter filtering
        mx, my = self.get_mouse_pos()
        mouse_dist_moved = math.hypot(mx - self.last_mouse_x, my - self.last_mouse_y)
        if mouse_dist_moved > 6.0: # Ignore optical mouse micro-drift
            self.last_mouse_move_time = now
            self.last_mouse_x = mx
            self.last_mouse_y = my

        dx_mouse = self.x - mx
        dy_mouse = self.y - my
        dist_mouse = math.hypot(dx_mouse, dy_mouse)
        mouse_is_active = (now - self.last_mouse_move_time < 0.8)

        # Move Mode
        if self.move_mode:
            pad = self.WEB_RADIUS + 40
            clamped_mx = max(self.screen_x + pad, min(self.screen_x + self.screen_w - pad, mx))
            clamped_my = max(self.screen_y + pad, min(self.screen_y + self.screen_h - pad, my))
            delta_x = clamped_mx - self.HOME_X
            delta_y = clamped_my - self.HOME_Y
            if abs(delta_x) > 0.5 or abs(delta_y) > 0.5:
                self.canvas.move("web", delta_x, delta_y)
                self.canvas.move("dewdrop", delta_x, delta_y)
                self.canvas.move("active_thread", delta_x, delta_y)
                self.canvas.move("cocoon", delta_x, delta_y)
                if self.insect:
                    self.insect.x += delta_x
                    self.insect.y += delta_y
                    self.canvas.move("insect", delta_x, delta_y)
                self.HOME_X = float(clamped_mx)
                self.HOME_Y = float(clamped_my)
                self.x += delta_x
                self.y += delta_y
                self.recompute_web_geometry()
            self.draw_babies()
            self.draw_spider(0)
            self.draw_health_reminder()
            self.draw_onboarding_hint()
            self.root.after(16, self.update_loop)
            return

        # Egg lifecycle
        if self.egg_state == 'EGG_SAC':
            if self.web_built and (now - self.egg_birth_time > 45.0):
                self.hatch_eggs()
        elif self.egg_state == 'CARRYING_BABIES':
            if dist_mouse < 75 and mouse_is_active:
                for b in self.babies:
                    if b.on_back and random.random() < 0.8:
                        b.scatter()
            if (now - self.egg_birth_time > 180.0) and all(b.on_back for b in self.babies) and self.state == 'RESTING':
                self.reset_egg_sac()

        for b in self.babies:
            b.update()

        # Update Insect
        if self.insect:
            was_trapped = self.insect.trapped
            self.insect.update()
            if not was_trapped and self.insect.trapped:
                self.trigger_vibration(1.5)
                if self.SOUND_ENABLED:
                    play_audio(1050, 40, 1400, 50)
        else:
            if self.web_built and (now - self.last_bug_spawn_time > self.BUG_INTERVAL):
                self.spawn_insect()

        # Periodic Auto Bungee Jump
        if self.BUNGEE_AUTO_ENABLED and self.state == 'RESTING' and (now - self.last_bungee_time > 80.0):
            if random.random() < 0.02:
                self.start_bungee_jump()

        # Periodic Health Reminder
        if now - self.last_reminder_time > self.REMINDER_INTERVAL:
            self.show_health_reminder()

        # === MULTI-CREATURE ROUTING (SPIDER vs BUTTERFLY) ===
        if self.species == "butterfly":
            self.butterfly.update(now)
            self.butterfly.draw(self.canvas)
            self.draw_health_reminder()
            self.draw_onboarding_hint()
            self.update_screen_shake(now)
            self.root.after(16, self.update_loop)
            return
        elif self.species == "chameleon":
            self.chameleon.update(now)
            self.chameleon.draw(self.canvas)
            self.draw_health_reminder()
            self.draw_onboarding_hint()
            self.update_screen_shake(now)
            self.root.after(16, self.update_loop)
            return
        elif self.species == "fireflies":
            self.fireflies.update(now)
            self.fireflies.draw(self.canvas)
            self.draw_health_reminder()
            self.draw_onboarding_hint()
            self.update_screen_shake(now)
            self.root.after(16, self.update_loop)
            return
        elif self.species == "dragon":
            self.dragon.update(now)
            self.dragon.draw(self.canvas)
            self.draw_health_reminder()
            self.draw_onboarding_hint()
            self.update_screen_shake(now)
            self.root.after(16, self.update_loop)
            return
        elif self.species == "jellyfish":
            self.jellyfish.update(now)
            self.jellyfish.draw(self.canvas)
            self.draw_health_reminder()
            self.draw_onboarding_hint()
            self.update_screen_shake(now)
            self.root.after(16, self.update_loop)
            return
        elif self.species == "bird":
            self.bird.update(now)
            self.bird.draw(self.canvas)
            self.draw_health_reminder()
            self.draw_onboarding_hint()
            self.update_screen_shake(now)
            self.root.after(16, self.update_loop)
            return
        else:
            # Spider mode active
            pass

        # Egg lifecycle
        if self.egg_state == 'EGG_SAC':
            if self.web_built and (now - self.egg_birth_time > 45.0):
                self.hatch_eggs()
        elif self.egg_state == 'CARRYING_BABIES':
            if dist_mouse < 75 and mouse_is_active:
                for b in self.babies:
                    if b.on_back and random.random() < 0.8:
                        b.scatter()
            if (now - self.egg_birth_time > 180.0) and all(b.on_back for b in self.babies) and self.state == 'RESTING':
                self.reset_egg_sac()

        for b in self.babies:
            b.update()

        # Update Insect
        if self.insect:
            was_trapped = self.insect.trapped
            self.insect.update()
            if not was_trapped and self.insect.trapped:
                self.trigger_vibration(1.5)
                if self.SOUND_ENABLED:
                    play_audio(1050, 40, 1400, 50)
        else:
            if self.web_built and (now - self.last_bug_spawn_time > self.BUG_INTERVAL):
                self.spawn_insect()

        # Periodic Auto Bungee Jump
        if self.BUNGEE_AUTO_ENABLED and self.state == 'RESTING' and (now - self.last_bungee_time > 80.0):
            if random.random() < 0.02:
                self.start_bungee_jump()

        # Periodic Health Reminder
        if now - self.last_reminder_time > self.REMINDER_INTERVAL:
            self.show_health_reminder()

        # === 0. GOOGLE FLOW STYLE ENTRANCE (DESCENDING ON SILK FROM SCREEN TOP) ===
        if self.state == 'ENTRANCE':
            self.handle_entrance(now)

        # === 1. FLEEING BEHAVIOR ===
        elif self.state != 'ENTRANCE' and (
            (dist_mouse < self.PANIC_RADIUS and mouse_is_active) or 
            (self.state == 'WEAVING' and math.hypot(mx - self.HOME_X, my - self.HOME_Y) < self.WEB_RADIUS + 30 and mouse_is_active)
        ):
            if self.state == 'BUNGEE':
                self.canvas.delete("bungee_silk")
            if self.state == 'ENTRANCE':
                self.canvas.delete("entrance_silk")
            # Immediately destroy web if user brings mouse cursor during weaving or resting!
            self.destroy_web()
            if self.insect:
                self.insect = None

            self.state = 'FLEEING'
            self.last_panic_time = now
            force = ((self.PANIC_RADIUS - min(self.PANIC_RADIUS, dist_mouse)) / self.PANIC_RADIUS) ** 1.1
            angle_away = math.atan2(dy_mouse, dx_mouse)
            repel_speed = 6.2
            self.vx += math.cos(angle_away) * force * repel_speed
            self.vy += math.sin(angle_away) * force * repel_speed
            self.vx += (random.random() - 0.5) * 1.5
            self.vy += (random.random() - 0.5) * 1.5
            self.target_angle = angle_away + math.pi / 2

        # === 2. CALMING & RETURNING ===
        elif self.state == 'FLEEING':
            if not mouse_is_active or dist_mouse > self.PANIC_RADIUS + 30:
                self.state = 'RETURNING'

        elif self.state == 'RETURNING':
            dist_home = math.hypot(self.HOME_X - self.x, self.HOME_Y - self.y)
            if dist_home > 8:
                angle_home = math.atan2(self.HOME_Y - self.y, self.HOME_X - self.x)
                # Fast nimble return: scales with distance, up to 9.5 speed!
                walk_speed = min(9.5, max(6.2, dist_home / 16.0))
                hx = math.cos(angle_home) * walk_speed
                hy = math.sin(angle_home) * walk_speed

                SAFE_MOUSE_GAP = 120.0
                if dist_mouse < SAFE_MOUSE_GAP and dist_mouse > 1.0:
                    avoid_force = ((SAFE_MOUSE_GAP - dist_mouse) / SAFE_MOUSE_GAP) * 5.0
                    hx += (dx_mouse / dist_mouse) * avoid_force
                    hy += (dy_mouse / dist_mouse) * avoid_force
                    hx += (-dy_mouse / dist_mouse) * (avoid_force * 1.2)
                    hy += (dx_mouse / dist_mouse) * (avoid_force * 1.2)

                self.vx = self.vx * 0.45 + hx * 0.55
                self.vy = self.vy * 0.45 + hy * 0.55
                self.target_angle = math.atan2(self.vy, self.vx) + math.pi / 2
                self.walk_phase += 0.38
            else:
                self.vx = 0
                self.vy = 0
                self.x = float(self.HOME_X)
                self.y = float(self.HOME_Y)
                if not self.web_built:
                    self.state = 'WEAVING'
                    self.weave_start_time = now
                    self.destroy_web()
                else:
                    self.state = 'RESTING'
                    self.target_angle = math.radians(135)

        # === 3. HUNTING TRAPPED INSECT ===
        elif self.state == 'HUNTING' or (self.insect and self.insect.trapped and self.state in ['RESTING', 'WEAVING', 'CURIOUS']):
            self.state = 'HUNTING'
            if not self.insect:
                self.state = 'RETURNING'
            else:
                dist_to_bug = math.hypot(self.insect.x - self.x, self.insect.y - self.y)
                if dist_to_bug > 18:
                    ang_to_bug = math.atan2(self.insect.y - self.y, self.insect.x - self.x)
                    hunt_speed = 4.8
                    self.vx = math.cos(ang_to_bug) * hunt_speed
                    self.vy = math.sin(ang_to_bug) * hunt_speed
                    self.target_angle = ang_to_bug + math.pi / 2
                else:
                    self.state = 'EATING'
                    self.eating_start_time = now
                    self.vx = 0
                    self.vy = 0
                    if self.SOUND_ENABLED:
                        play_audio(400, 30)

        # === 4. SLOW & REALISTIC EATING ===
        elif self.state == 'EATING':
            self.vx = 0
            self.vy = 0
            self.handle_eating(now)

        # === 5. BUNGEE JUMP ON SILK ===
        elif self.state == 'BUNGEE':
            self.handle_bungee(now)

        # === 6. CURIOSITY MODE (Triggered anywhere on screen when user is idle & NOT TYPING) ===
        elif (self.state == 'RESTING' and 
              (now - self.last_shove_time > self.SHOVE_COOLDOWN) and 
              not user_is_typing and 
              (self.get_system_idle_seconds() > 2.5) and 
              not mouse_is_active and 
              (now - self.last_mouse_move_time > 2.5) and 
              (dist_mouse > 40.0)):
            self.state = 'CURIOUS'
            self.curious_phase = 'APPROACH'
            self.curious_phase_start = now

        elif self.state == 'CURIOUS':
            # If user touches keyboard OR moves mouse substantially, spider aborts and flees back immediately!
            if user_is_typing or self.get_system_idle_seconds() < 0.6 or mouse_dist_moved > 14.0:
                self.state = 'RETURNING'
                self.last_shove_time = now
            elif self.curious_phase == 'APPROACH':
                if dist_mouse > 46.0:
                    ang_m = math.atan2(my - self.y, mx - self.x)
                    # Adaptive dash speed: faster when further away so it quickly reaches cursor anywhere across monitors
                    spd = min(16.0, max(self.spider_speed, dist_mouse / 22.0))
                    self.vx = math.cos(ang_m) * spd
                    self.vy = math.sin(ang_m) * spd
                    self.target_angle = ang_m + math.pi / 2
                    self.walk_phase += 0.24
                else:
                    self.vx = 0.0; self.vy = 0.0
                    self.curious_phase = 'ORBIT'
                    self.curious_phase_start = now
                    self.curious_orbit_angle = math.atan2(self.y - my, self.x - mx)

            elif self.curious_phase == 'ORBIT':
                # Circle around cursor for 2.0 seconds, inspecting from all angles ("gol gol gure dekhbe")
                elapsed = now - self.curious_phase_start
                if elapsed < 2.0:
                    self.curious_orbit_angle += 0.065
                    orbit_r = 44.0
                    target_ox = mx + math.cos(self.curious_orbit_angle) * orbit_r
                    target_oy = my + math.sin(self.curious_orbit_angle) * orbit_r
                    self.x += (target_ox - self.x) * 0.25
                    self.y += (target_oy - self.y) * 0.25
                    ang_to_cur = math.atan2(my - self.y, mx - self.x)
                    self.target_angle = ang_to_cur + math.pi / 2
                    self.walk_phase += 0.25
                else:
                    self.curious_phase = 'SHIVER'
                    self.curious_phase_start = now
                    if self.SOUND_ENABLED:
                        play_audio(320, 50)

            elif self.curious_phase == 'SHIVER':
                # Stop and shiver intensely with rage like an angry bull ("nije kepe ragi sharer moto")!
                elapsed = now - self.curious_phase_start
                ang_to_cur = math.atan2(my - self.y, mx - self.x)
                self.target_angle = ang_to_cur + math.pi / 2
                self.walk_phase += 0.50
                if elapsed < 0.95:
                    pass
                else:
                    # Deliver Headbutt #1
                    self.curious_phase = 'SHOVE_1'
                    push_dist = self.SHOVE_FORCE * 0.85
                    push_x = math.cos(ang_to_cur) * push_dist
                    push_y = math.sin(ang_to_cur) * push_dist
                    new_mx = max(self.screen_x + 15, min(self.screen_x + self.screen_w - 15, int(mx + push_x)))
                    new_my = max(self.screen_y + 15, min(self.screen_y + self.screen_h - 15, int(my + push_y)))
                    self.trigger_screen_shake(20.0, impact_x=new_mx, impact_y=new_my)
                    PlatformHelper.set_cursor_pos(new_mx, new_my)
                    self.last_mouse_x = new_mx
                    self.last_mouse_y = new_my
                    self.last_shove_time = now
                    self.curious_phase_start = now
                    if self.SOUND_ENABLED:
                        play_audio(180, 80, 480, 70)

            elif self.curious_phase == 'SHOVE_1':
                elapsed = now - self.curious_phase_start
                if elapsed < 0.45:
                    # Recoiling slightly from impact
                    ang_to_cur = math.atan2(my - self.y, mx - self.x)
                    self.x -= math.cos(ang_to_cur) * 2.5
                    self.y -= math.sin(ang_to_cur) * 2.5
                else:
                    # Deliver Headbutt #2!
                    self.curious_phase = 'SHOVE_2'
                    push_dist = self.SHOVE_FORCE * 1.15
                    ang_to_cur = math.atan2(my - self.y, mx - self.x)
                    push_x = math.cos(ang_to_cur) * push_dist
                    push_y = math.sin(ang_to_cur) * push_dist
                    new_mx = max(self.screen_x + 15, min(self.screen_x + self.screen_w - 15, int(mx + push_x)))
                    new_my = max(self.screen_y + 15, min(self.screen_y + self.screen_h - 15, int(my + push_y)))
                    self.trigger_screen_shake(26.0, impact_x=new_mx, impact_y=new_my)
                    PlatformHelper.set_cursor_pos(new_mx, new_my)
                    self.last_mouse_x = new_mx
                    self.last_mouse_y = new_my
                    self.last_shove_time = now
                    self.curious_phase_start = now
                    if self.SOUND_ENABLED:
                        play_audio(160, 90, 540, 80)

            elif self.curious_phase == 'SHOVE_2':
                elapsed = now - self.curious_phase_start
                if elapsed > 0.45:
                    # Two headbutts done! Proudly walk fast back to home
                    self.curious_phase = 'APPROACH'
                    self.state = 'RETURNING'
                    self.last_shove_time = now

        # === 7. WEAVING CURVED WEB ===
        elif self.state == 'WEAVING':
            self.handle_weaving(now)

        # === 8. RESTING & ORGANIC WEB PATROL (HALKA NORA CORA KORBE) ===
        elif self.state == 'RESTING':
            if not hasattr(self, 'patrol_target_x'):
                self.patrol_target_x = float(self.HOME_X)
                self.patrol_target_y = float(self.HOME_Y)
                self.next_patrol_time = now + random.uniform(6.0, 12.0)
                self.is_patrolling = False

            # Every 6-12 seconds, take curious steps along a spoke or inner ring
            if not self.is_patrolling and now > self.next_patrol_time:
                patrol_angle = random.choice(self.spoke_angles)
                patrol_r = self.WEB_RADIUS * random.uniform(0.18, 0.45)
                self.patrol_target_x = self.HOME_X + math.cos(patrol_angle) * patrol_r
                self.patrol_target_y = self.HOME_Y + math.sin(patrol_angle) * patrol_r
                self.is_patrolling = True
                self.patrol_start_time = now
                self.patrol_stay_time = random.uniform(2.5, 4.5)

            if self.is_patrolling:
                dx = self.patrol_target_x - self.x
                dy = self.patrol_target_y - self.y
                dist = math.hypot(dx, dy)
                if dist > 2.0:
                    spd = 1.4
                    self.vx = (dx / dist) * spd
                    self.vy = (dy / dist) * spd
                    self.target_angle = math.atan2(dy, dx) + math.pi / 2
                    self.walk_phase += 0.18
                else:
                    self.vx = 0.0; self.vy = 0.0
                    if random.random() < 0.03:
                        self.target_angle += (random.random() - 0.5) * 0.2
                    if now - self.patrol_start_time > self.patrol_stay_time:
                        self.patrol_target_x = float(self.HOME_X)
                        self.patrol_target_y = float(self.HOME_Y)
                        if dist < 2.0 and abs(self.x - self.HOME_X) < 3.0:
                            self.is_patrolling = False
                            self.next_patrol_time = now + random.uniform(7.0, 15.0)
            else:
                self.vx = 0.0; self.vy = 0.0
                self.x = float(self.HOME_X)
                self.y = float(self.HOME_Y)
                if random.random() < 0.02:
                    self.target_angle += (random.random() - 0.5) * 0.20

# Auto-reweave disabled: spider remains comfortably in web

        # Friction
        if self.state not in ['ENTRANCE', 'WEAVING', 'RESTING', 'EATING', 'BUNGEE', 'CURIOUS']:
            self.vx *= 0.88
            self.vy *= 0.88

        # Terminal speed cap
        speed = math.hypot(self.vx, self.vy)
        max_speed = 13.0
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed
            speed = max_speed

        self.x += self.vx
        self.y += self.vy

        # Screen boundaries (Only active when not in entrance descent)
        if self.state != 'ENTRANCE':
            pad = 35
            min_x = self.screen_x + pad
            max_x = self.screen_x + self.screen_w - pad
            min_y = self.screen_y + pad
            max_y = self.screen_y + self.screen_h - pad

            if self.x < min_x: self.x = min_x; self.vx = abs(self.vx) * 0.7
            elif self.x > max_x: self.x = max_x; self.vx = -abs(self.vx) * 0.7
            if self.y < min_y: self.y = min_y; self.vy = abs(self.vy) * 0.7
            elif self.y > max_y: self.y = max_y; self.vy = -abs(self.vy) * 0.7

        diff_angle = self.target_angle - self.angle
        while diff_angle < -math.pi: diff_angle += math.pi * 2
        while diff_angle > math.pi: diff_angle -= math.pi * 2
        self.angle += diff_angle * 0.24

        if speed > 0.4 or self.state in ['ENTRANCE', 'EATING', 'CURIOUS']:
            self.walk_phase += (speed * 0.18) if speed > 0.4 else 0.20

        # RENDER ALL LAYERS
        self.draw_dewdrops(now)
        self.draw_insect()
        self.draw_spider(speed)
        self.draw_babies()
        self.draw_health_reminder()
        self.draw_onboarding_hint()
        self.update_screen_shake(now)

        # Periodically ensure topmost so newly opened tabs/apps never cover the spider
        if now - getattr(self, 'last_topmost_check', 0.0) > 1.2:
            self.ensure_topmost()
            self.last_topmost_check = now

        self.root.after(16, self.update_loop)

    def handle_entrance(self, now):
        """Authentic Google Flow Music entrance:
           Phase 1: 'DROP'      -> Drops fast & snappy ("dum kore") straight down to monitor vertical center.
           Phase 2: 'WIGGLE'    -> Suspended at center, wiggles legs playfully ("aktu nara cara kore") for 1.1s.
           Phase 3: 'REEL_SILK' -> Thread rapidly reels in from ceiling down into spider's tail ("dorita ses hoye jokhon spider er pisone ses hobe").
           Phase 4: 'DASH'      -> The instant thread finishes into spider, dashes fast to nest (HOME_X, HOME_Y) and weaves!"""
        top_x = self.get_entrance_top_x()
        monitor_center_y = float(self.screen_y + (self.screen_h / 2.0))
        target_drop_y = (float(self.screen_y + self.ENTRANCE_SILK_LENGTH)) if self.ENTRANCE_SILK_LENGTH is not None else monitor_center_y

        if self.entrance_phase == 'DROP':
            # Snappy fast drop ("dum kore akdom center e nambe")
            self.entrance_drop_speed = min(22.0, self.entrance_drop_speed + 2.0)
            self.x = top_x
            self.y += self.entrance_drop_speed
            self.target_angle = math.pi # Facing straight down
            self.walk_phase += 0.30

            # Tapered silk from ceiling to spider
            self.draw_entrance_silk(top_x, self.screen_y, self.y)

            if self.y >= target_drop_y:
                self.y = float(target_drop_y)
                self.entrance_phase = 'WIGGLE'
                self.entrance_wiggle_start = now
                self.silk_top_y = float(self.screen_y)
                if self.SOUND_ENABLED:
                    play_audio(550, 40, 750, 50)

        elif self.entrance_phase == 'WIGGLE':
            # Suspended in center of monitor, wiggling legs playfully ("aktu nara cara kore")
            self.x = top_x
            self.y = float(target_drop_y)
            self.vx = 0.0
            self.vy = 0.0

            # Silk remains attached while wiggling
            self.draw_entrance_silk(top_x, self.screen_y, self.y)

            elapsed_wiggle = now - self.entrance_wiggle_start
            self.target_angle = math.pi + math.sin(elapsed_wiggle * 5.5) * 0.20
            self.walk_phase += 0.35

            if elapsed_wiggle > 1.1:
                # Begin reeling the thread down into the spider's tail!
                self.entrance_phase = 'REEL_SILK'
                self.silk_top_y = float(self.screen_y)
                if self.SOUND_ENABLED:
                    play_audio(850, 35)

        elif self.entrance_phase == 'REEL_SILK':
            # Thread retracts rapidly from ceiling down towards spider's tail
            reel_speed = 28.0 # Fast snappy retraction
            self.silk_top_y += reel_speed
            self.x = top_x
            self.y = float(target_drop_y)
            self.walk_phase += 0.40

            if self.silk_top_y < self.y - 6.0:
                self.draw_entrance_silk(top_x, self.silk_top_y, self.y)
            else:
                # Thread has completely finished into spider's back!
                self.canvas.delete("entrance_silk")
                self.entrance_phase = 'DASH'
                if self.SOUND_ENABLED:
                    play_audio(950, 35, 1350, 60)

        elif self.entrance_phase == 'DASH':
            # Dashes quickly across to nest ("taratari nijer jaigai jabe")
            dist_home = math.hypot(self.HOME_X - self.x, self.HOME_Y - self.y)
            if dist_home > 7.0:
                ang = math.atan2(self.HOME_Y - self.y, self.HOME_X - self.x)
                dash_speed = 9.2 # Fast energetic scamper!
                self.vx = math.cos(ang) * dash_speed
                self.vy = math.sin(ang) * dash_speed
                self.target_angle = ang + math.pi / 2
                self.walk_phase += 0.48
            else:
                self.vx = 0.0
                self.vy = 0.0
                self.x = float(self.HOME_X)
                self.y = float(self.HOME_Y)
                # Arrived at nest! Start actively weaving the web step-by-step!
                self.state = 'WEAVING'
                self.weave_start_time = now
                self.web_built = False
                self.destroy_web()
                if self.SOUND_ENABLED:
                    play_audio(600, 30, 800, 40)

    def handle_bungee(self, now):
        """Spider bungee jumps with elastic spring physics and ultra-rapid return!"""
        elapsed = now - self.bungee_start_time
        self.canvas.delete("bungee_silk")
        self.canvas.create_line(self.HOME_X, self.HOME_Y, self.x, self.y,
                                fill=self.theme['web'], width=1.6, tags="bungee_silk")

        target_y = self.bungee_drop_target
        if elapsed < 1.6:
            # Dropping down with spring rebound: reaches bottom, bounces upward, and gently settles
            progress = min(1.0, elapsed / 1.0)
            bounce = -math.sin(elapsed * 9.0) * math.exp(-elapsed * 2.5) * 55.0
            self.y = self.HOME_Y + (target_y - self.HOME_Y) * progress + bounce
            self.x = self.HOME_X
            self.target_angle = math.pi # Facing down
            self.walk_phase += 0.35
        elif elapsed < 2.4:
            # Hanging gently at bottom, looking around
            self.y = target_y
            self.x = self.HOME_X
            self.target_angle = math.pi + math.sin(elapsed * 4.0) * 0.25
            self.walk_phase += 0.10
        else:
            # ULTRA-FAST RAPID RETURN BACK TO WEB!
            climb_speed = 18.0
            self.y -= climb_speed
            self.target_angle = 0.0 # Facing up
            self.walk_phase += 0.50
            if self.y <= self.HOME_Y + 8:
                self.y = self.HOME_Y
                self.x = self.HOME_X
                self.canvas.delete("bungee_silk")
                self.state = 'RESTING'
                self.last_bungee_time = now
                self.target_angle = math.radians(135)
                self.trigger_vibration(1.2)

    def hatch_eggs(self):
        """Cute baby spiders emerge from under the mother's abdomen (peter tolay) and playfully scatter!"""
        self.egg_state = 'CARRYING_BABIES'
        self.egg_birth_time = time.time()
        self.babies = []
        num_babies = 10
        s = self.spider_scale
        for i in range(num_babies):
            # Clustered safely under belly / on abdomen (peter tolay)
            ox = random.uniform(-2.8, 2.8) * s
            oy = random.uniform(3.5, 8.5) * s
            b = BabySpider(self, ox, oy)
            burst_angle = i * (2 * math.pi / num_babies) + random.uniform(-0.15, 0.15)
            burst_speed = random.uniform(4.5, 7.5)
            b.on_back = False
            b.vx = math.cos(burst_angle) * burst_speed
            b.vy = math.sin(burst_angle) * burst_speed
            b.scatter_timer = time.time() + random.uniform(3.0, 4.5)
            self.babies.append(b)

        self.trigger_vibration(1.2)
        if self.SOUND_ENABLED:
            play_audio(1100, 35, 1500, 45)

    def handle_eating(self, now):
        elapsed = now - self.eating_start_time
        total_time = self.EATING_DURATION

        if not self.insect:
            self.state = 'RETURNING'
            return

        bx, by = self.insect.x, self.insect.y
        ang_to_prey = math.atan2(by - self.y, bx - self.x)
        self.target_angle = ang_to_prey + math.pi / 2

        if elapsed < 1.8:
            wrap_progress = elapsed / 1.8
            self.canvas.delete("cocoon")
            r = 9.0 * wrap_progress
            self.canvas.create_oval(bx - r, by - r, bx + r, by + r,
                                    fill="", outline="#ffffff", width=1.5, tags="cocoon")
            for ang_off in [0.0, 0.7, 1.4, 2.1]:
                lx = math.cos(ang_off) * r
                ly = math.sin(ang_off) * r
                self.canvas.create_line(bx - lx, by - ly, bx + lx, by + ly,
                                        fill="#e2e8f0", width=1.0, tags="cocoon")
        elif elapsed < total_time - 0.6:
            feed_progress = (elapsed - 1.8) / (total_time - 2.4)
            self.insect.size_scale = max(0.08, 1.0 - feed_progress)
            remain_r = max(2.5, 9.0 * (1.0 - feed_progress * 0.8))
            self.canvas.delete("cocoon")
            self.canvas.create_oval(bx - remain_r, by - remain_r, bx + remain_r, by + remain_r,
                                    fill="", outline="#cbd5e1", width=1.0, tags="cocoon")
            if random.random() < 0.08 and self.SOUND_ENABLED:
                play_audio(360, 25)
        else:
            self.canvas.delete("cocoon")
            self.canvas.delete("insect")
            self.insect = None
            self.last_bug_spawn_time = now
            self.state = 'RETURNING'

    def handle_weaving(self, now):
        """Authentic, visually captivating web weaving: Radial spokes shoot outwards,
        then spider scampers in fluid concentric spirals laying curved catenary arcs and dewdrops,
        finally returning to center hub. 100% CONTINUOUS MOTION - ZERO SUDDEN JUMPS!"""
        elapsed = now - getattr(self, 'weave_start_time', now)
        spoke_dur = max(1.0, getattr(self, 'SPOKE_DURATION', 4.5))
        ring_dur = max(2.0, getattr(self, 'RING_WEAVE_DURATION', 10.0))
        return_dur = 1.2
        TOTAL_WEAVE_TIME = spoke_dur + ring_dur + return_dur

        # Watchdog: if weaving runs over TOTAL_WEAVE_TIME + 1.2s, cleanly finalize
        if elapsed > TOTAL_WEAVE_TIME + 1.2:
            self.redraw_full_web()
            self.state = 'RESTING'
            self.target_angle = math.radians(135)
            return

        self.canvas.delete("web")
        self.canvas.delete("active_thread")
        self.canvas.delete("dewdrop")
        self.canvas.delete("hub")
        self.recompute_web_geometry()

        spoke_w = max(1.6, self.web_thickness * 1.15)
        ring_w = max(1.2, self.web_thickness * 0.95)

        STAGE1_TIME = spoke_dur
        STAGE2_TIME = spoke_dur + ring_dur

        # 1. SPOKES CREATION (OUT & IN CONTINUOUS NATURAL MARCH - ZERO TELEPORTS!)
        if elapsed < STAGE1_TIME:
            p = max(0.0, min(1.0, elapsed / STAGE1_TIME))
            total_spokes = self.num_spokes
            current_cycle = p * total_spokes
            spoke_idx = min(total_spokes - 1, int(current_cycle))
            cycle_frac = current_cycle - spoke_idx

            # Draw already completed spokes
            for s_i in range(spoke_idx):
                px, py = self.spoke_points[s_i]
                self.canvas.create_line(self.HOME_X, self.HOME_Y, px, py,
                                        fill=self.theme['web'], width=spoke_w, tags="web")

            target_px, target_py = self.spoke_points[spoke_idx]

            # 0.0 to 0.5: Spider walks OUTWARD from Center Hub to Rim laying the thread
            # 0.5 to 1.0: Spider walks INWARD from Rim back to Center Hub along the anchored spoke
            if cycle_frac < 0.5:
                out_p = cycle_frac * 2.0
                tip_x = self.HOME_X + (target_px - self.HOME_X) * out_p
                tip_y = self.HOME_Y + (target_py - self.HOME_Y) * out_p
                self.canvas.create_line(self.HOME_X, self.HOME_Y, tip_x, tip_y,
                                        fill=self.theme['web'], width=spoke_w, tags="web")
                self.x = tip_x
                self.y = tip_y
                self.target_angle = self.spoke_angles[spoke_idx] + math.pi / 2
            else:
                in_p = (cycle_frac - 0.5) * 2.0
                self.canvas.create_line(self.HOME_X, self.HOME_Y, target_px, target_py,
                                        fill=self.theme['web'], width=spoke_w, tags="web")
                self.x = target_px + (self.HOME_X - target_px) * in_p
                self.y = target_py + (self.HOME_Y - target_py) * in_p
                self.target_angle = self.spoke_angles[spoke_idx] - math.pi / 2

            self.walk_phase += 0.45
            if self.SOUND_ENABLED and int(cycle_frac * 10) == 0:
                play_audio(520 + spoke_idx * 35, 12)

        # 2. CONCENTRIC CURVED RINGS & DEWDROPS (SEAMLESS CONTINUOUS PATH)
        elif elapsed < STAGE2_TIME:
            # All 12 radial spokes are now fully anchored
            for px, py in self.spoke_points:
                self.canvas.create_line(self.HOME_X, self.HOME_Y, px, py,
                                        fill=self.theme['web'], width=spoke_w, tags="web")

            ring_t = max(0.0, min(1.0, (elapsed - STAGE1_TIME) / (STAGE2_TIME - STAGE1_TIME)))
            num_rings = len(self.ring_ratios)
            # Each ring consists of 1 spoke step + 12 arcs
            units_per_ring = self.num_spokes + 1
            total_units = num_rings * units_per_ring
            cur_unit = ring_t * total_units

            cur_ring_idx = min(num_rings - 1, int(cur_unit // units_per_ring))
            unit_in_ring = cur_unit - cur_ring_idx * units_per_ring

            # Draw all previously completed rings
            for r_k in range(cur_ring_idx):
                R_k = self.WEB_RADIUS * self.ring_ratios[r_k]
                for s_i in range(self.num_spokes):
                    s_next = (s_i + 1) % self.num_spokes
                    a1 = self.spoke_angles[s_i]
                    a2 = self.spoke_angles[s_next]
                    diff = a2 - a1
                    if diff < 0: diff += 2 * math.pi
                    a_mid = a1 + diff / 2.0
                    is_outer_ring = (r_k == len(self.ring_ratios) - 1)
                    droop = 0.88
                    p1 = (self.HOME_X + math.cos(a1) * R_k, self.HOME_Y + math.sin(a1) * R_k)
                    p_mid = (self.HOME_X + math.cos(a_mid) * (R_k * droop), self.HOME_Y + math.sin(a_mid) * (R_k * droop))
                    p2 = (self.HOME_X + math.cos(a2) * R_k, self.HOME_Y + math.sin(a2) * R_k)
                    self.canvas.create_line(p1[0], p1[1], p_mid[0], p_mid[1], p2[0], p2[1],
                                            smooth=True, fill=self.theme['web'], width=ring_w, tags="web")
                    dew_r = max(1.6, self.web_thickness * 0.9)
                    self.canvas.create_oval(p1[0] - dew_r, p1[1] - dew_r, p1[0] + dew_r, p1[1] + dew_r,
                                            fill=self.theme['dewdrop'], outline="#ffffff", width=0.5, tags="dewdrop")

            # Active ring processing
            R_prev = 0.0 if cur_ring_idx == 0 else self.WEB_RADIUS * self.ring_ratios[cur_ring_idx - 1]
            R_cur = self.WEB_RADIUS * self.ring_ratios[cur_ring_idx]
            a0 = self.spoke_angles[0]

            if unit_in_ring < 1.0:
                # Spider walks smoothly along spoke 0 from R_prev to R_cur
                step_p = unit_in_ring
                r = R_prev + (R_cur - R_prev) * step_p
                self.x = self.HOME_X + math.cos(a0) * r
                self.y = self.HOME_Y + math.sin(a0) * r
                self.target_angle = a0 + math.pi / 2
                self.walk_phase += 0.40
            else:
                # Weave the 12 arcs of the active ring
                active_arcs_done = min(self.num_spokes, int(unit_in_ring - 1.0))
                arc_frac = (unit_in_ring - 1.0) - active_arcs_done

                # Draw completed arcs of this ring
                for s_i in range(active_arcs_done):
                    s_next = (s_i + 1) % self.num_spokes
                    a1 = self.spoke_angles[s_i]
                    a2 = self.spoke_angles[s_next]
                    diff = a2 - a1
                    if diff < 0: diff += 2 * math.pi
                    a_mid = a1 + diff / 2.0
                    is_outer_ring = (cur_ring_idx == len(self.ring_ratios) - 1)
                    droop = 0.88
                    p1 = (self.HOME_X + math.cos(a1) * R_cur, self.HOME_Y + math.sin(a1) * R_cur)
                    p_mid = (self.HOME_X + math.cos(a_mid) * (R_cur * droop), self.HOME_Y + math.sin(a_mid) * (R_cur * droop))
                    p2 = (self.HOME_X + math.cos(a2) * R_cur, self.HOME_Y + math.sin(a2) * R_cur)
                    self.canvas.create_line(p1[0], p1[1], p_mid[0], p_mid[1], p2[0], p2[1],
                                            smooth=True, fill=self.theme['web'], width=ring_w, tags="web")
                    dew_r = max(1.6, self.web_thickness * 0.9)
                    self.canvas.create_oval(p1[0] - dew_r, p1[1] - dew_r, p1[0] + dew_r, p1[1] + dew_r,
                                            fill=self.theme['dewdrop'], outline="#ffffff", width=0.5, tags="dewdrop")

                # Active arc being woven
                if active_arcs_done < self.num_spokes:
                    s_next = (active_arcs_done + 1) % self.num_spokes
                    a1 = self.spoke_angles[active_arcs_done]
                    a2 = self.spoke_angles[s_next]
                    diff = a2 - a1
                    if diff < 0: diff += 2 * math.pi
                    a_mid = a1 + diff / 2.0
                    is_outer_ring = (cur_ring_idx == len(self.ring_ratios) - 1)
                    droop = 0.88
                    p1 = (self.HOME_X + math.cos(a1) * R_cur, self.HOME_Y + math.sin(a1) * R_cur)
                    p_mid = (self.HOME_X + math.cos(a_mid) * (R_cur * droop), self.HOME_Y + math.sin(a_mid) * (R_cur * droop))
                    p2 = (self.HOME_X + math.cos(a2) * R_cur, self.HOME_Y + math.sin(a2) * R_cur)

                    one_t = 1.0 - arc_frac
                    sx = one_t*one_t * p1[0] + 2*one_t*arc_frac * p_mid[0] + arc_frac*arc_frac * p2[0]
                    sy = one_t*one_t * p1[1] + 2*one_t*arc_frac * p_mid[1] + arc_frac*arc_frac * p2[1]

                    self.canvas.create_line(p1[0], p1[1], sx, sy,
                                            smooth=True, fill=self.theme['web'], width=ring_w, tags="active_thread")
                    self.x = sx
                    self.y = sy
                    self.target_angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0]) + math.pi / 2
                    self.walk_phase += 0.48
                else:
                    self.x = self.HOME_X + math.cos(a0) * R_cur
                    self.y = self.HOME_Y + math.sin(a0) * R_cur

                if self.SOUND_ENABLED and int(arc_frac * 10) == 0:
                    play_audio(620 + cur_ring_idx * 50, 14)

        # 3. RETURN DOWN TO CENTER HUB (ALONG SPOKE 0)
        elif elapsed < TOTAL_WEAVE_TIME:
            for px, py in self.spoke_points:
                self.canvas.create_line(self.HOME_X, self.HOME_Y, px, py,
                                        fill=self.theme['web'], width=spoke_w, tags="web")
            for r_ratio in self.ring_ratios:
                R = self.WEB_RADIUS * r_ratio
                for i in range(self.num_spokes):
                    i_next = (i + 1) % self.num_spokes
                    a1 = self.spoke_angles[i]
                    a2 = self.spoke_angles[i_next]
                    diff = a2 - a1
                    if diff < 0: diff += 2 * math.pi
                    a_mid = a1 + diff / 2.0
                    droop = 0.88
                    p1 = (self.HOME_X + math.cos(a1) * R, self.HOME_Y + math.sin(a1) * R)
                    p_mid = (self.HOME_X + math.cos(a_mid) * (R * droop), self.HOME_Y + math.sin(a_mid) * (R * droop))
                    p2 = (self.HOME_X + math.cos(a2) * R, self.HOME_Y + math.sin(a2) * R)
                    self.canvas.create_line(p1[0], p1[1], p_mid[0], p_mid[1], p2[0], p2[1],
                                            smooth=True, fill=self.theme['web'], width=ring_w, tags="web")
                    dew_r = max(1.6, self.web_thickness * 0.9)
                    self.canvas.create_oval(p1[0] - dew_r, p1[1] - dew_r, p1[0] + dew_r, p1[1] + dew_r,
                                            fill=self.theme['dewdrop'], outline="#ffffff", width=0.5, tags="dewdrop")

            ret_p = max(0.0, min(1.0, (elapsed - STAGE2_TIME) / return_dur))
            R_last = self.WEB_RADIUS * self.ring_ratios[-1]
            a0 = self.spoke_angles[0]
            p_last = (self.HOME_X + math.cos(a0) * R_last, self.HOME_Y + math.sin(a0) * R_last)
            self.x = p_last[0] + (self.HOME_X - p_last[0]) * ret_p
            self.y = p_last[1] + (self.HOME_Y - p_last[1]) * ret_p
            self.target_angle = a0 - math.pi / 2
            self.walk_phase += 0.40
        else:
            self.redraw_full_web()
            self.state = 'RESTING'
            self.target_angle = math.radians(135)

    def draw_dewdrops(self, now):
        """Draws glistening dewdrops on web intersections with subtle twinkling sparkle."""
        self.canvas.delete("dewdrop")
        if not self.web_built:
            return

        vib_off = math.sin(self.vibration_phase) * (self.web_vibration * 3.5)

        for ring_idx, r_ratio in enumerate(self.ring_ratios):
            R = self.WEB_RADIUS * r_ratio
            for s_idx, a in enumerate(self.spoke_angles):
                dx = math.cos(a) * R
                dy = math.sin(a) * R + vib_off * (r_ratio)
                cx = self.HOME_X + dx
                cy = self.HOME_Y + dy

                twinkle = math.sin(now * 3.0 + s_idx + ring_idx)
                r = 1.6 + (0.5 if twinkle > 0.7 else 0.0)

                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                        fill=self.theme['dewdrop'], outline="#ffffff", width=0.6, tags="dewdrop")

    def draw_health_reminder(self):
        """Draws a sleek, modern floating translucent cyber health reminder card with rotating tips."""
        self.canvas.delete("reminder")
        if not self.reminder_active:
            return

        now = time.time()
        if now > self.reminder_end_time:
            self.reminder_active = False
            return

        bx = self.HOME_X
        by = self.HOME_Y + self.WEB_RADIUS + 46

        # Hanging silk thread from web down to the card
        spoke_w = max(1.2, self.web_thickness * 0.85)
        self.canvas.create_line(self.HOME_X, self.HOME_Y + self.WEB_RADIUS, bx, by - 26,
                                fill=self.theme['web'], width=spoke_w, tags="reminder")
        # Dewdrop connecting thread to card
        self.canvas.create_oval(bx - 2, by - 26 - 2, bx + 2, by - 26 + 2,
                                fill=self.theme['dewdrop'], outline="#ffffff", width=0.5, tags="reminder")

        # Rotating health tips list (Title Key, Body Key, Fallback Title, Fallback Body)
        reminders_data = [
            ("reminder_water_title", "reminder_water_body", "💧 HYDRATION BREAK", "Time to hydrate! Drink a fresh glass of water."),
            ("reminder_eye_title", "reminder_eye_body", "👁 20-20-20 EYE CARE", "Look 20 feet away for 20 seconds to rest your eyes!"),
            ("reminder_stretch_title", "reminder_stretch_body", "🧘 POSTURE & STRETCH", "Straighten your back and gently roll your shoulders."),
            ("reminder_breathe_title", "reminder_breathe_body", "🌬 DEEP BREATHING", "Take 3 slow deep breaths to recharge your focus.")
        ]

        idx = getattr(self, 'reminder_idx', 0) % len(reminders_data)
        k_title, k_body, def_title, def_body = reminders_data[idx]

        title_text = self.i18n.t(k_title, def_title)
        body_text = self.i18n.t(k_body, def_body)

        # Floating Pill Card with Cyber Glow
        w, h = 215, 25
        # Soft Outer Glow matching dewdrop theme
        self.canvas.create_rectangle(bx - w - 2, by - h - 2, bx + w + 2, by + h + 2,
                                     fill="", outline=self.theme['dewdrop'], width=1.0, tags="reminder")
        # Main Dark Glass Card
        self.canvas.create_rectangle(bx - w, by - h, bx + w, by + h,
                                     fill="#090d16", outline=self.theme['hub'], width=1.8, tags="reminder")

        # Header Title (Theme Cyan Accent)
        self.canvas.create_text(bx, by - 10, text=f"✨ {title_text} ✨",
                                fill="#38bdf8", font=("Segoe UI", 9, "bold"), tags="reminder")
        # Body Description (Crisp White Text)
        self.canvas.create_text(bx, by + 9, text=body_text,
                                fill="#f8fafc", font=("Segoe UI", 9), tags="reminder")

    def dismiss_onboarding(self):
        """Dismisses the floating onboarding or update banner immediately."""
        self.onboarding_active = False
        self.canvas.delete("onboarding")

    def draw_onboarding_hint(self):
        """Draws a sleek floating cyber onboarding or update banner with hotkeys and guidance."""
        self.canvas.delete("onboarding")
        if not self.onboarding_active:
            return

        now = time.time()
        if now > self.onboarding_end_time:
            self.onboarding_active = False
            return

        primary_w = self.root.winfo_screenwidth() or 1440
        cx = primary_w // 2
        cy = 95

        card_w = 340
        card_h = 46

        # Soft glowing outer halo
        self.canvas.create_rectangle(cx - card_w - 2, cy - card_h - 2, cx + card_w + 2, cy + card_h + 2,
                                     fill="", outline=self.theme.get('dewdrop', '#38bdf8'), width=1.0, tags="onboarding")
        # Dark Cyber Glass Card
        self.canvas.create_rectangle(cx - card_w, cy - card_h, cx + card_w, cy + card_h,
                                     fill="#090d16", outline=self.theme.get('hub', '#00f5d4'), width=2.0, tags="onboarding")

        hk = self.config.get("HOTKEYS", {})
        hk_p = hk.get("SETTINGS", "Shift+P")
        hk_f = hk.get("BUG", "Shift+F")
        hk_b = hk.get("BUNGEE", "Shift+B")

        if self.onboarding_type == "FIRST_RUN":
            title = self.i18n.t("hint_welcome_title", "✨ WELCOME TO DESKTOP FLOATING SPIDER ✨")
            raw_l1 = self.i18n.t("hint_welcome_line1", "🎮 Quick Keys: [{SETTINGS}] Settings  |  [{BUG}] Drop Prey  |  [{BUNGEE}] Bungee Jump")
            line1 = raw_l1.replace("{SETTINGS}", hk_p).replace("{BUG}", hk_f).replace("{BUNGEE}", hk_b)
            line2 = self.i18n.t("hint_welcome_line2", "📍 System Tray (near clock) for Quick Menu & Exit | 🖱️ Drag pet freely!")
        else:
            raw_title = self.i18n.t("hint_update_title", f"🚀 UPDATED TO DESKTOP FLOATING v{APP_VERSION} ✨")
            title = raw_title.replace("{VERSION}", APP_VERSION)
            line1 = self.i18n.t("hint_update_line1", "💎 Cyan Cyber Spider Icon & Clean Taskbar (Tray 24/7)")
            line2 = self.i18n.t("hint_update_line2", "⚡ Standalone Portable .exe, Pip Ready & MB Live Updater!")

        dismiss_text = self.i18n.t("hint_dismiss", "[Click on card to close]")

        self.canvas.create_text(cx, cy - 25, text=title,
                                fill="#38bdf8", font=("Segoe UI", 10, "bold"), tags="onboarding")
        self.canvas.create_text(cx, cy - 6, text=line1,
                                fill="#f8fafc", font=("Segoe UI", 9), tags="onboarding")
        self.canvas.create_text(cx, cy + 13, text=line2,
                                fill="#94a3b8", font=("Segoe UI", 8), tags="onboarding")
        self.canvas.create_text(cx, cy + 30, text=dismiss_text,
                                fill="#64748b", font=("Segoe UI", 7), tags="onboarding")

        self.canvas.tag_bind("onboarding", "<Button-1>", lambda e: self.dismiss_onboarding())

    def draw_babies(self):
        self.canvas.delete("baby")
        if self.egg_state != 'CARRYING_BABIES':
            return

        for b in self.babies:
            if b.on_back:
                # Clustered safely under belly / on mother's abdomen (peter tolay)
                self.canvas.create_oval(b.x - 1.5, b.y - 1.5, b.x + 1.5, b.y + 1.5,
                                        fill="#e2e8f0", outline="#1e293b", width=0.5, tags="baby")
            else:
                bx, by = b.x, b.y
                w = math.sin(b.walk_phase) * 2.2
                self.canvas.create_line(bx - 3, by - 2, bx - 6, by - 4 + w, fill=self.theme['legs'], width=0.8, tags="baby")
                self.canvas.create_line(bx + 3, by - 2, bx + 6, by - 4 - w, fill=self.theme['legs'], width=0.8, tags="baby")
                self.canvas.create_line(bx - 3, by + 2, bx - 6, by + 4 - w, fill=self.theme['legs'], width=0.8, tags="baby")
                self.canvas.create_line(bx + 3, by + 2, bx + 6, by + 4 + w, fill=self.theme['legs'], width=0.8, tags="baby")
                self.canvas.create_oval(bx - 2.0, by - 2.0, bx + 2.0, by + 2.0,
                                        fill="#f8fafc", outline="#38bdf8", width=0.6, tags="baby")

    def draw_insect(self):
        """Draws authentic Mosquito, Realistic Morpho Butterfly, or Glowing Firefly!"""
        self.canvas.delete("insect")
        if not self.insect:
            return

        now = time.time()
        bx, by = self.insect.x, self.insect.y
        ang = self.insect.angle
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        s = self.insect.size_scale

        def rot(lx, ly):
            return bx + (lx * cos_a - ly * sin_a) * s, by + (lx * sin_a + ly * cos_a) * s

        itype = self.insect.type

        # =========================================================================
        # 1. REALISTIC BUTTERFLY (প্রজাপতি - Double Lobed Wings with Veins & Flapping)
        # =========================================================================
        if itype == Insect.TYPE_BUTTERFLY:
            # 3D folding perspective flap
            flap_compress = abs(math.cos(self.insect.wing_phase)) * 0.75 + 0.25
            span_fw = 18.0 * flap_compress
            span_hw = 13.0 * flap_compress

            # Forewings (Large curved upper wings)
            fw_left = [
                rot(-1.5, -2),
                rot(-span_fw * 0.5, -12),
                rot(-span_fw, -10),
                rot(-span_fw * 0.95, -2),
                rot(-span_fw * 0.6, 2),
                rot(-1.5, 1)
            ]
            fw_right = [
                rot(1.5, -2),
                rot(span_fw * 0.5, -12),
                rot(span_fw, -10),
                rot(span_fw * 0.95, -2),
                rot(span_fw * 0.6, 2),
                rot(1.5, 1)
            ]

            # Hindwings (Scalloped lower wings)
            hw_left = [
                rot(-1.5, 0),
                rot(-span_hw, 2),
                rot(-span_hw * 0.9, 9),
                rot(-span_hw * 0.5, 12),
                rot(-1.5, 6)
            ]
            hw_right = [
                rot(1.5, 0),
                rot(span_hw, 2),
                rot(span_hw * 0.9, 9),
                rot(span_hw * 0.5, 12),
                rot(1.5, 6)
            ]

            # Render Wings: Rich cyan-sapphire Morpho colors with dark borders
            self.canvas.create_polygon(hw_left, fill="#0284c7", outline="#0f172a", width=1.0, tags="insect")
            self.canvas.create_polygon(hw_right, fill="#0284c7", outline="#0f172a", width=1.0, tags="insect")
            self.canvas.create_polygon(fw_left, fill="#06b6d4", outline="#0f172a", width=1.2, tags="insect")
            self.canvas.create_polygon(fw_right, fill="#06b6d4", outline="#0f172a", width=1.2, tags="insect")

            # Wing vein details
            v1_l, v1_r = rot(-span_fw * 0.7, -6), rot(span_fw * 0.7, -6)
            v_base = rot(0, -1)
            self.canvas.create_line(v_base[0], v_base[1], v1_l[0], v1_l[1], fill="#083344", width=0.8, tags="insect")
            self.canvas.create_line(v_base[0], v_base[1], v1_r[0], v1_r[1], fill="#083344", width=0.8, tags="insect")

            # Slender Butterfly Body
            b_head = rot(0, -7.5)
            b_th_top = rot(0, -5.0)
            b_tail = rot(0, 7.5)
            # Abdomen
            self.canvas.create_line(b_th_top[0], b_th_top[1], b_tail[0], b_tail[1], fill="#1e293b", width=2.2*s, tags="insect")
            # Thorax
            self.canvas.create_oval(b_th_top[0]-2*s, b_th_top[1]-2*s, b_th_top[0]+2*s, b_th_top[1]+2*s,
                                    fill="#0f172a", outline="", tags="insect")
            # Head with eyes
            self.canvas.create_oval(b_head[0]-1.6*s, b_head[1]-1.6*s, b_head[0]+1.6*s, b_head[1]+1.6*s,
                                    fill="#020617", outline="", tags="insect")

            # Antennae with delicate round tips
            ant_l = rot(-5, -13)
            ant_r = rot(5, -13)
            self.canvas.create_line(b_head[0], b_head[1], ant_l[0], ant_l[1], fill="#0f172a", width=0.8, tags="insect")
            self.canvas.create_line(b_head[0], b_head[1], ant_r[0], ant_r[1], fill="#0f172a", width=0.8, tags="insect")
            self.canvas.create_oval(ant_l[0]-1, ant_l[1]-1, ant_l[0]+1, ant_l[1]+1, fill="#0f172a", outline="", tags="insect")
            self.canvas.create_oval(ant_r[0]-1, ant_r[1]-1, ant_r[0]+1, ant_r[1]+1, fill="#0f172a", outline="", tags="insect")

        # =========================================================================
        # 2. REALISTIC GLOWING FIREFLY (জোনাকি পোকা - Lampyrid Beetle & Multi-Layer Aura)
        # =========================================================================
        elif itype == Insect.TYPE_FIREFLY:
            # Beetle Elytra (split wing covers in flight)
            wing_spread = 3.5 if not self.insect.trapped else 5.0
            el_tip_l = rot(-5 - wing_spread, 7)
            el_tip_r = rot(5 + wing_spread, 7)
            el_base = rot(0, -2)

            # Translucent flight wings underneath
            fw_flap = math.sin(self.insect.wing_phase * 2.0) * 4.0
            tw_l = rot(-9, 4 + fw_flap)
            tw_r = rot(9, 4 - fw_flap)
            self.canvas.create_line(el_base[0], el_base[1], tw_l[0], tw_l[1], fill="#cbd5e1", width=1.5*s, tags="insect")
            self.canvas.create_line(el_base[0], el_base[1], tw_r[0], tw_r[1], fill="#cbd5e1", width=1.5*s, tags="insect")

            # Hardened dark elytra covers
            self.canvas.create_line(el_base[0], el_base[1], el_tip_l[0], el_tip_l[1], fill="#292524", width=2.4*s, tags="insect")
            self.canvas.create_line(el_base[0], el_base[1], el_tip_r[0], el_tip_r[1], fill="#292524", width=2.4*s, tags="insect")

            # Pronotum (Characteristic shield-shaped reddish hood covering head)
            pron_top = rot(0, -5.5)
            self.canvas.create_oval(pron_top[0]-3.2*s, pron_top[1]-3.0*s, pron_top[0]+3.2*s, pron_top[1]+3.0*s,
                                    fill="#ea580c", outline="#7c2d12", width=0.8, tags="insect")
            # Pronotum central dark spot
            self.canvas.create_oval(pron_top[0]-1.2*s, pron_top[1]-1.2*s, pron_top[0]+1.2*s, pron_top[1]+1.2*s,
                                    fill="#1c1917", outline="", tags="insect")

            # Slender antennae
            ant_l = rot(-4, -11)
            ant_r = rot(4, -11)
            self.canvas.create_line(pron_top[0], pron_top[1], ant_l[0], ant_l[1], fill="#44403c", width=0.8, tags="insect")
            self.canvas.create_line(pron_top[0], pron_top[1], ant_r[0], ant_r[1], fill="#44403c", width=0.8, tags="insect")

            # Beetle legs
            for side in [-1, 1]:
                l_base = rot(side * 2, -1)
                l_tip = rot(side * 6, 1)
                self.canvas.create_line(l_base[0], l_base[1], l_tip[0], l_tip[1], fill="#57534e", width=0.8, tags="insect")

            # Bioluminescent Lantern (Abdominal photic organ with organic pulsing glow!)
            p_lantern = rot(0, 5)
            # Organic breath pulse: quick bright flash, gradual fade
            raw_glow = (math.sin(now * 3.8))
            glow_intensity = max(0.15, raw_glow * raw_glow)

            # Layer 1: Ambient outer soft aura
            r_aura = (9.0 + glow_intensity * 5.0) * s
            self.canvas.create_oval(p_lantern[0]-r_aura, p_lantern[1]-r_aura, p_lantern[0]+r_aura, p_lantern[1]+r_aura,
                                    fill="", outline="#bef264", width=1.0, tags="insect")

            # Layer 2: Glowing chartreuse lantern bulb
            r_bulb = (4.0 + glow_intensity * 2.0) * s
            self.canvas.create_oval(p_lantern[0]-r_bulb, p_lantern[1]-r_bulb, p_lantern[0]+r_bulb, p_lantern[1]+r_bulb,
                                    fill="#a3e635", outline="#d9f99d", width=1.0, tags="insect")

            # Layer 3: Hot white-yellow focal core
            r_core = max(1.2, 2.2 * glow_intensity * s)
            self.canvas.create_oval(p_lantern[0]-r_core, p_lantern[1]-r_core, p_lantern[0]+r_core, p_lantern[1]+r_core,
                                    fill="#fef08a", outline="", tags="insect")

        # =========================================================================
        # 3. REALISTIC MOSQUITO (মশা - 6 Spindly Jointed Legs, Thorax & Proboscis)
        # =========================================================================
        else:
            leg_defs = [
                (-1, -4, -12, -18, -14), ( 1, -4,  12,  18, -14),
                (-1,  0, -14, -20,   0), ( 1,  0,  14,  20,   0),
                (-1,  4, -12, -18,  14), ( 1,  4,  12,  18,  14),
            ]
            leg_wiggle = math.sin(self.insect.wing_phase * 0.7) * (2.5 if self.insect.trapped else 0.8)
            for side, y_off, jx, fx, fy in leg_defs:
                w_root = rot(side * 2, y_off)
                w_knee = rot(jx + (leg_wiggle * side), y_off - 4)
                w_foot = rot(fx, fy + leg_wiggle)
                self.canvas.create_line(w_root[0], w_root[1], w_knee[0], w_knee[1], fill="#718096", width=1.0, tags="insect")
                self.canvas.create_line(w_knee[0], w_knee[1], w_foot[0], w_foot[1], fill="#a0aec0", width=0.8, tags="insect")

            # Abdomen
            p_tail_top = rot(0, 1)
            p_tail_end = rot(0, 11)
            self.canvas.create_line(p_tail_top[0], p_tail_top[1], p_tail_end[0], p_tail_end[1],
                                    fill="#4a5568", width=max(1.0, 2.5 * s), tags="insect")
            # Thorax
            p_th_top = rot(-2, -3)
            p_th_bot = rot(2, 1)
            self.canvas.create_oval(p_th_top[0], p_th_top[1], p_th_bot[0], p_th_bot[1],
                                    fill="#2d3748", outline="#718096", width=0.8, tags="insect")
            # Head
            p_h_top = rot(-1.5, -6)
            p_h_bot = rot(1.5, -3)
            self.canvas.create_oval(p_h_top[0], p_h_top[1], p_h_bot[0], p_h_bot[1], fill="#1a202c", outline="", tags="insect")
            # Sharp piercing proboscis needle
            p_needle_base = rot(0, -6)
            p_needle_tip = rot(0, -12)
            self.canvas.create_line(p_needle_base[0], p_needle_base[1], p_needle_tip[0], p_needle_tip[1],
                                    fill="#e2e8f0", width=1.0, tags="insect")
            # Red eyes
            e1 = rot(-1.2, -5.2); e2 = rot(1.2, -5.2)
            self.canvas.create_oval(e1[0]-0.8*s, e1[1]-0.8*s, e1[0]+0.8*s, e1[1]+0.8*s, fill="#ef4444", outline="", tags="insect")
            self.canvas.create_oval(e2[0]-0.8*s, e2[1]-0.8*s, e2[0]+0.8*s, e2[1]+0.8*s, fill="#ef4444", outline="", tags="insect")
            # Clear vibrating wings
            wing_flap = math.sin(self.insect.wing_phase) * 6.0
            w1_tip = rot(-10, -1 + wing_flap); w2_tip = rot(10, -1 - wing_flap); w_base = rot(0, -2)
            self.canvas.create_line(w_base[0], w_base[1], w1_tip[0], w1_tip[1], fill="#e0f2fe", width=max(1.0, 1.8 * s), tags="insect")
            self.canvas.create_line(w_base[0], w_base[1], w2_tip[0], w2_tip[1], fill="#e0f2fe", width=max(1.0, 1.8 * s), tags="insect")

    def draw_spider(self, speed):
        """Draws realistic spider with active anatomical model, 3D Drop Shadow, and custom markings!"""
        self.canvas.delete("spider")

        now = time.time()
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)

        m = SPIDER_MODELS[self.model_idx]
        s = self.spider_scale

        # Furious shiver tremor during CURIOUS 'SHIVER' or lunging during 'SHOVE_1'/'SHOVE_2'
        tremor_x = 0.0
        tremor_y = 0.0
        if self.state == 'CURIOUS':
            if self.curious_phase == 'SHIVER':
                tremor_x = (random.random() - 0.5) * 4.5
                tremor_y = (random.random() - 0.5) * 4.5
            elif self.curious_phase in ['SHOVE_1', 'SHOVE_2']:
                lunge = math.sin((now - self.curious_phase_start) * 14.0) * 6.0
                tremor_x = math.sin(self.angle) * lunge
                tremor_y = -math.cos(self.angle) * lunge

        def transform(lx, ly, off_x=0, off_y=0):
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            return self.x + rx + off_x + tremor_x, self.y + ry + off_y + tremor_y

        leg_configs = [
            (-1, 0, -50, 16.0 * m['leg_l1_scale'] * s, 18.0 * m['leg_l2_scale'] * s),
            ( 1, 0,  50, 16.0 * m['leg_l1_scale'] * s, 18.0 * m['leg_l2_scale'] * s),
            (-1, 1, -85, 14.0 * m['leg_l1_scale'] * s, 16.0 * m['leg_l2_scale'] * s),
            ( 1, 1,  85, 14.0 * m['leg_l1_scale'] * s, 16.0 * m['leg_l2_scale'] * s),
            (-1, 2, -115, 15.0 * m['leg_l1_scale'] * s, 17.0 * m['leg_l2_scale'] * s),
            ( 1, 2,  115, 15.0 * m['leg_l1_scale'] * s, 17.0 * m['leg_l2_scale'] * s),
            (-1, 3, -150, 18.0 * m['leg_l1_scale'] * s, 20.0 * m['leg_l2_scale'] * s),
            ( 1, 3,  150, 18.0 * m['leg_l1_scale'] * s, 20.0 * m['leg_l2_scale'] * s),
        ]

        # === LAYER 1: 3D SOFT DROP SHADOW ===
        SHADOW_OFF_X = 4.0 * s
        SHADOW_OFF_Y = 5.0 * s
        SHADOW_COL = "#05070a"

        # Abdomen Shadow
        ab_shadow = []
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            lx = math.cos(rad) * m['ab_rx'] * s
            ly = (8.0 * s) + math.sin(rad) * m['ab_ry'] * s
            ab_shadow.extend(transform(lx, ly, SHADOW_OFF_X, SHADOW_OFF_Y))
        self.canvas.create_polygon(ab_shadow, fill=SHADOW_COL, outline="", tags="spider")

        # Thorax Shadow
        th_shadow = []
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            lx = math.cos(rad) * m['th_rx'] * s
            ly = (-2.5 * s) + math.sin(rad) * m['th_ry'] * s
            th_shadow.extend(transform(lx, ly, SHADOW_OFF_X, SHADOW_OFF_Y))
        self.canvas.create_polygon(th_shadow, fill=SHADOW_COL, outline="", tags="spider")

        # === LAYER 2: 8 JOINTED LEGS ===
        for side, idx, base_deg, l1, l2 in leg_configs:
            osc = math.sin(self.walk_phase + idx * 1.5 + (0 if side == 1 else math.pi))
            wiggle = (osc * 16.0) if (speed > 0.4 or self.state in ['ENTRANCE', 'EATING', 'CURIOUS']) else 0.0

            # In Entrance WIGGLE / REEL phase, all legs wave playfully in alternating rhythms!
            if self.state == 'ENTRANCE' and self.entrance_phase in ['WIGGLE', 'REEL_SILK']:
                wiggle_t = now - getattr(self, 'entrance_wiggle_start', now)
                wave = math.sin(wiggle_t * 14.0 + idx * 1.4 + (0 if side == 1 else math.pi * 0.6)) * 26.0
                cur_angle_rad = math.radians(base_deg + (wave * side))
                l1_use, l2_use = l1 + 2.0 * s, l2 + 3.0 * s
            # In Curious state, front legs inspect, shiver intensely, or deliver angry shove!
            elif self.state == 'CURIOUS' and idx == 0:
                if self.curious_phase == 'SHIVER':
                    shake_ang = math.sin(now * 32.0) * 22.0
                    cur_angle_rad = math.radians(side * 25 + shake_ang)
                    l1_use, l2_use = 22.0 * s, 24.0 * s
                elif self.curious_phase in ['SHOVE_1', 'SHOVE_2']:
                    cur_angle_rad = math.radians(side * 12 + math.sin(now * 24.0) * 12.0)
                    l1_use, l2_use = 25.0 * s, 28.0 * s
                elif self.curious_phase == 'ORBIT':
                    cur_angle_rad = math.radians(side * 28 + math.sin(now * 8.0) * 16.0)
                    l1_use, l2_use = 20.0 * s, 22.0 * s
                else:
                    cur_angle_rad = math.radians(base_deg + (wiggle * side))
                    l1_use, l2_use = l1, l2
            else:
                cur_angle_rad = math.radians(base_deg + (wiggle * side))
                l1_use, l2_use = l1, l2

            j1_x = (side * 3.5 * s) + math.sin(cur_angle_rad) * l1_use
            j1_y = (2.0 * s) + math.cos(cur_angle_rad) * l1_use
            foot_angle_rad = cur_angle_rad + math.radians(side * 22)
            j2_x = j1_x + math.sin(foot_angle_rad) * l2_use
            j2_y = j1_y + math.cos(foot_angle_rad) * l2_use

            # Leg Shadows
            s_root = transform(side * 2.5 * s, (2 + idx * 2) * s, SHADOW_OFF_X, SHADOW_OFF_Y)
            s_j1 = transform(j1_x, j1_y, SHADOW_OFF_X, SHADOW_OFF_Y)
            s_foot = transform(j2_x, j2_y, SHADOW_OFF_X, SHADOW_OFF_Y)
            self.canvas.create_line(s_root[0], s_root[1], s_j1[0], s_j1[1], fill=SHADOW_COL, width=max(1.0, 1.8 * s), tags="spider")
            self.canvas.create_line(s_j1[0], s_j1[1], s_foot[0], s_foot[1], fill=SHADOW_COL, width=max(1.0, 1.3 * s), tags="spider")

            # Main Legs
            w_root = transform(side * 2.5 * s, (2 + idx * 2) * s)
            w_j1 = transform(j1_x, j1_y)
            w_foot = transform(j2_x, j2_y)
            leg_w = max(1.0, m['leg_width'] * s)
            self.canvas.create_line(w_root[0], w_root[1], w_j1[0], w_j1[1], fill=self.theme['legs'], width=leg_w * 1.25, tags="spider")
            self.canvas.create_line(w_j1[0], w_j1[1], w_foot[0], w_foot[1], fill=self.theme['legs'], width=leg_w, tags="spider")
            self.canvas.create_oval(w_j1[0]-1.2*s, w_j1[1]-1.2*s, w_j1[0]+1.2*s, w_j1[1]+1.2*s,
                                    fill=self.theme['leg_outline'], outline="", tags="spider")

        # === LAYER 3: ABDOMEN BODY ===
        ab_pts = []
        for deg in range(0, 360, 20):
            rad = math.radians(deg)
            lx = math.cos(rad) * m['ab_rx'] * s
            ly = (8.0 * s) + math.sin(rad) * m['ab_ry'] * s
            ab_pts.extend(transform(lx, ly))
        self.canvas.create_polygon(ab_pts, fill=self.theme['abdomen'],
                                   outline=self.theme['abdomen_outline'], width=max(1, int(1.8 * s)), tags="spider")

        # === LAYER 4: DORSAL ACCENTS & MARKINGS ===
        if m.get('has_hourglass'):
            # Iconic Black Widow hourglass dorsal marking
            hg_pts = [
                transform(-2.5 * s, 4.0 * s),
                transform(2.5 * s, 4.0 * s),
                transform(0.0, 8.5 * s),
                transform(3.2 * s, 13.0 * s),
                transform(-3.2 * s, 13.0 * s),
                transform(0.0, 8.5 * s)
            ]
            flat_hg = [coord for pt in hg_pts for coord in pt]
            self.canvas.create_polygon(flat_hg, fill=self.theme['eyes'], outline="#ffffff", width=0.8, tags="spider")
        else:
            s_top = transform(0, 1.5 * s)
            s_bot = transform(0, (8.0 + m['ab_ry'] * 0.7) * s)
            self.canvas.create_line(s_top[0], s_top[1], s_bot[0], s_bot[1],
                                    fill=self.theme['dorsal_stripe'], width=max(1.0, m['dorsal_stripe_width'] * s), tags="spider")

        # === LAYER 5: THORAX & EYES ===
        th_pts = []
        for deg in range(0, 360, 20):
            rad = math.radians(deg)
            lx = math.cos(rad) * m['th_rx'] * s
            ly = (-2.5 * s) + math.sin(rad) * m['th_ry'] * s
            th_pts.extend(transform(lx, ly))
        self.canvas.create_polygon(th_pts, fill=self.theme['thorax'],
                                   outline=self.theme['thorax_outline'], width=max(1, int(1.8 * s)), tags="spider")

        if m.get('has_cute_eyes'):
            # Adorable Jumping Spider Eyes (2 giant front puppy eyes + lateral shiny eyes)
            e_r = m['eye_radius'] * s
            eye_y = (-2.5 - m['th_ry'] * 0.7) * s
            eye_left = transform(-2.2 * s, eye_y)
            eye_right = transform(2.2 * s, eye_y)
            # Big main front eyes
            self.canvas.create_oval(eye_left[0]-e_r, eye_left[1]-e_r, eye_left[0]+e_r, eye_left[1]+e_r,
                                    fill=self.theme['eyes'], outline="#ffffff", width=1.0, tags="spider")
            self.canvas.create_oval(eye_right[0]-e_r, eye_right[1]-e_r, eye_right[0]+e_r, eye_right[1]+e_r,
                                    fill=self.theme['eyes'], outline="#ffffff", width=1.0, tags="spider")
            # Cute shiny white reflections
            self.canvas.create_oval(eye_left[0]-e_r*0.6, eye_left[1]-e_r*0.6, eye_left[0]-e_r*0.1, eye_left[1]-e_r*0.1,
                                    fill="#ffffff", outline="", tags="spider")
            self.canvas.create_oval(eye_right[0]-e_r*0.6, eye_right[1]-e_r*0.6, eye_right[0]-e_r*0.1, eye_right[1]-e_r*0.1,
                                    fill="#ffffff", outline="", tags="spider")
            # Secondary lateral tiny eyes
            lat_left = transform(-4.4 * s, (-2.5 - m['th_ry'] * 0.4) * s)
            lat_right = transform(4.4 * s, (-2.5 - m['th_ry'] * 0.4) * s)
            self.canvas.create_oval(lat_left[0]-e_r*0.45, lat_left[1]-e_r*0.45, lat_left[0]+e_r*0.45, lat_left[1]+e_r*0.45,
                                    fill=self.theme['eyes'], outline="", tags="spider")
            self.canvas.create_oval(lat_right[0]-e_r*0.45, lat_right[1]-e_r*0.45, lat_right[0]+e_r*0.45, lat_right[1]+e_r*0.45,
                                    fill=self.theme['eyes'], outline="", tags="spider")
        else:
            e_r = m['eye_radius'] * s
            eye_y = (-2.5 - m['th_ry'] * 0.75) * s
            eye_left = transform(-2.4 * s, eye_y)
            eye_right = transform(2.4 * s, eye_y)
            self.canvas.create_oval(eye_left[0]-e_r, eye_left[1]-e_r, eye_left[0]+e_r, eye_left[1]+e_r,
                                    fill=self.theme['eyes'], outline="#ffffff", width=0.8, tags="spider")
            self.canvas.create_oval(eye_right[0]-e_r, eye_right[1]-e_r, eye_right[0]+e_r, eye_right[1]+e_r,
                                    fill=self.theme['eyes'], outline="#ffffff", width=0.8, tags="spider")



def main():
    banner = """\033[96m
  ███████╗██╗      ██████╗  █████╗ ████████╗██╗███╗   ██╗ ██████╗ 
  ██╔════╝██║     ██╔═══██╗██╔══██╗╚══██╔══╝██║████╗  ██║██╔════╝ 
  █████╗  ██║     ██║   ██║███████║   ██║   ██║██╔██╗ ██║██║  ███╗
  ██╔══╝  ██║     ██║   ██║██╔══██║   ██║   ██║██║╚██╗██║██║   ██║
  ██║     ███████╗╚██████╔╝██║  ██║   ██║   ██║██║ ╚████║╚██████╔╝
  ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝\033[0m
\033[93m                 D E S K T O P   F L O A T I N G\033[0m

\033[97m  ✨ Living Cyber Pet Ecosystem (Spider 🕷️, Butterfly 🦋, and more!)\033[0m
\033[90m  ⚡ Version: 1.0.0 | Author: Sohag Haldar | License: MIT\033[0m
\033[36m  ----------------------------------------------------------------------\033[0m
\033[92m  🎮 QUICK SHORTCUTS:\033[0m
\033[97m     [Shift + M]\033[0m Switch Companion (Spider ↔ Butterfly)
\033[97m     [Shift + P]\033[0m Open Live Settings & Customizer
\033[97m     [Shift + F]\033[0m Spawn Prey Fly / Fresh Leaf
\033[97m     [Shift + B]\033[0m Bungee Jump (Spider) / Stardust Burst (Butterfly)
\033[97m     [Shift + T]\033[0m Cycle Cyber Color Themes
\033[97m     [Shift + `]\033[0m Relocate Web / Cocoon Anchor
\033[97m     [Shift + ESC]\033[0m Safely Exit Pet & Application
\033[36m  ----------------------------------------------------------------------\033[0m"""
    try:
        if IS_WINDOWS:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Attach to console if started from CMD or PowerShell
            try:
                if kernel32.AttachConsole(0xFFFFFFFF):
                    sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)
                    sys.stderr = open("CONOUT$", "w", encoding="utf-8", buffering=1)
            except Exception:
                pass
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        print(banner, flush=True)
        sys.stdout.flush()
    except Exception:
        clean_banner = banner
        for code in ["\033[96m", "\033[0m", "\033[93m", "\033[97m", "\033[90m", "\033[36m", "\033[92m"]:
            clean_banner = clean_banner.replace(code, "")
        try:
            print(clean_banner, flush=True)
            sys.stdout.flush()
        except Exception:
            pass

    args = [a.lower() for a in sys.argv[1:]]
    if "-k" in args or "--kill" in args or "--stop" in args:
        if kill_running_instance():
            print("\033[93m  🛑 Stopped active Desktop Floating companion.\033[0m", flush=True)
        else:
            print("\033[90m  ℹ️ No active Desktop Floating companion was found.\033[0m", flush=True)
        return

    if "-v" in args or "--version" in args:
        print(f"Desktop Floating v1.0.0 (Engine v{APP_VERSION})", flush=True)
        return

    if "-h" in args or "--help" in args:
        print("\n  Usage:")
        print("    desktop-floating              Launch companion detached in background")
        print("    desktop-floating --foreground Run attached directly inside CMD")
        print("    desktop-floating --kill       Safely stop running companion")
        print("    desktop-floating --help       Show help & hotkeys")
        print("    desktop-floating --version    Show version\n", flush=True)
        return

    # If executed from an interactive Windows console (CMD/PowerShell), launch detached
    # so the user can close the CMD window without killing the floating companion!
    is_worker = ("--worker" in args or "--foreground" in args or "-f" in args)
    if IS_WINDOWS and not is_worker:
        if not sys.executable.lower().endswith("pythonw.exe"):
            enforce_single_instance()
            pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            if not os.path.exists(pyw):
                pyw = sys.executable

            script_path = os.path.abspath(__file__)
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200

            try:
                import subprocess
                subprocess.Popen(
                    [pyw, script_path, "--worker"],
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                    close_fds=True
                )
                print("\033[92m  📍 Status: Launched seamlessly in background!\033[0m", flush=True)
                print("\033[90m  💡 You can safely close this CMD window anytime—your companion will stay floating!\033[0m\n", flush=True)
                return
            except Exception:
                pass

    enforce_single_instance()

    print("\033[92m  📍 Status: Active & Running! 100% transparent click-through on desktop!\033[0m", flush=True)
    print("\033[90m  💡 Tip: Check the bottom-right tray icon near your clock for quick menu.\033[0m\n", flush=True)
    try:
        sys.stdout.flush()
    except Exception:
        pass

    app = DesktopSpiderApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
