# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Localization & Internationalization (i18n) Engine
Equipped with embedded fallback strings, multi-language catalog, and zero-lag async downloader.
"""

import os
import json
import threading
import urllib.request
import urllib.parse
from core.config import LOCALES_DIR

WORLD_LANGUAGES = [
    ("bn", "বাংলা (Bengali)"),
    ("en", "English (US/UK)"),
    ("es", "Español (Spanish)"),
    ("hi", "हिन्दी (Hindi)"),
    ("fr", "Français (French)"),
    ("de", "Deutsch (German)"),
    ("ja", "日本語 (Japanese)"),
    ("zh", "简体中文 (Chinese)"),
    ("ar", "العربية (Arabic)"),
    ("ru", "Русский (Russian)"),
    ("pt", "Português (Portuguese)"),
    ("it", "Italiano (Italian)"),
    ("ko", "한국어 (Korean)"),
    ("tr", "Türkçe (Turkish)"),
    ("vi", "Tiếng Việt (Vietnamese)"),
    ("id", "Bahasa Indonesia"),
    ("pl", "Polski (Polish)"),
    ("nl", "Nederlands (Dutch)"),
    ("th", "ไทย (Thai)"),
    ("sv", "Svenska (Swedish)"),
    ("el", "Ελληνικά (Greek)"),
    ("ro", "Română (Romanian)"),
    ("cs", "Čeština (Czech)"),
    ("uk", "Українська (Ukrainian)"),
    ("fa", "فارسی (Persian)"),
    ("ur", "اردو (Urdu)")
]

# Hardcoded fallback dictionary ensures the app NEVER crashes even without locales folder or in .exe
FALLBACK_STRINGS = {
    "lang_name": "English",
    "app_title": "Desktop Floating",
    "win_title": "🕷 Desktop Floating — Live Settings & Customizer",
    "header_title": "🕷 Desktop Floating Live Control Panel",
    "header_sub": "⚡ Changes apply immediately live on desktop!",
    "card_lang": "🌐 Language & Localization",
    "lbl_lang": "Select Language:",
    "btn_add_lang": "📥 Add / Download New Language...",
    "card_model": "🕷 Spider Model & Anatomy",
    "lbl_model_select": "Choose Model:",
    "lbl_spider_scale": "Body Scale / Slimness:",
    "card_speed": "⚡ Speed & Mobility",
    "lbl_crawl_speed": "Normal Crawl Speed:",
    "card_hunting": "🎯 Mouse Attack & Curiosity",
    "lbl_shove_interval": "Mouse Attack Timer (sec):",
    "lbl_shove_force": "Headbutt Shove Force (px):",
    "card_web": "🕸 Web, Silk & Themes",
    "lbl_web_radius": "Web Radius (px):",
    "lbl_silk_length": "Ceiling Silk Length (px):",
    "lbl_bungee_dist": "Bungee Drop Distance (px):",
    "lbl_theme": "Color Theme:",
    "chk_sound": "🔊 Enable Sound Effects",
    "card_hotkeys": "⌨ Custom Hotkey Settings",
    "lbl_hotkey_tip": "Click any button then press your key combination (e.g. Ctrl, Shift, Alt + Key):",
    "btn_save_hotkeys": "💾 Save Hotkeys",
    "hk_model": "Model Switch:",
    "hk_settings": "Settings Panel:",
    "hk_restart": "Rappel Restart:",
    "hk_entry": "Set Ceiling Entry:",
    "hk_theme": "Switch Theme:",
    "hk_bug": "Spawn Insect:",
    "hk_bungee": "Bungee Jump:",
    "hk_babies": "Hatch Babies:",
    "hk_reminder": "Health Reminder:",
    "hk_sound": "Sound Toggle:",
    "hk_move": "Move Web:",
    "card_test": "⚡ Instant Test Actions",
    "btn_test_shove": "🎯 Test Mouse Headbutt Now",
    "btn_test_entrance": "🕸 Test Ceiling Rappel",
    "btn_test_bug": "🦟 Spawn Insect",
    "btn_test_bungee": "🪂 Bungee Jump",
    "btn_reset": "🔄 Reset to Defaults",
    "btn_save_close": "💾 Save All & Close",
    "tray_settings": "⚙ Live Settings & Customizer",
    "tray_switch_model": "🕷 Switch Model",
    "tray_restart": "🕸 Restart / Rappel Down",
    "tray_set_entry": "🎯 Set Ceiling Entry Point",
    "tray_switch_theme": "🎨 Switch Theme",
    "tray_spawn_insect": "🦟 Spawn Insect",
    "tray_bungee": "🪂 Bungee Jump",
    "tray_hatch": "🥚 Hatch Babies",
    "tray_health": "💧 Health Break",
    "tray_sound": "🔊 Sound Toggle",
    "tray_move_web": "📍 Move Web",
    "tray_exit": "❌ Exit Desktop Floating",
    "model_0": "Velvet Slim Widow",
    "model_1": "⚡ Phantom Cyber Hunter",
    "model_2": "Cute Jumping Spider",
    "model_3": "Daddy Long-Legs",
    "theme_0": "Velvet Wolf Spider",
    "theme_1": "Golden Silk Weaver",
    "theme_2": "Ghost Frost Spider",
    "theme_3": "Blood Ruby / Black Widow",
    "theme_4": "Cyber Teal Spider",
    "theme_5": "Obsidian Pitch Black",
    "reminder_water": "💧 Time to hydrate! Drink a fresh glass of water.",
    "reminder_eye": "👁 20-20-20 Rule: Look away at something 20 feet away for 20 seconds!",
    "reminder_stretch": "🧘 Posture check: Straighten your back and stretch your shoulders!",
    "lock_pos": "Web position locked at:",
    "status_on": "ON",
    "status_off": "OFF",
    "status_locked": "LOCKED",
    "status_moving": "DRAGGING",
    "lbl_weave_duration": "Web Weaving Duration (sec):",
    "lbl_web_thickness": "Web Thread Thickness (px):",
    "reminder_water_title": "HYDRATION BREAK",
    "reminder_water_body": "Time to hydrate! Drink a fresh glass of water.",
    "reminder_eye_title": "20-20-20 EYE CARE",
    "reminder_eye_body": "Look 20 feet away for 20 seconds to rest your eyes!",
    "reminder_stretch_title": "POSTURE & STRETCH",
    "reminder_stretch_body": "Straighten your back and gently roll your shoulders.",
    "reminder_breathe_title": "DEEP BREATHING",
    "reminder_breathe_body": "Take 3 slow deep breaths to recharge your focus.",
    "card_species": "🐾 Desktop Creature & Species",
    "lbl_species_select": "Active Creature Species:",
    "species_spider": "🕷️ Silk Arachnid (Spider)",
    "species_butterfly": "🦋 Metamorphosis Butterfly",
    "card_butterfly": "🦋 Butterfly Life Cycle & Metamorphosis",
    "lbl_butterfly_stage": "Current Life Stage:",
    "stage_caterpillar": "🐛 Cute Caterpillar",
    "stage_chrysalis": "🌿 Chrysalis Cocoon (Pupa)",
    "stage_emergence": "✨ Butterfly Emergence",
    "stage_flying": "🦋 Free Flight & Flutter",
    "btn_restart_butterfly": "🔄 Restart Life Cycle (Caterpillar)",
    "btn_evolve_butterfly": "⏩ Advance to Next Stage",
    "lbl_butterfly_style": "Wing Style & Theme:",
    "b_style_0": "💙 Morpho Electric Blue",
    "b_style_1": "🧡 Royal Monarch Sunset",
    "b_style_2": "💚 Emerald Swallowtail",
    "b_style_3": "💜 Twilight Fairy Violet",
    "chk_autostart": "🚀 Start Automatically with Windows (Silent Background)",
    "tray_switch_species": "🐾 Switch Creature",
    "tray_butterfly_evolve": "⏩ Advance Metamorphosis",
    "tray_butterfly_restart": "🐛 Restart as Caterpillar",
    "hk_species": "Creature Switch:",
    "lbl_spoke_duration": "Spoke Lines Duration (sec):",
    "lbl_ring_duration": "Spiral Rings Weaving Duration (sec):",
    "species_chameleon": "🦎 Wall Gecko",
    "species_fireflies": "💡 Firefly Swarm",
    "species_dragon": "🐉 Celestial Dragon",
    "species_jellyfish": "🪼 Cosmic Jellyfish",
    "card_creature_controls": "🐾 Active Creature Controls",
    "btn_dragon_breath": "🔥 Starlight Ember Breath",
    "btn_chameleon_snap": "👅 Ballistic Tongue Zap",
    "btn_fireflies_pulse": "✨ Synchronized Glow Flash",
    "btn_jellyfish_pulse": "🌊 Bioluminescent Ripple",
    "species_bird": "🦚 Royal Crested Bird",
    "nest_moved": "Bird nest relocated to new position!",
    "card_updater": "🔄 Software Updates & GitHub",
    "lbl_version": "Current Version:",
    "btn_check_update": "🔍 Check for Updates",
    "btn_update_now": "✨ Update Now",
    "lbl_up_to_date": "✅ You are using the latest version!",
    "lbl_update_found": "🚀 New version available:",
    "lbl_checking_updates": "Checking GitHub for updates...",
    "chk_auto_update": "Automatically check for updates on startup",
    "tray_check_update": "🔄 Check for Updates",
    "tray_update_available": "✨ New Update Available!",
    "msg_update_success": "Software updated successfully! Please restart the application to apply changes.",
    "msg_update_error": "Update download failed: ",
    "stage_eating": "🍃 Eating Fresh Leaf",
    "stage_walking_cocoon": "🚶 Walking to Cocoon Spot",
    "stage_entering_cocoon": "🚪 Entering Silk Cocoon",
    "btn_bf_advance": "⏩ Advance Stage",
    "btn_bf_restart": "🔄 Restart Lifecycle",
    "btn_bf_relocate": "🥚 Relocate Cocoon / Egg",
    "lbl_wing_themes": "🎨 Wing Color Themes (4 Styles):",
    "lbl_bf_scale": "Butterfly & Caterpillar Size Scale:",
    "lbl_bf_flight_speed": "Butterfly Flight Speed:",
    "lbl_bf_crawl_speed": "Caterpillar Crawl Speed:",
    "th_morpho": "🦋 Morpho Azure",
    "th_monarch": "🌅 Monarch Ember",
    "th_emerald": "🌿 Emerald Swallowtail",
    "th_sakura": "🌸 Sakura Empress",
    "hk_bf_species": "Creature Switch:",
    "hk_bf_settings": "Settings Panel:",
    "hk_bf_advance": "Advance Stage:",
    "hk_bf_restart": "Restart Lifecycle:",
    "hk_bf_move": "Relocate Cocoon / Egg:",
    "hk_bf_theme": "Wing Theme Switch:",
    "hk_bf_sparkle": "Fairy Dust / Fresh Leaf:",
    "hk_bf_sound": "Sound Toggle:",
    "hk_bf_reminder": "Health Reminder:",
    "hk_bf_exit": "Quit Application:",
    "hk_spider_model": "Spider Model Switch:",
    "hk_spider_restart": "Ceiling Rappel Restart:",
    "hk_spider_entry": "Set Ceiling Entry:",
    "hk_spider_theme": "Silk Web Theme:",
    "hk_spider_bug": "Spawn Insect:",
    "hk_spider_bungee": "Bungee Jump:",
    "hk_spider_babies": "Hatch Spiderlings:",
    "hk_spider_move": "Move Web to Cursor:",
    "hk_bird_move": "Relocate Nest:",
    "hk_bird_theme": "Plumage Theme:",
    "hk_bird_song": "Bird Call & Flight:",
    "hk_bird_return": "Return to Nest:",
    "btn_bird_song": "🎵 Bird Call & Flight",
    "btn_bird_theme": "🪶 Plumage Theme",
    "btn_bird_nest": "🪺 Relocate Nest",
    "hk_cham_theme": "Camouflage Color:",
    "hk_cham_hunt": "Tongue Zap Hunt:",
    "hk_fireflies_pulse": "Synchronized Flash:",
    "hk_dragon_breath": "Starlight Breath:",
    "hk_jellyfish_pulse": "Bioluminescent Ripple:",
    "tray_wing_theme": "Wing Theme",
    "tray_relocate_cocoon": "Relocate Cocoon / Egg",
    "tray_advance_stage": "Advance Stage",
    "tray_restart_lifecycle": "Restart Life Cycle",
    "tray_fairy_dust": "Fairy Dust Burst",
    "tray_bird_theme": "Plumage Theme",
    "tray_bird_nest": "Relocate Nest",
    "tray_bird_song": "Bird Call & Flight",
    "tray_bird_return": "Return to Nest",
    "lbl_hotkey_creature": "Active Creature:",
    "msg_hotkeys_saved": "Custom hotkeys saved successfully!",
    "title_hotkeys_saved": "Hotkeys Saved",
    "toast_cocoon_relocated": "🥚 Cocoon / Egg Spot Relocated:",
    "toast_wing_theme": "🎨 Wing Theme:",
    "toast_sparkle_burst": "✨ Fairy Dust Stardust Burst!",
    "toast_leaf_spawned": "🌿 Fresh Leaf Spawned!",
    "hk_move_gecko": "Relocate Gecko:",
    "lbl_gecko_size": "Wall Gecko Size Scale:",
    "tray_gecko_theme": "Camouflage Theme",
    "tray_relocate_gecko": "Relocate Gecko",
    "tray_gecko_hunt": "Ballistic Tongue Zap",
    "lb_title": "🌐 Global Language Library & Downloader",
    "lb_subtitle": "Switch languages instantly with zero lag, or download new languages in the background.",
    "lb_status_active": "● Active Language",
    "lb_status_ready": "✓ Installed & Ready",
    "lb_status_download": "⬇ Download Needed (~2 KB)",
    "lb_active_badge": "Active ✓",
    "lb_btn_activate": "Activate",
    "lb_btn_download": "⬇ Download",
    "lb_btn_waiting": "⏳ Please wait...",
    "lb_custom_lbl": "Custom Language Code (e.g. 'el', 'ro', 'cs'):",
    "lb_custom_btn": "Download",
    "lb_downloading": "Downloading & translating",
    "lb_download_succ": "Downloaded successfully!",
    "lb_download_err": "Download error:",
    "lb_retry": "Retry",
    "hk_prompt_press": "[Press Key...]",
    "lbl_spoke": "Spoke",
    "lbl_rings": "Rings",
    "mode_spider_active": "Silk Arachnid Mode Active"
}

class I18n:
    def __init__(self, lang="bn"):
        self.lang = lang
        self.fallback_strings = FALLBACK_STRINGS
        self.strings = {}
        self.load(self.lang)

    @classmethod
    def get_available_languages(cls):
        """Returns dictionary of all installed languages in locales directory."""
        langs = {"en": "English", "bn": "বাংলা (Bengali)"}
        if os.path.exists(LOCALES_DIR):
            for fname in os.listdir(LOCALES_DIR):
                if fname.endswith(".json"):
                    code = fname[:-5]
                    fpath = os.path.join(LOCALES_DIR, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            d = json.load(f)
                            langs[code] = d.get("lang_name", code.upper())
                    except Exception:
                        langs[code] = code.upper()
        return langs

    def load(self, lang_code):
        """Loads language strings from file with seamless fallback."""
        self.lang = lang_code
        fpath = os.path.join(LOCALES_DIR, f"{lang_code}.json")
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    self.strings = json.load(f)
                return True
            except Exception:
                pass
        fpath_en = os.path.join(LOCALES_DIR, "en.json")
        if os.path.exists(fpath_en):
            try:
                with open(fpath_en, "r", encoding="utf-8") as f:
                    self.strings = json.load(f)
                return True
            except Exception:
                pass
        self.strings = dict(self.fallback_strings)
        return False

    def t(self, key, default=""):
        """Safely resolves a localized string. Falls back to embedded English, then default, then key."""
        val = self.strings.get(key)
        if val is not None and str(val).strip():
            return val
        fb = self.fallback_strings.get(key)
        if fb is not None and str(fb).strip():
            return fb
        return default or key

    def download_language_async(self, lang_code, lang_name=None, on_progress=None, on_success=None, on_error=None):
        """Downloads/translates a language in a background daemon thread with zero GUI freeze."""
        def _worker():
            try:
                os.makedirs(LOCALES_DIR, exist_ok=True)
                target_path = os.path.join(LOCALES_DIR, f"{lang_code}.json")
                base_dict = dict(self.fallback_strings)
                en_path = os.path.join(LOCALES_DIR, "en.json")
                if os.path.exists(en_path):
                    try:
                        with open(en_path, "r", encoding="utf-8") as f:
                            base_dict = json.load(f)
                    except Exception:
                        pass

                name = lang_name or lang_code.upper()
                translated = {"lang_name": name}
                keys = [k for k in base_dict.keys() if k != "lang_name"]
                total = len(keys)

                for idx, k in enumerate(keys):
                    text = str(base_dict[k])
                    try:
                        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={lang_code}&dt=t&q=" + urllib.parse.quote(text)
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=4) as res:
                            data = json.loads(res.read().decode('utf-8'))
                            translated[k] = data[0][0][0]
                    except Exception:
                        translated[k] = text

                    if on_progress and (idx % 10 == 0 or idx == total - 1):
                        on_progress(idx + 1, total)

                with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(translated, f, indent=2, ensure_ascii=False)

                if on_success:
                    on_success(lang_code, name)
            except Exception as e:
                if on_error:
                    on_error(str(e))

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return t

I18nManager = I18n
