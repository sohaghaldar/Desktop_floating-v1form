# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Global Configuration, Constants & Themes
"""

import os
import sys
import json
import copy

APP_VERSION = "2.6.0"

IS_WINDOWS = (sys.platform == "win32")
IS_MACOS = (sys.platform == "darwin")
IS_LINUX = sys.platform.startswith("linux")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    ROOT_DIR = BUNDLE_DIR
    exe_dir = os.path.dirname(sys.executable)
    # Check if exe_dir is writable for true portable settings persistence
    test_file = os.path.join(exe_dir, ".perm_test")
    try:
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        SETTINGS_FILE = os.path.join(exe_dir, "settings.json")
    except Exception:
        appdata_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'DesktopFloatingSpider')
        os.makedirs(appdata_dir, exist_ok=True)
        SETTINGS_FILE = os.path.join(appdata_dir, "settings.json")
else:
    SETTINGS_FILE = os.path.join(ROOT_DIR, "settings.json")

LOCALES_DIR = os.path.join(ROOT_DIR, "locales")

THEMES = [
    {
        "name_key": "theme_0",
        "abdomen": "#22272e",
        "abdomen_outline": "#f8fafc",
        "dorsal_stripe": "#e2e8f0",
        "thorax": "#2d3748",
        "thorax_outline": "#cbd5e1",
        "legs": "#2d3748",
        "leg_outline": "#ffffff",
        "eyes": "#f59e0b",
        "egg_sac": "#f59e0b",
        "egg_sac_glow": "#fbbf24",
        "web": "#e2e8f0",
        "dewdrop": "#e0f2fe",
        "hub": "#ffffff"
    },
    {
        "name_key": "theme_1",
        "abdomen": "#d97706",
        "abdomen_outline": "#fef3c7",
        "dorsal_stripe": "#fef08a",
        "thorax": "#92400e",
        "thorax_outline": "#fde68a",
        "legs": "#d97706",
        "leg_outline": "#fef3c7",
        "eyes": "#10b981",
        "egg_sac": "#10b981",
        "egg_sac_glow": "#34d399",
        "web": "#fef08a",
        "dewdrop": "#fef9c3",
        "hub": "#f59e0b"
    },
    {
        "name_key": "theme_2",
        "abdomen": "#ffffff",
        "abdomen_outline": "#94a3b8",
        "dorsal_stripe": "#cbd5e1",
        "thorax": "#f1f5f9",
        "thorax_outline": "#64748b",
        "legs": "#ffffff",
        "leg_outline": "#cbd5e1",
        "eyes": "#38bdf8",
        "egg_sac": "#38bdf8",
        "egg_sac_glow": "#7dd3fc",
        "web": "#f8fafc",
        "dewdrop": "#bae6fd",
        "hub": "#7dd3fc"
    },
    {
        "name_key": "theme_3",
        "abdomen": "#18181b",
        "abdomen_outline": "#ef4444",
        "dorsal_stripe": "#dc2626",
        "thorax": "#27272a",
        "thorax_outline": "#ef4444",
        "legs": "#18181b",
        "leg_outline": "#ef4444",
        "eyes": "#ff0033",
        "egg_sac": "#ef4444",
        "egg_sac_glow": "#f87171",
        "web": "#cbd5e1",
        "dewdrop": "#fecaca",
        "hub": "#ef4444"
    },
    {
        "name_key": "theme_4",
        "abdomen": "#00f5d4",
        "abdomen_outline": "#ffffff",
        "dorsal_stripe": "#ffffff",
        "thorax": "#00bbf9",
        "thorax_outline": "#ffffff",
        "legs": "#00f5d4",
        "leg_outline": "#ffffff",
        "eyes": "#ff0055",
        "egg_sac": "#00f5d4",
        "egg_sac_glow": "#a7f3d0",
        "web": "#a5f3fc",
        "dewdrop": "#cffafe",
        "hub": "#38bdf8"
    },
    {
        "name_key": "theme_5",
        "abdomen": "#030712",
        "abdomen_outline": "#38bdf8",
        "dorsal_stripe": "#38bdf8",
        "thorax": "#090d16",
        "thorax_outline": "#38bdf8",
        "legs": "#090d16",
        "leg_outline": "#38bdf8",
        "eyes": "#38bdf8",
        "egg_sac": "#38bdf8",
        "egg_sac_glow": "#0284c7",
        "web": "#38bdf8",
        "dewdrop": "#e0f2fe",
        "hub": "#38bdf8"
    }
]

# 4 Distinct Anatomical Spider Models
SPIDER_MODELS = [
    {
        "id": "black_widow",
        "name_key": "model_0",
        "desc": "Slender elongated abdomen with graceful curved arching legs",
        "ab_rx": 5.2,
        "ab_ry": 13.5,
        "th_rx": 4.2,
        "th_ry": 5.8,
        "leg_l1_scale": 1.25,
        "leg_l2_scale": 1.35,
        "leg_width": 1.8,
        "eye_radius": 1.6,
        "has_hourglass": True,
        "has_cute_eyes": False,
        "dorsal_stripe_width": 1.5
    },
    {
        "id": "phantom_cyber",
        "name_key": "model_1",
        "desc": "Athletic cybernetic proportions, aerodynamic and snappy",
        "ab_rx": 6.8,
        "ab_ry": 10.5,
        "th_rx": 5.2,
        "th_ry": 6.8,
        "leg_l1_scale": 1.05,
        "leg_l2_scale": 1.10,
        "leg_width": 2.0,
        "eye_radius": 2.0,
        "has_hourglass": False,
        "has_cute_eyes": False,
        "dorsal_stripe_width": 2.0
    },
    {
        "id": "jumping_spider",
        "name_key": "model_2",
        "desc": "Compact rounded body with adorable huge puppy eyes",
        "ab_rx": 6.2,
        "ab_ry": 7.0,
        "th_rx": 5.8,
        "th_ry": 6.0,
        "leg_l1_scale": 0.85,
        "leg_l2_scale": 0.85,
        "leg_width": 2.4,
        "eye_radius": 3.2,
        "has_hourglass": False,
        "has_cute_eyes": True,
        "dorsal_stripe_width": 2.2
    },
    {
        "id": "daddy_longlegs",
        "name_key": "model_3",
        "desc": "Tiny round bead body with ultra-long spindly whip legs",
        "ab_rx": 3.6,
        "ab_ry": 4.5,
        "th_rx": 3.0,
        "th_ry": 3.2,
        "leg_l1_scale": 1.65,
        "leg_l2_scale": 1.85,
        "leg_width": 1.2,
        "eye_radius": 1.4,
        "has_hourglass": False,
        "has_cute_eyes": False,
        "dorsal_stripe_width": 1.2
    }
]

DEFAULT_SETTINGS = {
    "LANGUAGE": "en",
    "CREATURE_SPECIES": "spider",
    "AUTO_START": True,
    "BUTTERFLY_THEME_INDEX": 2,
    "THEME_INDEX": 1,
    "SPIDER_MODEL_INDEX": 1,
    "SPIDER_SIZE_SCALE": 1.05,
    "SPIDER_SPEED": 7.0,
    "SHOVE_INTERVAL_SECONDS": 60,
    "SHOVE_FORCE": 35,
    "REWEAVE_INTERVAL_SECONDS": 120,
    "PANIC_RADIUS": 220,
    "EATING_DURATION_SECONDS": 5,
    "HOME_X": 1290,
    "HOME_Y": 170,
    "ENTRY_TOP_X": 705,
    "ENTRANCE_SILK_LENGTH": 290,
    "WEB_RADIUS": 115,
    "BUG_SPAWN_INTERVAL": 20,
    "SOUND_ENABLED": False,
    "REMINDER_INTERVAL_MINUTES": 30,
    "BUNGEE_AUTO_ENABLED": True,
    "BUNGEE_DROP_DISTANCE": 480,
    "WEAVE_DURATION": 14.0,
    "SPOKE_DURATION": 4.5,
    "RING_WEAVE_DURATION": 10.0,
    "WEB_THREAD_THICKNESS": 2.2,
    "FIRST_RUN_SHOWN": False,
    "LAST_SEEN_VERSION": "0.0.0",
    "HOTKEYS": {
        "SPECIES": "Shift+M",
        "MODEL": "Shift+W",
        "SETTINGS": "Shift+P",
        "ADVANCE": "Shift+E",
        "RESTART": "Shift+C",
        "ENTRY": "Shift+Q",
        "THEME": "Shift+T",
        "BUG": "Shift+F",
        "BUNGEE": "Shift+B",
        "BABIES": "Shift+H",
        "REMINDER": "Shift+R",
        "SOUND": "Shift+S",
        "MOVE": "Shift+`"
    }
}

def load_config():
    cfg = copy.deepcopy(DEFAULT_SETTINGS)
    target_path = SETTINGS_FILE
    if not os.path.exists(target_path):
        bundled = os.path.join(ROOT_DIR, "settings.json")
        if os.path.exists(bundled) and bundled != target_path:
            target_path = bundled

    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    if k == "HOTKEYS" and isinstance(v, dict):
                        cfg["HOTKEYS"].update(v)
                    else:
                        cfg[k] = v
        except Exception as e:
            print("[!] Error reading settings.json:", e)
    return cfg

def save_config_value(key, value):
    try:
        cfg = load_config()
        cfg[key] = value
        save_full_settings(cfg)
    except Exception as e:
        print("[!] Error saving config value:", e)

def save_full_settings(settings_dict):
    try:
        # Load existing file first to safely preserve any custom user keys
        existing = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = {}
        
        # Merge changes into existing dictionary
        for k, v in settings_dict.items():
            if k == "HOTKEYS" and isinstance(v, dict):
                if "HOTKEYS" not in existing or not isinstance(existing["HOTKEYS"], dict):
                    existing["HOTKEYS"] = {}
                existing["HOTKEYS"].update(v)
            else:
                existing[k] = v

        # Atomic write with temp file
        tmp_file = SETTINGS_FILE + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        if os.path.exists(SETTINGS_FILE):
            os.replace(tmp_file, SETTINGS_FILE)
        else:
            os.rename(tmp_file, SETTINGS_FILE)
    except Exception as e:
        print("[!] Error writing settings.json:", e)

def parse_hotkey_combo(hk_str):
    """Parses hotkey string into (need_shift, need_ctrl, need_alt, vk_code)."""
    parts = [p.strip().upper() for p in str(hk_str).split("+")]
    need_shift = "SHIFT" in parts
    need_ctrl = "CTRL" in parts or "CONTROL" in parts
    need_alt = "ALT" in parts
    key_part = parts[-1] if parts else ""
    vk = get_vk_code(key_part)
    return need_shift, need_ctrl, need_alt, vk

def get_vk_code(key_char):
    s = str(key_char).upper().strip()
    if len(s) == 1 and ('A' <= s <= 'Z' or '0' <= s <= '9'):
        return ord(s)
    if s in ['`', '~']:
        return 0xC0
    if s == 'ESC':
        return 0x1B
    if s.startswith('F') and s[1:].isdigit() and 1 <= int(s[1:]) <= 12:
        return 0x6F + int(s[1:])
    if s == 'SPACE':
        return 0x20
    if s == 'TAB':
        return 0x09
    return ord(s[0]) if s else 0
