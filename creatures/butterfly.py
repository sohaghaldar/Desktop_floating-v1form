# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Butterfly & Caterpillar Metamorphosis Engine
Features:
1. True Inverse-Kinematics Segment Trail: Fixed segment distances (NO spring compression!).
2. Natural multi-joint body bending: Whole body curves smoothly when turning or targeting leaves.
3. Looper arch wave: Smooth, continuous arch without any tail jumping.
4. Correct head anatomy: Antennae rooted on upper crown/forehead, completely separate from lateral eyes.
5. Interactive Mouse Pain & Shove: Clicking the caterpillar causes pain reaction, defensive thrashing,
   and shoving the mouse cursor away like the spider!
6. Cocoon progress strictly proportional to leaf eating (3 leaves = 100% cocoon).
7. Cocoon descends smoothly from monitor ceiling like spider silk, with ZERO gaps to the thread!
8. Caterpillar crawls head-first smoothly into the cocoon opening with zero teleportation or floating discs.
9. Realistic butterfly flight: Flaps wings 3-4 times, then glides straight forward with wings spread open!
"""

import math
import random
import time
import ctypes
import traceback
from core.platform_helper import play_audio, PlatformHelper
from core.config import save_config_value, load_config

BUTTERFLY_THEMES = [
    {
        "name": "Morpho Azure",
        "bengali": "মর্ফো নীল (রয়েল সাইয়ান)",
        "icon": "🦋",
        "primary": "#0284c7",    # Electric Sapphire
        "secondary": "#0369a1",  # Deep Marine
        "accent": "#00f2fe",     # Luminous Aqua
        "glow": "#7dd3fc",       # Bioluminescent Cyan
        "border": "#021a2f",     # Midnight Velvet
        "iridescent": "#cffafe", # Diamond Pearl
        "spots": "#ffffff",      # Pure Pearl
        "ant_tip": "#38bdf8",
        "cocoon_shell": "#0c4a6e",
        "cocoon_accent": "#38bdf8",
        "cocoon_weave": "#7dd3fc",
        "particle_colors": ["#0284c7", "#38bdf8", "#7dd3fc", "#ffffff"]
    },
    {
        "name": "Monarch Ember",
        "bengali": "রাজকীয় আগুন (সানসেট অ্যাম্বার)",
        "icon": "🌅",
        "primary": "#ea580c",    # Fiery Tangerine
        "secondary": "#c2410c",  # Deep Terracotta
        "accent": "#f59e0b",     # Sunburst Gold
        "glow": "#fef08a",       # Warm Sunshine
        "border": "#1c1917",     # Obsidian Charcoal
        "iridescent": "#ffedd5", # Golden Silk
        "spots": "#ffffff",      # White Stars
        "ant_tip": "#fbbf24",
        "cocoon_shell": "#78350f",
        "cocoon_accent": "#f59e0b",
        "cocoon_weave": "#fef08a",
        "particle_colors": ["#ea580c", "#f59e0b", "#fef08a", "#ffffff"]
    },
    {
        "name": "Emerald Swallowtail",
        "bengali": "মরকত সবুজ (জেড ও গোল্ড)",
        "icon": "🌿",
        "primary": "#059669",    # Jeweled Emerald
        "secondary": "#047857",  # Deep Forest Jade
        "accent": "#10b981",     # Bright Mint
        "glow": "#a7f3d0",       # Spring Meadow
        "border": "#022c22",     # Dark Pine
        "iridescent": "#6ee7b7", # Aurora Lime
        "spots": "#fef08a",      # Golden Dew
        "ant_tip": "#a3e635",
        "cocoon_shell": "#064e3b",
        "cocoon_accent": "#10b981",
        "cocoon_weave": "#a7f3d0",
        "particle_colors": ["#059669", "#10b981", "#a7f3d0", "#fef08a"]
    },
    {
        "name": "Sakura Empress",
        "bengali": "বেগুনী অর্কিড (অ্যামেথিস্ট ও গোলাপি)",
        "icon": "🌸",
        "primary": "#9333ea",    # Royal Amethyst
        "secondary": "#7e22ce",  # Deep Velvet Plum
        "accent": "#ec4899",     # Vivid Orchid Pink
        "glow": "#f472b6",       # Rose Petal Glow
        "border": "#2e1065",     # Midnight Plum
        "iridescent": "#fbcfe8", # Sakura Silk
        "spots": "#fef9c3",      # Cream Stardust
        "ant_tip": "#f472b6",
        "cocoon_shell": "#581c87",
        "cocoon_accent": "#ec4899",
        "cocoon_weave": "#f472b6",
        "particle_colors": ["#9333ea", "#ec4899", "#f472b6", "#ffffff"]
    }
]

class ButterflyLifeCycle:
    def __init__(self, app):
        self.app = app
        self.stage = "FLYING" # Default directly to flying butterfly so it's immediately visible!
        self.theme_idx = int(app.config.get("BUTTERFLY_THEME_INDEX", 0)) % len(BUTTERFLY_THEMES)
        self.theme = BUTTERFLY_THEMES[self.theme_idx]

        self.scale = float(app.config.get("BUTTERFLY_SCALE", 1.15))
        self.crawl_speed = float(app.config.get("BUTTERFLY_CRAWL_SPEED", 1.8))
        self.flight_speed = float(app.config.get("BUTTERFLY_FLIGHT_SPEED", 1.0))
        self.toast_text = ""
        self.toast_until = 0.0

        self.x = float(app.screen_x + app.screen_w // 2)
        self.y = float(app.screen_y + app.screen_h // 2)
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.target_angle = 0.0
        self.flight_timer = time.time()

        # Cocoon Location
        self.cocoon_x = float(app.config.get("COCOON_X", app.screen_x + app.screen_w // 2))
        self.cocoon_y = float(app.config.get("COCOON_Y", app.screen_y + 160))
        # Cocoon descent from top of screen
        self.cocoon_descent_y = float(app.screen_y - 20.0)

        # Caterpillar Kinematics: 12 segments with fixed inter-segment distance (NO SPRINGING!)
        self.num_segments = 12
        # Short, overlapping segments read as a soft body instead of a chain of beads.
        self.seg_dist = 13.8 * self.scale
        # Initialize segments in a smooth line behind head
        self.segments = []
        for i in range(self.num_segments):
            self.segments.append({
                'x': self.x - i * self.seg_dist,
                'y': self.y,
                'angle': 0.0
            })

        self.inch_phase = 0.0
        self._last_crawl_time = time.time()
        self._last_phase_time = self._last_crawl_time
        self._last_reported_error = None
        self._last_error_report_time = 0.0
        self.border_edge = 0 # 0: bottom, 1: right, 2: top, 3: left

        # Leaves and Cocoon Construction Progress
        self.leaves_eaten = 0
        self.total_leaves_needed = 3
        self.leaves = []
        self.current_leaf = None
        self.chew_crumbs = []
        self.cocoon_build_p = 0.0
        self.caterpillar_entry_p = 0.0
        self.entry_start_time = 0.0
        self.entry_mouth_x = self.cocoon_x
        self.entry_mouth_y = self.cocoon_y
        self.entry_direction = (0.0, 1.0)
        self.entry_hidden_segments = set()
        self.eating_start = 0.0
        self.chrysalis_start = 0.0
        self.emergence_start = 0.0
        self.wing_expansion = 0.0

        # Interactive Pain & Shove Reaction
        self.pain_active = False
        self.pain_start = 0.0
        self.last_pain_time = 0.0
        self.shove_target_x = 0.0
        self.shove_target_y = 0.0
        self.pain_flee_dx = -1.0

        # Realistic Butterfly Flight Dynamics (Flutter-Glide)
        self.flight_timer = 0.0
        self.is_gliding = False
        self.flap_phase = 0.0
        self.trail_particles = []
        self.free_flight_timer = 0.0

        # Spawn initial leaf
        self.spawn_leaf_for_current_border()

    def show_toast(self, text, duration=2.5):
        self.toast_text = text
        self.toast_until = time.time() + duration

    def set_scale(self, val, commit=True):
        self.scale = max(0.5, min(2.5, float(val)))
        self.seg_dist = 13.8 * self.scale
        if commit:
            save_config_value("BUTTERFLY_SCALE", round(self.scale, 2))

    def set_crawl_speed(self, val, commit=True):
        self.crawl_speed = max(1.0, min(5.0, float(val)))
        if commit:
            save_config_value("BUTTERFLY_CRAWL_SPEED", round(self.crawl_speed, 2))

    def set_flight_speed(self, val, commit=True):
        self.flight_speed = max(0.5, min(3.0, float(val)))
        if commit:
            save_config_value("BUTTERFLY_FLIGHT_SPEED", round(self.flight_speed, 2))

    def trigger_flight_sparkle(self):
        """Shift+F action: bursts shimmering fairy dust particles in current theme colors!"""
        for _ in range(20):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(2.0, 6.5)
            self.trail_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(ang) * spd,
                'vy': math.sin(ang) * spd - 1.2,
                'size': random.uniform(2.2, 4.2),
                'life': 1.0,
                'color': random.choice(self.theme.get('particle_colors', ['#ffffff']))
            })
        hk_f = getattr(self.app, 'hotkeys', {}).get('BUG', 'Shift+F') if hasattr(self.app, 'hotkeys') else 'Shift+F'
        is_bn = hasattr(self.app, 'i18n') and getattr(self.app.i18n, 'lang', '') == "bn"
        if self.stage in ["CATERPILLAR", "CATERPILLAR_EATING"]:
            self.spawn_leaf_for_current_border()
            msg = f"🌿 নতুন তাজা পাতা জন্মালো! [{hk_f}]" if is_bn else f"🌿 Fresh Leaf Spawned! [{hk_f}]"
            self.show_toast(msg)
        else:
            msg = f"✨ জাদুকরী ফেয়ারি ডাস্ট বিচ্ছুরণ! [{hk_f}]" if is_bn else f"✨ Fairy Dust Stardust Burst! [{hk_f}]"
            self.show_toast(msg)
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(900, 30, 1350, 45)

    def set_cocoon_spot_from_cursor(self):
        mx, my = self.app.get_mouse_pos()
        self.cocoon_x = float(mx)
        self.cocoon_y = max(float(self.app.screen_y + 90), float(my))
        if self.cocoon_build_p >= 0.95 or self.stage in ["CHRYSALIS", "EMERGENCE", "FLYING"]:
            self.cocoon_descent_y = self.cocoon_y
        save_config_value("COCOON_X", int(self.cocoon_x))
        save_config_value("COCOON_Y", int(self.cocoon_y))
        hk_move = getattr(self.app, 'hotkeys', {}).get('MOVE', 'Shift+`') if hasattr(self.app, 'hotkeys') else 'Shift+`'
        is_bn = hasattr(self.app, 'i18n') and getattr(self.app.i18n, 'lang', '') == "bn"
        prefix = "🥚 ডিম ও কোকুন স্থানান্তর:" if is_bn else "🥚 Cocoon / Egg Spot Relocated:"
        self.show_toast(f"{prefix} ({int(self.cocoon_x)}, {int(self.cocoon_y)}) [{hk_move}]")
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(900, 45, 1250, 55)
        print(f"[*] Butterfly Cocoon Spot Relocated to: ({int(self.cocoon_x)}, {int(self.cocoon_y)})")

    def set_theme(self, idx):
        self.theme_idx = idx % len(BUTTERFLY_THEMES)
        self.theme = BUTTERFLY_THEMES[self.theme_idx]
        save_config_value("BUTTERFLY_THEME_INDEX", self.theme_idx)

    def cycle_theme(self):
        new_idx = (self.theme_idx + 1) % len(BUTTERFLY_THEMES)
        self.set_theme(new_idx)
        th = BUTTERFLY_THEMES[self.theme_idx]
        hk_th = getattr(self.app, 'hotkeys', {}).get('THEME', 'Shift+T') if hasattr(self.app, 'hotkeys') else 'Shift+T'
        is_bn = hasattr(self.app, 'i18n') and getattr(self.app.i18n, 'lang', '') == "bn"
        th_name = th.get('bengali') if is_bn else th.get('name')
        prefix = "🎨 ডানার থিম:" if is_bn else "🎨 Wing Theme:"
        self.show_toast(f"{prefix} {th.get('icon','🦋')} {th_name} [{self.theme_idx+1}/4] [{hk_th}]")
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(650, 40, 950, 50)

    def advance_stage(self):
        now = time.time()
        if self.stage in ["CATERPILLAR", "CATERPILLAR_EATING"]:
            self.cocoon_build_p = 1.0
            self.leaves_eaten = self.total_leaves_needed
            self.stage = "WALKING_TO_COCOON"
            if self.app.SOUND_ENABLED: play_audio(440, 40, 660, 50)
        elif self.stage == "WALKING_TO_COCOON":
            self._begin_cocoon_entry(now)
        elif self.stage == "COCOON_ENTERING":
            self.stage = "CHRYSALIS"
            self.chrysalis_start = now
        elif self.stage == "CHRYSALIS":
            self.stage = "EMERGENCE"
            self.emergence_start = now
            self.wing_expansion = 0.2
        elif self.stage == "EMERGENCE":
            self.stage = "FLYING"
            self.free_flight_timer = now
        elif self.stage == "FLYING":
            self.restart_lifecycle()
            return

        is_bn = hasattr(self.app, 'i18n') and getattr(self.app.i18n, 'lang', '') == "bn"
        stage_titles = {
            "WALKING_TO_COCOON": "🚶 কোকুনে যাচ্ছে" if is_bn else "🚶 Walking to Cocoon",
            "COCOON_ENTERING": "🚪 গুটিতে ঢুকছে" if is_bn else "🚪 Entering Cocoon",
            "CHRYSALIS": "🌿 রেশম গুটি (পিউপা)" if is_bn else "🌿 Chrysalis Cocoon",
            "EMERGENCE": "✨ প্রজাপতি ডানা মেলা" if is_bn else "✨ Emergence",
            "FLYING": "🦋 মুক্ত উড্ডয়ন" if is_bn else "🦋 Free Flight",
            "CATERPILLAR": "🐛 শুঁয়োপোকা" if is_bn else "🐛 Caterpillar"
        }
        st_title = stage_titles.get(self.stage, self.stage)
        self.show_toast(f"⏩ {st_title}")

    def restart_lifecycle(self):
        self.stage = "CATERPILLAR"
        self.x = float(self.app.screen_x + 220)
        self.y = float(self.app.screen_y + self.app.screen_h - 40)
        self.angle = 0.0
        self.border_edge = 0
        self.leaves_eaten = 0
        self.leaves = []
        self.current_leaf = None
        self.chew_crumbs = []
        self.cocoon_build_p = 0.0
        self.caterpillar_entry_p = 0.0
        self.entry_start_time = 0.0
        self.wing_expansion = 0.0
        self._last_crawl_time = time.time()
        self.cocoon_descent_y = float(self.app.screen_y - 20.0)
        self.pain_active = False
        is_bn = hasattr(self.app, 'i18n') and getattr(self.app.i18n, 'lang', '') == "bn"
        msg = "🔄 নতুন করে জীবনচক্র শুরু [শুঁয়োপোকা]" if is_bn else "🔄 Restart Lifecycle [Caterpillar]"
        self.show_toast(msg)

        self.segments = []
        for i in range(self.num_segments):
            self.segments.append({
                'x': self.x - i * self.seg_dist,
                'y': self.y,
                'angle': 0.0
            })

        self.spawn_leaf_for_current_border()
        if self.app.SOUND_ENABLED:
            play_audio(550, 40, 880, 50)

    def set_stage(self, stage_name):
        """Immediately switch to a specific stage (CATERPILLAR, CHRYSALIS, or FLYING)."""
        is_bn = hasattr(self.app, 'i18n') and getattr(self.app.i18n, 'lang', '') == "bn"
        if stage_name == "FLYING":
            self.stage = "FLYING"
            self.flight_timer = time.time()
            self.free_flight_timer = time.time()
            self.x = float(self.app.screen_x + self.app.screen_w // 2)
            self.y = float(self.app.screen_y + self.app.screen_h // 2)
            self.vx = 2.0
            self.vy = -1.0
            msg = "🦋 মুক্ত উড্ডয়ন ও ডানা ঝাপটানো" if is_bn else "🦋 Free Flight & Flutter"
            self.show_toast(msg)
            if self.app.SOUND_ENABLED: play_audio(700, 30, 1100, 45)
        elif stage_name == "CATERPILLAR":
            self.restart_lifecycle()
        elif stage_name == "CHRYSALIS":
            self.stage = "CHRYSALIS"
            self.cocoon_build_p = 1.0
            self.cocoon_descent_y = self.cocoon_y
            self.chrysalis_start = time.time()
            msg = "🌿 পান্না রেশম গুটি (পিউপা)" if is_bn else "🌿 Chrysalis Cocoon (Pupa)"
            self.show_toast(msg)
            if self.app.SOUND_ENABLED: play_audio(440, 40, 660, 50)

    def trigger_pain_reaction(self, mx, my, now):
        """Interactive pain startle & mouse shove (মাউস দিয়ে আঘাত করলে ব্যথা ও তাড়িয়ে দেওয়া)"""
        self.pain_active = True
        self.pain_start = now
        self.last_pain_time = now
        self.shove_target_x = mx
        self.shove_target_y = my

        # Shove mouse cursor 40px away
        dx_m = mx - self.x
        dy_m = my - self.y
        dist_m = max(1.0, math.hypot(dx_m, dy_m))
        self.pain_flee_dx = -dx_m / dist_m
        for leaf in self.leaves:
            leaf['approach'] = None
        if abs(self.pain_flee_dx) < 0.15:
            self.pain_flee_dx = -1.0 if math.cos(self.angle) >= 0 else 1.0
        new_mx = int(mx + (dx_m / dist_m) * 45.0)
        new_my = int(my + (dy_m / dist_m) * 45.0)
        try:
            PlatformHelper.set_cursor_pos(new_mx, new_my)
        except Exception:
            pass

        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(850, 35, 1300, 50)

    def spawn_leaf_for_current_border(self):
        self.leaves = []
        pad = 42.0
        sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
        if self.border_edge == 0:   # Bottom border
            lx = random.uniform(sx + 350, sx + sw - 220); ly = sy + sh - pad
        elif self.border_edge == 1: # Right border
            lx = sx + sw - pad; ly = random.uniform(sy + 200, sy + sh - 280)
        elif self.border_edge == 2: # Top border
            lx = random.uniform(sx + 250, sx + sw - 350); ly = sy + pad
        else:                       # Left border
            lx = sx + pad; ly = random.uniform(sy + 280, sy + sh - 220)

        self.leaves.append({'x': lx, 'y': ly, 'health': 1.0, 'spawn': time.time(), 'approach': None})

    def update(self, now):
        try:
            phase_dt = max(0.0, min(0.1, now - self._last_phase_time))
            self._last_phase_time = now
            self.inch_phase += phase_dt * 5.2
            # 1. Interactive Mouse Click Detection on Caterpillar Body
            if self.stage in ["CATERPILLAR", "CATERPILLAR_EATING", "WALKING_TO_COCOON"]:
                is_click = False
                try:
                    if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'user32'):
                        is_click = (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) != 0
                except Exception:
                    pass

                mx, my = self.app.get_mouse_pos()
                hit_radius = 42.0 * self.scale
                is_hit = False
                for s in self.segments:
                    if math.hypot(mx - s['x'], my - s['y']) < hit_radius:
                        is_hit = True
                        break

                if is_click and is_hit and (now - self.last_pain_time > 1.8):
                    self.trigger_pain_reaction(mx, my, now)

            # End pain reaction after 1.6 seconds
            if self.pain_active and (now - self.pain_start > 1.6):
                self.pain_active = False

            # 2. Smooth Cocoon Descent from top of monitor on shimmering thread
            if self.cocoon_build_p > 0.05:
                target_cy = self.cocoon_y
                self.cocoon_descent_y += (target_cy - self.cocoon_descent_y) * 0.045

            # 3. Stage updates. A click interrupts eating so the caterpillar can
            # show pain and sprint away instead of chewing in place.
            if self.pain_active and self.stage in ["CATERPILLAR", "CATERPILLAR_EATING", "WALKING_TO_COCOON"]:
                if self.stage == "CATERPILLAR_EATING":
                    self.stage = "CATERPILLAR"
                self.update_caterpillar(now)
            elif self.stage == "CATERPILLAR":
                self.update_caterpillar(now)
            elif self.stage == "CATERPILLAR_EATING":
                self.update_caterpillar_eating(now)
            elif self.stage == "WALKING_TO_COCOON":
                self.update_walking_to_cocoon(now)
            elif self.stage == "COCOON_ENTERING":
                self.update_cocoon_entering(now)
            elif self.stage == "CHRYSALIS":
                self.update_chrysalis(now)
            elif self.stage == "EMERGENCE":
                self.update_emergence(now)
            elif self.stage == "FLYING":
                self.update_flying(now)
        except Exception as exc:
            self._report_runtime_error("update", exc)

    def _report_runtime_error(self, area, exc):
        """Keep one bad animation frame from killing the overlay and make it diagnosable."""
        signature = (area, type(exc).__name__)
        report_time = time.time()
        if signature != self._last_reported_error or report_time - self._last_error_report_time > 5.0:
            try:
                print(f"[Butterfly] {area} error: {type(exc).__name__}: {exc}")
                traceback.print_exc()
            except Exception:
                pass
            self._last_reported_error = signature
            self._last_error_report_time = report_time

    def _crawl_toward(self, target_x, target_y, now, base_speed=1.35):
        """Move with small inchworm pulses and let each body segment follow the head."""
        dt = max(0.0, min(0.05, now - self._last_crawl_time))
        self._last_crawl_time = now
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)
        if distance > 1.0:
            self.target_angle = math.atan2(dy, dx)

        angle_diff = (self.target_angle - self.angle + math.pi) % (2.0 * math.pi) - math.pi
        # Wider, smoother steering keeps the long body from folding into a
        # sharp corner when it changes from edge walking toward the nest.
        turn_alpha = 1.0 - math.exp(-4.0 * dt)
        self.angle += angle_diff * turn_alpha

        pulse = max(0.0, math.sin(self.inch_phase)) ** 2
        step = base_speed * (0.22 + 0.78 * pulse) * dt * 60.0
        # Prevent the head from overshooting a leaf or entrance and having to
        # turn around to reach it on the next frame.
        step = min(step, distance)
        self.x += math.cos(self.angle) * step
        self.y += math.sin(self.angle) * step

        head = self.segments[0]
        head.update(x=self.x, y=self.y, angle=self.angle)
        for i in range(1, self.num_segments):
            previous, current = self.segments[i - 1], self.segments[i]
            sx, sy = previous['x'] - current['x'], previous['y'] - current['y']
            segment_length = math.hypot(sx, sy)
            if segment_length > 1e-6:
                current['x'] = previous['x'] - sx / segment_length * self.seg_dist
                current['y'] = previous['y'] - sy / segment_length * self.seg_dist
                current['angle'] = math.atan2(sy, sx)
        return distance

    def update_caterpillar(self, now):
        if self.pain_active:
            # Startle sprint away from the click, then settle back into crawling.
            edge_pad = 42.0
            sx, _, sw, _ = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
            target_x = self.x + self.pain_flee_dx * 160.0
            target_x = max(sx + edge_pad, min(sx + sw - edge_pad, target_x))
            self._crawl_toward(target_x, self.y, now, self.crawl_speed * 2.7)
            return

        sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
        pad = 42.0

        if not self.leaves and self.leaves_eaten < self.total_leaves_needed:
            self.spawn_leaf_for_current_border()

        target_leaf = self.leaves[0] if self.leaves else None
        target_x, target_y = self.x, self.y
        is_targeting_leaf = False

        if target_leaf and target_leaf.get('health', 1.0) > 0.05:
            is_targeting_leaf = True
            leaf_dx, leaf_dy = target_leaf['x'] - self.x, target_leaf['y'] - self.y
            leaf_dist = math.hypot(leaf_dx, leaf_dy)
            # Stop at the leaf's edge with the head facing it; don't crawl over
            # the leaf and then reverse to start eating from behind.
            if leaf_dist <= 64.0 and target_leaf.get('approach') is None:
                unit = max(1.0, leaf_dist)
                bite_gap = 18.0 * self.scale
                target_leaf['approach'] = (
                    target_leaf['x'] - leaf_dx / unit * bite_gap,
                    target_leaf['y'] - leaf_dy / unit * bite_gap,
                )
            if target_leaf.get('approach') is not None:
                target_x, target_y = target_leaf['approach']
            else:
                target_x, target_y = target_leaf['x'], target_leaf['y']
        else:
            if self.border_edge == 0:   target_x = sx + sw - pad; target_y = sy + sh - pad
            elif self.border_edge == 1: target_x = sx + sw - pad; target_y = sy + pad
            elif self.border_edge == 2: target_x = sx + pad;      target_y = sy + pad
            else:                       target_x = sx + pad;      target_y = sy + sh - pad

        dist = math.hypot(target_x - self.x, target_y - self.y)

        # Eating arrival
        if is_targeting_leaf and dist <= 5.0:
            self.stage = "CATERPILLAR_EATING"
            self.eating_start = now
            self.current_leaf = self.leaves[0]
            if self.app.SOUND_ENABLED:
                play_audio(600, 30, 480, 40)
            return

        # Slow, grounded inchworm motion; reduce pace near a leaf.
        self._crawl_toward(target_x, target_y, now, self.crawl_speed * (0.52 if is_targeting_leaf and dist < 45.0 else 1.0))

        # Reached corner
        if not is_targeting_leaf and dist < 26.0:
            self.border_edge = (self.border_edge + 1) % 4
            if self.leaves_eaten >= self.total_leaves_needed:
                self.stage = "WALKING_TO_COCOON"
            else:
                self.spawn_leaf_for_current_border()

    def update_caterpillar_eating(self, now):
        eat_duration = 3.8
        elapsed = max(0.0, now - self.eating_start)
        p = min(1.0, elapsed / eat_duration)

        if self.current_leaf:
            self.current_leaf['health'] = max(0.0, 1.0 - p)

        # Proportional Cocoon Construction: Leaf eating builds the cocoon!
        prev_p = self.leaves_eaten / float(self.total_leaves_needed)
        next_p = (self.leaves_eaten + 1) / float(self.total_leaves_needed)
        self.cocoon_build_p = prev_p + (next_p - prev_p) * p

        # Crumbs falling
        if random.random() < 0.35 and self.current_leaf:
            lx = self.current_leaf['x'] + random.uniform(-6, 6)
            ly = self.current_leaf['y'] + random.uniform(-4, 4)
            self.chew_crumbs.append({
                'x': lx, 'y': ly, 'vy': random.uniform(0.6, 1.8),
                'life': 1.0, 'color': random.choice(["#84cc16", "#65a30d", "#4d7c0f"])
            })

        for c in self.chew_crumbs[:]:
            c['y'] += c['vy']
            c['life'] -= 0.04
            if c['life'] <= 0:
                self.chew_crumbs.remove(c)

        if p >= 1.0:
            self.leaves_eaten += 1
            self.leaves = []
            self.current_leaf = None
            if self.app.SOUND_ENABLED:
                play_audio(700, 40, 950, 50)

            if self.leaves_eaten >= self.total_leaves_needed:
                self.cocoon_build_p = 1.0
                self.stage = "WALKING_TO_COCOON"
            else:
                self.stage = "CATERPILLAR"
                self.border_edge = (self.border_edge + 1) % 4
                self.spawn_leaf_for_current_border()

    def update_walking_to_cocoon(self, now):
        self.cocoon_build_p = 1.0
        # Face the nest entrance toward the caterpillar's approach to avoid a
        # sharp turn on top of the cocoon at the last moment.
        entrance_x, entrance_y = self._cocoon_mouth()

        dist = self._crawl_toward(entrance_x, entrance_y, now, self.crawl_speed)

        if dist < 12.0:
            self._begin_cocoon_entry(now)
            if self.app.SOUND_ENABLED:
                play_audio(440, 50, 660, 60)

    def _cocoon_mouth(self):
        cx, cy = self.cocoon_x, self.cocoon_descent_y
        rx = max(4.0, 29.0 * self.scale * max(0.12, self.cocoon_build_p) * 0.82)
        ry = max(4.0, 27.0 * self.scale * max(0.12, self.cocoon_build_p) * 0.82)
        dx, dy = self.x - cx, self.y - cy
        norm = math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
        if norm < 1e-4:
            dx, dy, norm = 0.0, 1.0, 1.0 / ry
        return cx + dx / norm, cy + dy / norm

    def _begin_cocoon_entry(self, now):
        self.stage = "COCOON_ENTERING"
        self.caterpillar_entry_p = 0.0
        self.entry_start_time = now
        self.entry_mouth_x, self.entry_mouth_y = self._cocoon_mouth()
        # Carry the approach heading through the opening so the caterpillar
        # does not pivot sharply at the lip.
        dx, dy = math.cos(self.angle), math.sin(self.angle)
        to_mouth_x, to_mouth_y = self.entry_mouth_x - self.x, self.entry_mouth_y - self.y
        if dx * to_mouth_x + dy * to_mouth_y < 0.0:
            length = max(1.0, math.hypot(to_mouth_x, to_mouth_y))
            dx, dy = to_mouth_x / length, to_mouth_y / length
        self.entry_direction = (dx, dy)
        self.entry_hidden_segments.clear()

    def update_cocoon_entering(self, now):
        # Keep advancing the real head/segment chain through the entrance.
        # The tail follows the same curved path; it is never redrawn as a stack.
        p = min(1.0, max(0.0, now - self.entry_start_time) / self._entry_duration())
        self.caterpillar_entry_p = p
        dx, dy = self.entry_direction
        travel = self.seg_dist * (self.num_segments + 2)
        target_x = self.entry_mouth_x + dx * travel
        target_y = self.entry_mouth_y + dy * travel
        self._crawl_toward(target_x, target_y, now, self.crawl_speed)
        for idx, seg in enumerate(self.segments):
            if ((seg['x'] - self.entry_mouth_x) * dx
                    + (seg['y'] - self.entry_mouth_y) * dy) > 3.0:
                self.entry_hidden_segments.add(idx)
        if p >= 1.0:
            self.caterpillar_entry_p = 1.0
            self.stage = "CHRYSALIS"
            self.chrysalis_start = now
            if self.app.SOUND_ENABLED:
                play_audio(520, 60, 780, 80)

    def _entry_duration(self):
        crawl_px_per_second = max(18.0, self.crawl_speed * 30.0)
        return max(2.2, (self.seg_dist * (self.num_segments + 2)) / crawl_px_per_second)

    def update_chrysalis(self, now):
        if now - self.chrysalis_start > 4.5:
            self.stage = "EMERGENCE"
            self.emergence_start = now
            self.wing_expansion = 0.15
            if self.app.SOUND_ENABLED:
                play_audio(550, 50, 880, 70)

    def update_emergence(self, now):
        # Wall clock corrections can make elapsed briefly negative; fractional
        # powers of a negative float become complex and crash Tk canvas drawing.
        elapsed = max(0.0, now - self.emergence_start)
        p = min(1.0, elapsed / 3.8)
        self.wing_expansion = 0.15 + 0.85 * (p ** 1.3)
        self.flap_phase = math.sin(elapsed * 4.0) * 0.4
        if p >= 1.0:
            self.stage = "FLYING"
            self.free_flight_timer = now
            self.flight_timer = now
            self.x = self.cocoon_x
            self.y = self.cocoon_descent_y
            self.angle = -math.pi / 2
            if self.app.SOUND_ENABLED:
                play_audio(600, 50, 900, 70)

    def update_flying(self, now):
        # === REALISTIC BUTTERFLY FLIGHT DYNAMICS (FLUTTER & GLIDE) ===
        # 1.5s fluttering wing flap, then 2.3s soaring straight with wings spread open!
        cycle_time = (now - self.flight_timer) % 3.8
        if cycle_time < 1.5:
            # Flutter phase
            self.is_gliding = False
            flutter_t = cycle_time / 1.5
            self.flap_phase = math.sin(flutter_t * math.pi * 6.0)
            lift = -0.6 * math.sin(flutter_t * math.pi * 6.0)
            spd = 4.2 * self.flight_speed
        else:
            # Glide phase: Wings spread open, soaring straight forward!
            self.is_gliding = True
            self.flap_phase = 0.0
            lift = 0.1
            spd = 3.2 * self.flight_speed

        mx, my = self.app.get_mouse_pos()
        dx = (mx + math.sin(now * 0.7) * 90.0) - self.x
        dy = (my + math.cos(now * 0.6) * 70.0) - self.y
        dist = math.hypot(dx, dy)

        if dist > 20.0:
            self.target_angle = math.atan2(dy, dx)
        diff = self.target_angle - self.angle
        while diff < -math.pi: diff += math.pi * 2
        while diff > math.pi: diff -= math.pi * 2
        turn_rate = 0.05 if self.is_gliding else 0.09
        self.angle += diff * turn_rate

        self.vx = math.cos(self.angle) * spd
        self.vy = math.sin(self.angle) * spd + lift
        self.x += self.vx
        self.y += self.vy

        sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
        pad = 40.0
        if self.x < sx + pad: self.x = sx + pad; self.vx = abs(self.vx)
        if self.x > sx + sw - pad: self.x = sx + sw - pad; self.vx = -abs(self.vx)
        if self.y < sy + pad: self.y = sy + pad; self.vy = abs(self.vy)
        if self.y > sy + sh - pad: self.y = sy + sh - pad; self.vy = -abs(self.vy)

        # Shimmering Fairy Dust / Stardust particle trail
        if (random.random() < 0.50 or not self.is_gliding) and len(self.trail_particles) < 40:
            part_col = random.choice(self.theme.get('particle_colors', ['#ffffff']))
            self.trail_particles.append({
                'x': self.x + random.uniform(-4, 4),
                'y': self.y + random.uniform(-3, 3),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(0.15, 0.8),
                'size': random.uniform(1.8, 3.8),
                'life': 1.0,
                'color': part_col
            })
        for p in self.trail_particles[:]:
            p['x'] += p.get('vx', 0.0)
            p['y'] += p.get('vy', 0.4)
            p['life'] -= 0.032
            if p['life'] <= 0:
                self.trail_particles.remove(p)

    def draw(self, canvas):
        canvas.delete("butterfly_creature")
        try:
            # Draw descending silk cocoon chamber
            if self.cocoon_build_p > 0.05 and self.stage in ["CATERPILLAR", "CATERPILLAR_EATING", "WALKING_TO_COCOON", "COCOON_ENTERING", "CHRYSALIS", "EMERGENCE"]:
                self.draw_cocoon_chamber(canvas)

            if self.stage in ["CATERPILLAR", "CATERPILLAR_EATING", "WALKING_TO_COCOON"]:
                self.draw_caterpillar(canvas)
            elif self.stage == "COCOON_ENTERING":
                self.draw_caterpillar_entering(canvas)
            elif self.stage == "CHRYSALIS":
                self.draw_chrysalis(canvas)
            elif self.stage == "EMERGENCE":
                self.draw_emergence(canvas)
            elif self.stage == "FLYING":
                self.draw_flying(canvas)

            # Draw sleek cyber on-screen toast banner if active
            if self.toast_text and time.time() < self.toast_until:
                self._draw_toast_banner(canvas)
        except Exception as exc:
            self._report_runtime_error("draw", exc)

    def draw_caterpillar(self, canvas):
        # 1. Fresh leaves
        for l in self.leaves:
            lx, ly = l['x'], l['y']
            h_pct = max(0.05, l.get('health', 1.0))
            w_blade = 22.0 * h_pct
            h_blade = 11.0 * h_pct

            leaf_pts = [
                lx - w_blade, ly,
                lx - w_blade * 0.4, ly - h_blade,
                lx + w_blade * 0.6, ly - h_blade * 0.8,
                lx + w_blade * 1.1, ly,
                lx + w_blade * 0.6, ly + h_blade * 0.8,
                lx - w_blade * 0.4, ly + h_blade
            ]
            canvas.create_polygon(leaf_pts, fill="#84cc16", outline="#4d7c0f", width=1.4, smooth=True, tags="butterfly_creature")
            canvas.create_line(lx - w_blade, ly, lx + w_blade * 0.9, ly, fill="#4d7c0f", width=1.1, tags="butterfly_creature")

        for c in self.chew_crumbs:
            canvas.create_oval(c['x']-1.5, c['y']-1.5, c['x']+1.5, c['y']+1.5,
                              fill=c['color'], outline="", tags="butterfly_creature")

        # 2. Smooth Looper Arch along Segment Normal
        # Arc height peaks in middle segments during inching
        tau = self.inch_phase % (math.pi * 2)
        arch_wave = max(0.0, math.sin(tau))

        chew_bob = math.sin((time.time() - self.eating_start) * 16.0) * 2.5 if self.stage == "CATERPILLAR_EATING" else 0.0

        # Defensive Pain Startle Thrash
        pain_shake = math.sin((time.time() - self.pain_start) * 28.0) * 5.0 if self.pain_active else 0.0

        seg_render_coords = []
        for i in range(self.num_segments):
            seg = self.segments[i]
            s_frac = i / float(self.num_segments - 1)
            # Normal perpendicular to segment orientation (pointing upwards/away from ground)
            s_ang = seg['angle']
            norm_x = math.sin(s_ang)
            norm_y = -math.cos(s_ang)

            # Arch lift
            # Keep the abdomen close to the surface with only a gentle inching ripple.
            h = math.sin(s_frac * math.pi) * (0.25 * self.scale * arch_wave)
            # A small traveling side-to-side wave travels from head to tail, like
            # an inchworm contracting one body segment after another.
            wobble = math.sin(self.inch_phase * 1.55 - i * 0.62) * (0.45 + 0.55 * s_frac) * self.scale

            px = seg['x'] + norm_x * (h + wobble)
            py = seg['y'] + norm_y * (h + wobble)

            if i == 0:
                px += math.cos(s_ang) * chew_bob + norm_x * pain_shake
                py += math.sin(s_ang) * chew_bob + norm_y * pain_shake
            seg_render_coords.append((px, py, s_ang, norm_x, norm_y))

        # Anal clasper at tail
        tx_i, ty_i, t_ang, t_nx, t_ny = seg_render_coords[-1]
        canvas.create_line(tx_i, ty_i, tx_i - math.cos(t_ang) * 4.5 - t_nx * 2.5, ty_i - math.sin(t_ang) * 4.5 - t_ny * 2.5,
                           fill="#14532d", width=2.4 * self.scale, tags="butterfly_creature")
        canvas.create_line(tx_i, ty_i, tx_i - math.cos(t_ang) * 4.5 + t_nx * 2.5, ty_i - math.sin(t_ang) * 4.5 + t_ny * 2.5,
                           fill="#14532d", width=2.4 * self.scale, tags="butterfly_creature")

        # 4. Plump Segments (Fixed Distance - NO Springing!)
        for i in reversed(range(self.num_segments)):
            sx_i, sy_i, _, _, _ = seg_render_coords[i]
            pulse = 1.0 + 0.055 * math.sin(self.inch_phase * 1.35 - i * 0.7)
            r = (7.4 - abs(i - 5) * 0.16) * self.scale * pulse
            col = "#22c55e" if i % 2 == 0 else "#16a34a"
            border_col = "#15803d"
            canvas.create_oval(sx_i - r, sy_i - r, sx_i + r, sy_i + r,
                               fill=col, outline=border_col, width=1.5, tags="butterfly_creature")
            canvas.create_arc(sx_i - r*0.75, sy_i - r*0.75, sx_i + r*0.75, sy_i + r*0.75,
                              start=45, extent=110, outline="#86efac", style="arc", width=1.4, tags="butterfly_creature")
            hi_x = sx_i + math.sin(seg_render_coords[i][2]) * r * 0.42
            hi_y = sy_i - math.cos(seg_render_coords[i][2]) * r * 0.42
            canvas.create_oval(hi_x - 1.4, hi_y - 1.1, hi_x + 1.4, hi_y + 1.1,
                               fill="#bbf7d0", outline="", tags="butterfly_creature")

        # Draw feet in front of the body so every pair remains visible on dark desktops.
        # Three thoracic pairs plus seven small abdominal proleg pairs follow the same gait.
        for seg_idx in range(1, 11):
            sx_i, sy_i, s_ang, norm_x, norm_y = seg_render_coords[seg_idx]
            body_r = (7.4 - abs(seg_idx - 5) * 0.16) * self.scale
            forward_x, forward_y = math.cos(s_ang), math.sin(s_ang)
            down_x, down_y = -norm_x, -norm_y
            is_true_leg = seg_idx <= 3
            leg_length = (8.0 if is_true_leg else 5.4) * self.scale
            leg_width = (2.0 if is_true_leg else 1.8) * self.scale
            for side in (-1, 1):
                phase = self.inch_phase * 1.4 + (seg_idx + (side > 0) * 0.5) * math.pi
                swing = math.sin(phase) * (2.4 if is_true_leg else 1.3) * self.scale
                lift = max(0.0, math.cos(phase)) * (2.2 if is_true_leg else 1.2) * self.scale
                root_x = sx_i + down_x * body_r * 0.76 + forward_x * side * 2.0 * self.scale
                root_y = sy_i + down_y * body_r * 0.76 + forward_y * side * 2.0 * self.scale
                foot_x = root_x + down_x * (leg_length - lift) + forward_x * (side * 2.5 * self.scale + swing)
                foot_y = root_y + down_y * (leg_length - lift) + forward_y * (side * 2.5 * self.scale + swing)
                canvas.create_line(root_x, root_y, foot_x, foot_y,
                                   fill="#14532d" if is_true_leg else "#166534",
                                   width=leg_width, capstyle="round", tags="butterfly_creature")
                pad_r = (1.2 if is_true_leg else 1.35) * self.scale
                canvas.create_oval(foot_x - pad_r, foot_y - pad_r * 0.72,
                                   foot_x + pad_r, foot_y + pad_r * 0.72,
                                   fill="#a3e635" if is_true_leg else "#84cc16",
                                   outline="#365314", width=0.7, tags="butterfly_creature")

        # 5. Prominent Rounded Head Capsule & Adorable Face
        hx, hy, h_ang, h_nx, h_ny = seg_render_coords[0]
        cos_a = math.cos(h_ang)
        sin_a = math.sin(h_ang)
        hr = 9.5 * self.scale
        canvas.create_oval(hx - hr, hy - hr, hx + hr, hy + hr,
                           fill="#4d7c0f", outline="#14532d", width=1.8, tags="butterfly_creature")

        # Rounded snout
        snout_dist = 4.0 * self.scale
        snout_x = hx + cos_a * snout_dist
        snout_y = hy + sin_a * snout_dist
        canvas.create_oval(snout_x - 5.0*self.scale, snout_y - 4.2*self.scale,
                           snout_x + 5.0*self.scale, snout_y + 4.2*self.scale,
                           fill="#65a30d", outline="#365314", width=1.1, tags="butterfly_creature")

        # Chewing mandibles (snaps when eating or pained)
        jaw_spread = 2.4 + (math.sin(time.time() * 20.0) * 2.2 if (self.stage == "CATERPILLAR_EATING" or self.pain_active) else 0.0)
        canvas.create_polygon([
            snout_x + cos_a * 2.2 - h_nx * jaw_spread, snout_y + sin_a * 2.2 - h_ny * jaw_spread,
            snout_x + cos_a * 5.8, snout_y + sin_a * 5.8,
            snout_x + cos_a * 2.2 + h_nx * jaw_spread, snout_y + sin_a * 2.2 + h_ny * jaw_spread
        ], fill="#365314", outline="#1a2e05", width=0.9, tags="butterfly_creature")

        # Cute shiny eyes on LATERAL sides of the head (NOT overlapping antennae!)
        eye_lat = 5.6 * self.scale
        eye_fwd = 1.8 * self.scale
        for side in [-1, 1]:
            ex = hx + cos_a * eye_fwd + side * h_nx * eye_lat
            ey = hy + sin_a * eye_fwd + side * h_ny * eye_lat
            canvas.create_oval(ex - 2.8, ey - 2.8, ex + 2.8, ey + 2.8,
                               fill="#ffffff", outline="#14532d", width=0.9, tags="butterfly_creature")
            pupil_ox = cos_a * 0.5
            pupil_oy = sin_a * 0.5
            canvas.create_oval(ex + pupil_ox - 1.6, ey + pupil_oy - 1.6,
                               ex + pupil_ox + 1.6, ey + pupil_oy + 1.6,
                               fill="#09090b", outline="", tags="butterfly_creature")
            canvas.create_oval(ex - 1.4, ey - 1.4, ex - 0.3, ey - 0.3,
                               fill="#ffffff", outline="", tags="butterfly_creature")

        # Antennae feelers rooted on DORSAL CROWN (forehead), clearly above & separate from eyes!
        ant_len = 12.0 * self.scale
        for side in [-1, 1]:
            base_x = hx + cos_a * (6.5 * self.scale) + side * h_nx * (2.2 * self.scale)
            base_y = hy + sin_a * (6.5 * self.scale) + side * h_ny * (2.2 * self.scale)
            mid_x = base_x + cos_a * (ant_len * 0.55) + side * h_nx * (4.5 * self.scale)
            mid_y = base_y + sin_a * (ant_len * 0.55) + side * h_ny * (4.5 * self.scale)
            tip_x = base_x + cos_a * ant_len + side * h_nx * (7.2 * self.scale)
            tip_y = base_y + sin_a * ant_len + side * h_ny * (7.2 * self.scale)

            canvas.create_line(base_x, base_y, mid_x, mid_y, tip_x, tip_y,
                               fill="#a3e635", width=1.8 * self.scale, smooth=True, tags="butterfly_creature")
            canvas.create_oval(tip_x - 2.0, tip_y - 2.0, tip_x + 2.0, tip_y + 2.0,
                               fill="#fde047", outline="#ca8a04", width=0.9, tags="butterfly_creature")

        # Pain / Startle Sweat Spark Indicator
        if self.pain_active:
            canvas.create_text(hx, hy - 18.0, text="💢", font=("Segoe UI Emoji", 14), fill="#ef4444", tags="butterfly_creature")

    def draw_caterpillar_entering(self, canvas):
        """Draw the live articulated body as it crawls into the nest mouth."""
        cx, cy = self.cocoon_x, self.cocoon_descent_y
        p = min(1.0, max(0.12, self.cocoon_build_p))
        h = 54.0 * self.scale * p
        w = 29.0 * self.scale * p
        if self.stage == "COCOON_ENTERING":
            entrance_x, entrance_y = self.entry_mouth_x, self.entry_mouth_y
        else:
            entrance_x, entrance_y = self._cocoon_mouth()
        rendered = []
        for seg_idx in reversed(range(self.num_segments)):
            seg = self.segments[seg_idx]
            angle = seg.get('angle', self.angle)
            nx, ny = math.sin(angle), -math.cos(angle)
            wobble = math.sin(self.inch_phase * 1.55 - seg_idx * 0.62) * 0.8 * self.scale
            sx, sy = seg['x'] + nx * wobble, seg['y'] + ny * wobble

            # The woven shell occludes the body inside it; only the short part
            # actually passing through the opening remains visible.
            if seg_idx in self.entry_hidden_segments:
                continue
            ex = (sx - cx) / max(1.0, w * 0.86)
            ey = (sy - cy) / max(1.0, h * 0.48)
            inside_shell = ex * ex + ey * ey < 1.0
            at_mouth = math.hypot((sx - entrance_x) / max(1.0, 14.0 * self.scale),
                                  (sy - entrance_y) / max(1.0, 10.0 * self.scale)) < 1.15
            if inside_shell and not at_mouth:
                continue

            r = (7.4 - abs(seg_idx - 5) * 0.16) * self.scale
            col = "#22c55e" if seg_idx % 2 == 0 else "#16a34a"
            canvas.create_oval(sx - r, sy - r, sx + r, sy + r,
                               fill=col, outline="#15803d", width=1.4, tags="butterfly_creature")
            canvas.create_arc(sx-r*.72, sy-r*.72, sx+r*.72, sy+r*.72,
                              start=35, extent=115, outline="#86efac", width=1.1,
                              style="arc", tags="butterfly_creature")
            canvas.create_oval(sx - 1.5, sy - 1.2, sx + 1.5, sy + 1.2,
                               fill="#fef08a", outline="#f59e0b", width=0.6, tags="butterfly_creature")
            rendered.append((seg_idx, sx, sy, angle, nx, ny, r, inside_shell))

        # Keep the feet stepping as the rear follows the head into the opening.
        for idx, x, y, angle, nx, ny, radius, in_shell in rendered:
            if in_shell:
                continue
            for side in (-1, 1):
                phase = self.inch_phase * 1.4 + (idx + (side > 0) * .5) * math.pi
                swing = math.sin(phase) * 1.5 * self.scale
                fx = x - nx * (radius + 3.0*self.scale) + math.cos(angle) * (side*2.0 + swing)
                fy = y + math.cos(angle) * (radius + 3.0*self.scale) + math.sin(angle) * (side*2.0 + swing)
                canvas.create_line(x - nx*radius*.7, y + math.cos(angle)*radius*.7, fx, fy,
                                   fill="#166534", width=1.4*self.scale,
                                   capstyle="round", tags="butterfly_creature")

        head = next((item for item in rendered if item[0] == 0), None)
        if head:
            _, hx, hy, angle, nx, ny, _, _ = head
            for side in (-1, 1):
                ex = hx + math.cos(angle)*3*self.scale + nx*side*3*self.scale
                ey = hy + math.sin(angle)*3*self.scale + ny*side*3*self.scale
                canvas.create_oval(ex-1.8, ey-1.8, ex+1.8, ey+1.8,
                                   fill="#fef3c7", outline="#365314", width=.7,
                                   tags="butterfly_creature")

    def draw_cocoon_chamber(self, canvas):
        """Exquisite Woven Silk Cocoon Chamber:
        - Descends on a shimmering silk thread from the monitor ceiling (like spider silk).
        - Connects 100% seamlessly to the thread with ZERO GAP!
        - Theme-matched silk shell, golden/iridescent weave ribs and glowing entrance collar."""
        cx, cy = self.cocoon_x, self.cocoon_descent_y
        top_y = self.app.screen_y

        p = min(1.0, max(0.12, self.cocoon_build_p))
        w = 29.0 * self.scale * p
        h = 54.0 * self.scale * p

        shell_col = self.theme.get('cocoon_shell', '#0c4a6e')
        accent_col = self.theme.get('cocoon_accent', '#38bdf8')
        weave_col = self.theme.get('cocoon_weave', '#7dd3fc')
        border_col = self.theme.get('border', '#021a2f')

        # 1. Shimmering Silk Thread connects SEAMLESSLY to the top tip of the cocoon (ZERO GAP!)
        cocoon_top_y = cy - h/2
        canvas.create_line(cx, top_y, cx, cocoon_top_y, fill="#f8fafc", width=1.8, tags="butterfly_creature")
        canvas.create_line(cx - 2, top_y, cx + 2, top_y + 12, fill="#e2e8f0", width=1.0, tags="butterfly_creature")
        canvas.create_oval(cx - 4, top_y - 2, cx + 4, top_y + 4, fill="#ffffff", outline="#cbd5e1", width=1.0, tags="butterfly_creature")

        # 2. Outer Silk Shell with Theme-Matched Weave Threads
        nest_shape = [
            cx, cy-h*.50, cx+w*.48, cy-h*.44, cx+w*.84, cy-h*.22,
            cx+w, cy+h*.06, cx+w*.76, cy+h*.37, cx+w*.38, cy+h*.49,
            cx, cy+h*.52, cx-w*.38, cy+h*.49, cx-w*.76, cy+h*.37,
            cx-w, cy+h*.06, cx-w*.84, cy-h*.22, cx-w*.48, cy-h*.44
        ]
        canvas.create_polygon(nest_shape, smooth=True, fill=shell_col, outline=border_col,
                              width=2.0, tags="butterfly_creature")
        canvas.create_oval(cx-w*.78, cy-h*.39, cx+w*.78, cy+h*.34,
                           fill=accent_col, outline=weave_col, width=1.2,
                           tags="butterfly_creature")

        # Layered horizontal silk strands crossed by fine diagonals
        for deg in [-40, -20, 0, 20, 40]:
            r_y = cy + (deg / 50.0) * (h * 0.35)
            r_w = w * 0.75 * math.cos(math.radians(deg))
            canvas.create_arc(cx - r_w, r_y - 4, cx + r_w, r_y + 4,
                              start=20, extent=140, outline=weave_col, width=1.5, style="arc", tags="butterfly_creature")
        for row in range(1, 8):
            yy = cy - h * 0.39 + row * h * 0.105
            normalized = (yy - cy) / (h * 0.5)
            half_w = w * 0.78 * math.sqrt(max(0.0, 1.0 - normalized * normalized))
            if half_w < 2:
                continue
            wave = h * 0.025
            canvas.create_line(cx - half_w, yy, cx - half_w * 0.35, yy - wave,
                               cx + half_w * 0.35, yy + wave, cx + half_w, yy,
                               fill=weave_col if row % 2 else accent_col, width=1.35,
                               smooth=True, tags="butterfly_creature")
        for side in (-1, 1):
            for strand in range(4):
                start_y = cy - h * 0.38 + strand * h * 0.19
                end_y = start_y + h * 0.30
                canvas.create_line(cx + side * w * 0.66, start_y,
                                   cx + side * w * 0.30, (start_y + end_y) / 2,
                                   cx - side * w * 0.12, end_y,
                                   fill=weave_col, width=1.0, smooth=True,
                                   tags="butterfly_creature")

        # 3. Exquisite 3D Entrance Opening Collar
        if self.stage in ["CATERPILLAR", "CATERPILLAR_EATING", "WALKING_TO_COCOON", "COCOON_ENTERING"]:
            hole_w = 13.0 * self.scale * p
            hole_h = 9.0 * self.scale * p
            if self.stage == "COCOON_ENTERING":
                entrance_x, entrance_y = self.entry_mouth_x, self.entry_mouth_y
            else:
                entrance_x, entrance_y = self._cocoon_mouth()
            # Glowing theme-accented outer collar
            canvas.create_oval(entrance_x - hole_w*1.2, entrance_y - hole_h*1.2, entrance_x + hole_w*1.2, entrance_y + hole_h*1.2,
                               fill=shell_col, outline=weave_col, width=2.2, tags="butterfly_creature")
            # Deep dark interior entrance
            canvas.create_oval(entrance_x - hole_w, entrance_y - hole_h, entrance_x + hole_w, entrance_y + hole_h,
                               fill="#030712", outline=accent_col, width=1.2, tags="butterfly_creature")

            # Draw entering caterpillar body segments into the dark hole
            if self.stage == "COCOON_ENTERING":
                self.draw_caterpillar_entering(canvas)
                # Front half collar lip drawn OVER the entering segments for true 3D depth!
                canvas.create_arc(entrance_x - hole_w*1.2, entrance_y - hole_h*1.2, entrance_x + hole_w*1.2, entrance_y + hole_h*1.2,
                                  start=180, extent=180, outline=weave_col, width=2.4, style="arc", tags="butterfly_creature")

    def draw_chrysalis(self, canvas):
        cx, cy = self.cocoon_x, self.cocoon_descent_y
        now = time.time()
        pulse = 0.5 + 0.5 * math.sin(now * 2.4)
        rx = (8.5 + pulse * 1.5) * self.scale
        ry = (15.5 + pulse * 2.0) * self.scale
        accent_col = self.theme.get('accent', '#38bdf8')
        glow_col = self.theme.get('glow', '#7dd3fc')
        canvas.create_oval(cx-rx, cy-ry, cx+rx, cy+ry,
                           fill=accent_col, outline=glow_col, width=1.4,
                           tags="butterfly_creature")
        canvas.create_arc(cx-rx*.72, cy-ry*.74, cx+rx*.72, cy+ry*.74,
                          start=35, extent=115, outline="#ffffff", width=1.1,
                          style="arc", tags="butterfly_creature")

    def draw_emergence(self, canvas):
        cx, cy = self.cocoon_x, self.cocoon_descent_y
        self.draw_chrysalis(canvas)
        # Wing growth begins at pupa center
        self._render_butterfly_wings(canvas, cx, cy, 0.0, self.wing_expansion, self.flap_phase)

    def draw_flying(self, canvas):
        for p in self.trail_particles:
            r = max(0.6, p.get('size', 2.0) * p['life'])
            canvas.create_oval(p['x']-r, p['y']-r, p['x']+r, p['y']+r,
                              fill=p['color'], outline="", tags="butterfly_creature")
        self._render_butterfly_wings(canvas, self.x, self.y, self.angle, 1.0, self.flap_phase)

    def _render_butterfly_wings(self, canvas, cx, cy, angle, expansion, flap):
        """Breathtaking Swallowtail Butterfly Rendering:
        - Scalloped double-lobed forewings with dark velvet borders & submarginal pearl spots.
        - Signature Swallowtail hindwings with elegant curved streamer tails & concentric ocelli!
        - Breathing luminous discal cell with structural gradient radiance.
        - Radiating branching venation patterns across both wings.
        - Slender segmented abdomen, multifaceted compound eyes & graceful curved antennae with golden clubs."""
        ux = math.cos(angle)
        uy = math.sin(angle)
        vx = -math.sin(angle)
        vy = math.cos(angle)

        def pt(lx, ly):
            return (cx + lx * ux + ly * vx, cy + lx * uy + ly * vy)

        now = time.time()
        if self.is_gliding and self.stage == "FLYING":
            f_scale_fw = 0.98 + 0.02 * math.sin(now * 2.5)
            f_scale_hw = 0.96 + 0.03 * math.sin(now * 2.5 - 0.22)
        else:
            f_scale_fw = max(0.18, abs(math.cos(flap * 3.14159)))
            f_scale_hw = max(0.18, abs(math.cos((flap - 0.22) * 3.14159)))

        s = self.scale * expansion

        pri_col = self.theme.get('primary', '#0284c7')
        sec_col = self.theme.get('secondary', '#0369a1')
        accent_col = self.theme.get('accent', '#38bdf8')
        glow_col = self.theme.get('glow', '#7dd3fc')
        border_col = self.theme.get('border', '#030712')
        irid_col = self.theme.get('iridescent', '#cffafe')
        spot_col = self.theme.get('spots', '#ffffff')

        # =========================================================================
        # 1. HINDWINGS (Swallowtail Scalloped Wings with Streamer Tails & Ocelli)
        # =========================================================================
        for side in [-1, 1]:
            # Hindwing base & scalloped lobes with graceful swallowtail streamer!
            hw_pts = [
                pt(-2.0 * s, side * 3.0 * s),
                pt(-5.0 * s, side * 14.0 * s * f_scale_hw),
                pt(-10.0 * s, side * 22.0 * s * f_scale_hw),
                pt(-16.0 * s, side * 26.0 * s * f_scale_hw),
                pt(-21.0 * s, side * 24.5 * s * f_scale_hw),
                # Signature Swallowtail Streamer / Tail:
                pt(-28.5 * s, side * 28.0 * s * f_scale_hw),
                pt(-26.0 * s, side * 21.0 * s * f_scale_hw),
                pt(-23.0 * s, side * 15.0 * s * f_scale_hw),
                pt(-18.0 * s, side * 8.0 * s * f_scale_hw),
                pt(-11.0 * s, side * 3.0 * s)
            ]
            canvas.create_polygon([c for p in hw_pts for c in p], fill=border_col, outline="", smooth=True, tags="butterfly_creature")

            # Core vibrant wing field
            hw_inner_pts = [
                pt(-3.0 * s, side * 4.0 * s),
                pt(-6.0 * s, side * 13.0 * s * f_scale_hw),
                pt(-10.0 * s, side * 20.0 * s * f_scale_hw),
                pt(-15.0 * s, side * 23.5 * s * f_scale_hw),
                pt(-19.5 * s, side * 21.5 * s * f_scale_hw),
                pt(-21.0 * s, side * 13.5 * s * f_scale_hw),
                pt(-16.5 * s, side * 7.5 * s * f_scale_hw),
                pt(-10.0 * s, side * 3.5 * s)
            ]
            canvas.create_polygon([c for p in hw_inner_pts for c in p], fill=sec_col, outline="", smooth=True, tags="butterfly_creature")

            # Luminous inner radiance
            hw_glow_pts = [
                pt(-4.0 * s, side * 4.5 * s),
                pt(-7.5 * s, side * 12.0 * s * f_scale_hw),
                pt(-12.5 * s, side * 15.0 * s * f_scale_hw),
                pt(-15.0 * s, side * 8.0 * s * f_scale_hw),
                pt(-9.0 * s, side * 4.0 * s)
            ]
            canvas.create_polygon([c for p in hw_glow_pts for c in p], fill=accent_col, outline="", smooth=True, tags="butterfly_creature")

            # Radiating branching veins on hindwing
            for end_x, end_y in [(-9, 19), (-15, 23), (-20, 21), (-20, 14)]:
                start = pt(-3.5 * s, side * 4.5 * s)
                end = pt(end_x * s, side * end_y * s * f_scale_hw)
                canvas.create_line(start[0], start[1], end[0], end[1],
                                   fill=irid_col, width=max(0.7, 1.0 * s),
                                   smooth=True, tags="butterfly_creature")

            # Multi-layer concentric Eye-Spot (Ocellus)
            eyespot_x, eyespot_y = pt(-16.5 * s, side * 17.5 * s * f_scale_hw)
            es_r = 2.8 * s
            canvas.create_oval(eyespot_x - es_r, eyespot_y - es_r, eyespot_x + es_r, eyespot_y + es_r,
                               fill=border_col, outline="", tags="butterfly_creature")
            canvas.create_oval(eyespot_x - es_r*0.7, eyespot_y - es_r*0.7, eyespot_x + es_r*0.7, eyespot_y + es_r*0.7,
                               fill=accent_col, outline="", tags="butterfly_creature")
            canvas.create_oval(eyespot_x - es_r*0.35, eyespot_y - es_r*0.35, eyespot_x + es_r*0.35, eyespot_y + es_r*0.35,
                               fill="#0f172a", outline="", tags="butterfly_creature")
            canvas.create_oval(eyespot_x - es_r*0.2 - 0.4, eyespot_y - es_r*0.2 - 0.4, eyespot_x - es_r*0.2 + 0.5, eyespot_y - es_r*0.2 + 0.5,
                               fill="#ffffff", outline="", tags="butterfly_creature")

            # Submarginal pearls along hindwing border
            for mx_k, my_k in [(-11, 23), (-16, 25), (-22, 23), (-22, 17)]:
                hx_m, hy_m = pt(mx_k * s, side * my_k * s * f_scale_hw)
                mr = 1.3 * s
                canvas.create_oval(hx_m - mr, hy_m - mr, hx_m + mr, hy_m + mr,
                                   fill=spot_col, outline="", tags="butterfly_creature")

        # =========================================================================
        # 2. FOREWINGS (Aerodynamic Scalloped Wings with Breathing Discal Cell)
        # =========================================================================
        for side in [-1, 1]:
            # Outer dark velvet frame
            fw_pts = [
                pt(3.0 * s, side * 2.0 * s),
                pt(9.0 * s, side * 14.0 * s * f_scale_fw),
                pt(16.0 * s, side * 26.0 * s * f_scale_fw),
                pt(20.0 * s, side * 38.0 * s * f_scale_fw),
                pt(18.5 * s, side * 43.0 * s * f_scale_fw),
                pt(13.5 * s, side * 42.5 * s * f_scale_fw),
                pt(10.5 * s, side * 40.5 * s * f_scale_fw),
                pt(5.5 * s,  side * 39.0 * s * f_scale_fw),
                pt(2.5 * s,  side * 36.5 * s * f_scale_fw),
                pt(-3.0 * s, side * 33.5 * s * f_scale_fw),
                pt(-6.5 * s, side * 29.5 * s * f_scale_fw),
                pt(-9.5 * s, side * 20.0 * s * f_scale_fw),
                pt(-4.0 * s, side * 3.0 * s)
            ]
            canvas.create_polygon([c for p in fw_pts for c in p], fill=border_col, outline="", smooth=True, tags="butterfly_creature")

            # Vibrant primary wing field
            fw_inner_pts = [
                pt(3.5 * s, side * 3.0 * s),
                pt(8.5 * s, side * 13.5 * s * f_scale_fw),
                pt(14.5 * s, side * 24.5 * s * f_scale_fw),
                pt(17.5 * s, side * 35.0 * s * f_scale_fw),
                pt(14.0 * s, side * 38.0 * s * f_scale_fw),
                pt(9.5 * s,  side * 37.0 * s * f_scale_fw),
                pt(4.5 * s,  side * 35.0 * s * f_scale_fw),
                pt(-1.5 * s, side * 30.0 * s * f_scale_fw),
                pt(-6.5 * s, side * 19.0 * s * f_scale_fw),
                pt(-3.0 * s, side * 4.0 * s)
            ]
            canvas.create_polygon([c for p in fw_inner_pts for c in p], fill=pri_col, outline="", smooth=True, tags="butterfly_creature")

            # Luminous Discal Cell (Breathing core glow)
            cell_pts = [
                pt(3.5 * s, side * 3.5 * s),
                pt(10.0 * s, side * 17.0 * s * f_scale_fw),
                pt(12.5 * s, side * 28.0 * s * f_scale_fw),
                pt(3.0 * s,  side * 24.0 * s * f_scale_fw),
                pt(-3.0 * s, side * 14.0 * s * f_scale_fw)
            ]
            canvas.create_polygon([c for p in cell_pts for c in p], fill=glow_col, outline="", smooth=True, tags="butterfly_creature")

            cell_core_pts = [
                pt(3.5 * s, side * 4.0 * s),
                pt(8.5 * s, side * 15.0 * s * f_scale_fw),
                pt(9.5 * s, side * 23.0 * s * f_scale_fw),
                pt(3.0 * s, side * 19.0 * s * f_scale_fw),
                pt(-1.5 * s, side * 11.0 * s * f_scale_fw)
            ]
            canvas.create_polygon([c for p in cell_core_pts for c in p], fill=irid_col, outline="", smooth=True, tags="butterfly_creature")

            # Radiating Branching Veins
            for end_x, end_y in [(16, 27), (18, 36), (13, 40), (7, 38), (1, 35), (-4, 30)]:
                start = pt(2.5 * s, side * 4.0 * s)
                end = pt(end_x * s, side * end_y * s * f_scale_fw)
                canvas.create_line(start[0], start[1], end[0], end[1],
                                   fill=irid_col, width=max(0.7, 1.1 * s),
                                   smooth=True, tags="butterfly_creature")

            # Submarginal Pearl Dots along forewing margin
            for mark_x, mark_y in [(18, 40), (14, 42), (9, 40), (4, 38), (-1, 35), (-5, 31)]:
                mx, my = pt(mark_x * s, side * mark_y * s * f_scale_fw)
                mr = 1.45 * s
                canvas.create_oval(mx - mr, my - mr, mx + mr, my + mr,
                                   fill=spot_col, outline=border_col, width=0.4, tags="butterfly_creature")

            # Apex Jewel Accent Spot
            spot_x, spot_y = pt(15.0 * s, side * 33.0 * s * f_scale_fw)
            spot_r = 2.6 * s
            canvas.create_oval(spot_x - spot_r, spot_y - spot_r, spot_x + spot_r, spot_y + spot_r,
                               fill=spot_col, outline=border_col, width=0.8, tags="butterfly_creature")
            canvas.create_oval(spot_x - spot_r*0.5, spot_y - spot_r*0.5, spot_x + spot_r*0.5, spot_y + spot_r*0.5,
                               fill=accent_col, outline="", tags="butterfly_creature")

        # =========================================================================
        # 3. BUTTERFLY BODY (Segmented Abdomen, Thorax, Head, Compound Eyes & Antennae)
        # =========================================================================
        # Abdomen
        abd_pts = [
            pt(-2.0 * s, -3.2 * s),
            pt(-2.0 * s, 3.2 * s),
            pt(-10.0 * s, 2.5 * s),
            pt(-19.0 * s, 1.8 * s),
            pt(-24.0 * s, 0.0),
            pt(-19.0 * s, -1.8 * s),
            pt(-10.0 * s, -2.5 * s)
        ]
        canvas.create_polygon([c for p in abd_pts for c in p], fill=border_col, outline="#334155", width=1.0, smooth=True, tags="butterfly_creature")

        # Delicate abdominal segments
        for stripe_x in [-6.0, -11.0, -16.0, -20.0]:
            w_strip = 2.4 * s * (1.0 - abs(stripe_x) / 28.0)
            a, b = pt(stripe_x * s, -w_strip), pt(stripe_x * s, w_strip)
            canvas.create_line(a[0], a[1], b[0], b[1], fill=self.theme.get('glow', '#94a3b8'),
                               width=max(0.8, 1.0 * s), tags="butterfly_creature")

        # Thorax (Robust, fuzzy central motor)
        th_p1 = pt(-3.0 * s, -4.5 * s)
        th_p2 = pt(6.5 * s, 4.5 * s)
        canvas.create_oval(min(th_p1[0], th_p2[0]), min(th_p1[1], th_p2[1]),
                           max(th_p1[0], th_p2[0]), max(th_p1[1], th_p2[1]),
                           fill=border_col, outline=self.theme.get('glow', '#64748b'), width=1.1, tags="butterfly_creature")

        # Thorax center dorsal sheen
        th_c = pt(1.5 * s, 0)
        canvas.create_oval(th_c[0] - 1.8*s, th_c[1] - 2.8*s, th_c[0] + 1.8*s, th_c[1] + 2.8*s,
                           fill=pri_col, outline="", tags="butterfly_creature")

        # Head capsule
        hd_p1 = pt(6.5 * s, -3.2 * s)
        hd_p2 = pt(12.5 * s, 3.2 * s)
        canvas.create_oval(min(hd_p1[0], hd_p2[0]), min(hd_p1[1], hd_p2[1]),
                           max(hd_p1[0], hd_p2[0]), max(hd_p1[1], hd_p2[1]),
                           fill="#0f172a", outline=border_col, width=0.8, tags="butterfly_creature")

        # Head glint
        glint = pt(11.0 * s, -0.9 * s)
        canvas.create_oval(glint[0] - 0.9*s, glint[1] - 0.9*s, glint[0] + 0.9*s, glint[1] + 0.9*s,
                           fill="#ffffff", outline="", tags="butterfly_creature")

        # Multifaceted compound eyes with specular highlights
        for side in [-1, 1]:
            eye = pt(9.5 * s, side * 2.8 * s)
            canvas.create_oval(eye[0] - 1.6*s, eye[1] - 1.6*s, eye[0] + 1.6*s, eye[1] + 1.6*s,
                               fill="#020617", outline=border_col, width=0.6, tags="butterfly_creature")
            canvas.create_oval(eye[0] - 0.7*s, eye[1] - 0.7*s, eye[0] + 0.4*s, eye[1] + 0.4*s,
                               fill="#ffffff", outline="", tags="butterfly_creature")

            # Elegant curved antennae with glowing golden nectar clubs!
            a_root = pt(10.5 * s, side * 1.6 * s)
            a_mid  = pt(19.0 * s, side * 9.0 * s)
            a_tip  = pt(26.0 * s, side * 15.0 * s)
            canvas.create_line(a_root[0], a_root[1], a_mid[0], a_mid[1], a_tip[0], a_tip[1],
                               fill=border_col, width=1.3 * s, smooth=True, tags="butterfly_creature")
            canvas.create_oval(a_tip[0] - 1.8*s, a_tip[1] - 1.8*s, a_tip[0] + 1.8*s, a_tip[1] + 1.8*s,
                               fill=self.theme.get('ant_tip', '#facc15'), outline=border_col, width=0.6, tags="butterfly_creature")

    def _draw_toast_banner(self, canvas):
        now = time.time()
        rem = self.toast_until - now
        if rem <= 0:
            return

        bx = self.app.screen_x + self.app.screen_w // 2
        by = self.app.screen_y + 46
        txt = self.toast_text
        accent = self.theme.get('accent', '#38bdf8')

        tw = max(200, len(txt) * 7.8 + 36)
        canvas.create_rectangle(bx - tw/2, by - 16, bx + tw/2, by + 16,
                                fill="#090d16", outline=accent, width=1.8, tags="butterfly_creature")
        canvas.create_text(bx, by, text=txt, fill="#f8fafc",
                           font=("Segoe UI", 10, "bold"), tags="butterfly_creature")
