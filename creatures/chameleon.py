# -*- coding: utf-8 -*-
"""
================================================================================
🦎 Desktop Pet Ecosystem - True Asian House Gecko / Tiktiki (দেয়াল টিকটিকি)
Authentic Hemidactylus frenatus Anatomy, Real Reptile Locomotion & Physics:
--------------------------------------------------------------------------------
1. Sleek, Slender Natural Proportions (আসল স্লিক ও চ্যাপ্টা টিকটিকির স্বাভাবিক রূপ).
   - Aspect ratio ~ 8:1 (Total length ~138px, Body width ~17px).
   - NOT a bloated round balloon, NOT a stretched noodle!
2. Smooth, streamlined teardrop-wedge head with delicate jaw contours, nostrils,
   and rhythmic gular breathing pulsation.
3. Natural lateral eyes with golden-amber iris, dark vertical slit pupil, and specular shine.
4. Clean, beautifully splayed 5-digit gecko feet with slender stalks, expanded
   adhesive scansor pads (subdigital lamellae), and tiny recurved micro-claws.
5. Sprawling multi-joint reptile limbs with alternating diagonal trot kinematics.
6. Sinuous 12-segment S-curve undulating spine with soft dorsal midline contour
   and subtle skin freckles (NO harsh dinosaur ribcage stripes!).
7. Seamless, long, tapering muscular tail that flows behind the body in a gentle
   fluid sinusoidal wave with idle tip twitching during pauses.
8. Realistic scurry-and-pause patrol, panic sprint evasion on mouse approach,
   and precision ballistic tongue insect hunting with fluttering moths.
================================================================================
"""

import math
import random
import time
from core.platform_helper import play_audio, PlatformHelper

# ------------------------------------------------------------------------------
# 4 AUTHENTIC HOUSE GECKO CAMOUFLAGE COLOR THEMES
# ------------------------------------------------------------------------------
GECKO_THEMES = [
    # 0: Classic Asian House Gecko (আমাদের ঘরের আসল দেয়াল টিকটিকি)
    {
        "name": "Classic Asian House Gecko",
        "bengali": "আসল দেয়াল টিকটিকি (বেলে-ধূসর)",
        "body": "#d6bcad",          # Warm sandy beige dorsal skin
        "belly": "#f8eee7",         # Soft translucent milky-cream underside
        "shadow": "#211613",        # Realistic ambient contact shadow
        "dark": "#5e453c",          # Fine contour outline
        "mottle": "#8a6a5d",        # Subtle soft dorsal midline contour
        "mottle_light": "#e8d8cf",  # Subtle translucent flank highlight & micro-tubercles
        "throat": "#f6eae2",        # Delicate gular throat patch
        "eye_socket": "#4a352c",    # Orbital brow contour
        "iris": "#d97706",          # Luminous golden-amber iris
        "pupil": "#0a0706",         # Deep black vertical slit pupil
        "lamellae": "#9c7c70",      # Adhesive subdigital scansor pads
        "claw": "#261713"           # Dark recurved micro-claws
    },
    # 1: Translucent Glass Gecko (স্বচ্ছ ফ্যাকাশে টিকটিকি)
    {
        "name": "Translucent Wall Gecko",
        "bengali": "স্বচ্ছ দেয়াল টিকটিকি (গোলাপী-সাদা)",
        "body": "#ded8ce",          # Ghostly pale translucent buff
        "belly": "#fdfbf7",         # Pale alabaster belly
        "shadow": "#1e201b",
        "dark": "#666358",
        "mottle": "#918b7c",
        "mottle_light": "#ece7dd",
        "throat": "#faf6ed",
        "eye_socket": "#4d4b43",
        "iris": "#eab308",          # Luminous warm yellow-gold iris
        "pupil": "#060708",
        "lamellae": "#a09789",
        "claw": "#24221c"
    },
    # 2: Mottled Bark Gecko (গাছের গুঁড়ি ছোপ টিকটিকি)
    {
        "name": "Mottled Bark Gecko",
        "bengali": "গাছের গুঁড়ি ছোপ টিকটিকি (বাদামী)",
        "body": "#a6825c",          # Earthy rich bark tan
        "belly": "#f4eadf",
        "shadow": "#1f160e",
        "dark": "#4c3722",
        "mottle": "#6e4f30",
        "mottle_light": "#c3a47e",
        "throat": "#eedfce",
        "eye_socket": "#3c2a19",
        "iris": "#c2410c",          # Fiery copper-bronze iris
        "pupil": "#090503",
        "lamellae": "#7a5c3c",
        "claw": "#20150b"
    },
    # 3: Nocturnal Slate Shadow Gecko (কালচে নিশাচর টিকটিকি)
    {
        "name": "Nocturnal Shadow Gecko",
        "bengali": "কালচে নিশাচর টিকটিকি (স্লেট ধূসর)",
        "body": "#4a5568",          # Charcoal slate grey
        "belly": "#cbd5e1",
        "shadow": "#090d16",
        "dark": "#1e293b",
        "mottle": "#334155",
        "mottle_light": "#64748b",
        "throat": "#94a3b8",
        "eye_socket": "#0f172a",
        "iris": "#38bdf8",          # Striking icy electric cyan-amber
        "pupil": "#020617",
        "lamellae": "#3b4759",
        "claw": "#080c14"
    }
]


class ChameleonCreature:
    """Authentic, sleek, life-like Asian House Gecko (দেয়াল টিকটিকি - Hemidactylus frenatus)."""

    def __init__(self, app):
        self.app = app
        # Colors & Themes
        self.colors = GECKO_THEMES
        self.color_idx = int(app.config.get("GECKO_COLOR_INDEX", 0)) % len(self.colors)
        self.theme = self.colors[self.color_idx]

        # Authentic Natural Gecko Proportions:
        self.scale = float(app.config.get("GECKO_SCALE", 1.15))
        
        saved_gx = app.config.get("GECKO_X", None)
        saved_gy = app.config.get("GECKO_Y", None)
        if saved_gx is not None and saved_gy is not None:
            try:
                self.x = float(saved_gx)
                self.y = float(saved_gy)
            except Exception:
                self.x = float(app.screen_x + 360.0)
                self.y = float(app.screen_y + app.screen_h - 48.0)
        else:
            self.x = float(app.screen_x + 360.0)
            self.y = float(app.screen_y + app.screen_h - 48.0)
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.target_angle = 0.0
        self.walk_phase = 0.0
        self.is_fleeing = False
        self.state = "CALM"  # "CALM", "FLEE", "ALERT"
        self.cruise_direction = 1.0
        self.flee_direction = 1.0
        self.flee_until = 0.0
        self.flee_cooldown_until = 0.0
        self.alert_until = 0.0
        self.pause_timer = 0.0
        self.num_spine_joints = 12
        self.num_tail_joints = 14

        # Hunting & Insects
        self.tongue_state = "IDLE"  # "IDLE", "EXTENDING", "RETRACTING"
        self.tongue_progress = 0.0
        self.target_bug = None
        self.tongue_target_x = 0.0
        self.tongue_target_y = 0.0
        self.insects = []
        self.last_bug_spawn = 0.0

    def trigger_hunt(self):
        """Fires an authentic lightning-fast ballistic tongue strike at nearby moths."""
        if self.tongue_state == "IDLE":
            if self.insects:
                self.target_bug = self.insects[0]
                self.tongue_target_x = self.target_bug['x']
                self.tongue_target_y = self.target_bug['y']
            else:
                cos_a = math.cos(self.angle)
                sin_a = math.sin(self.angle)
                self.tongue_target_x = self.x + cos_a * (120.0 * self.scale)
                self.tongue_target_y = self.y + sin_a * (120.0 * self.scale)
            self.tongue_state = "EXTENDING"
            self.tongue_progress = 0.0
            if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
                play_audio(1100, 20, 480, 30)

    def cycle_color(self):
        """Cycles through the 4 authentic gecko camouflage themes."""
        self.color_idx = (self.color_idx + 1) % len(self.colors)
        self.theme = self.colors[self.color_idx]
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(650, 30)
        from core.config import save_config_value
        save_config_value("GECKO_COLOR_INDEX", self.color_idx)
        self.show_toast(f"🦎 {self.theme.get('bengali', self.theme['name'])}")

    def set_spot_from_cursor(self):
        """Relocates the gecko directly underneath the mouse cursor."""
        mx, my = self.app.get_mouse_pos()
        self.x = float(mx)
        self.y = float(my)
        self.vx = 0.0
        self.vy = 0.0
        self.state = "ALERT"
        self.alert_until = time.time() + 0.8
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(550, 30, 750, 40)
        from core.config import save_config_value
        save_config_value("GECKO_X", float(self.x))
        save_config_value("GECKO_Y", float(self.y))
        self.show_toast("📍 টিকটিকির অবস্থান পরিবর্তন করা হয়েছে")

    def show_toast(self, text):
        """Shows floating banner toast on app canvas if supported."""
        if hasattr(self.app, 'show_notification_toast'):
            self.app.show_notification_toast(text)

    def on_canvas_click(self, click_x, click_y):
        """Interactive click reaction: startled burst sprint."""
        dx = self.x - click_x
        dy = self.y - click_y
        dist = math.hypot(dx, dy)
        if dist < (50.0 * self.scale):
            self.state = "FLEE"
            self.is_fleeing = True
            self.flee_direction = 1.0 if dx >= 0 else -1.0
            self.flee_until = time.time() + random.uniform(0.9, 1.4)
            self.flee_cooldown_until = time.time() + 2.8
            if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
                play_audio(700, 25, 950, 30)

    def update(self, now):
        """Updates position, spine physics, fleeing logic, and insect hunting."""
        # 1. Spawn prey insects (realistic fluttering wall moths/gnats)
        if len(self.insects) < 2 and (now - self.last_bug_spawn > 4.2):
            bx = self.x + random.uniform(-160, 160)
            by = self.y - random.uniform(25, 75)
            self.insects.append({
                'x': bx, 'y': by,
                'vx': random.uniform(-0.8, 0.8),
                'vy': random.uniform(-0.5, 0.5),
                'flutter_phase': random.uniform(0, 6.28)
            })
            self.last_bug_spawn = now

        for b in self.insects:
            if b != self.target_bug:
                b['x'] += b['vx']
                b['y'] += b['vy']
                b['flutter_phase'] += 0.35
                if abs(b['x'] - self.x) > 190:
                    b['vx'] *= -1

        # 2. Interactive Mouse Evasion (Panic Scurry away from approaching cursor)
        mx, my = self.app.get_mouse_pos()
        dx_m = self.x - mx
        dy_m = self.y - my
        dist_m = math.hypot(dx_m, dy_m)

        sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
        left_limit = sx + 45.0
        right_limit = sx + sw - 45.0
        bottom_limit = sy + sh - 42.0

        if dist_m < 150.0 and self.state != "FLEE" and now >= self.flee_cooldown_until:
            self.state = "FLEE"
            self.is_fleeing = True
            self.flee_direction = 1.0 if dx_m >= 0.0 else -1.0
            if self.x < left_limit + 90.0:
                self.flee_direction = 1.0
            elif self.x > right_limit - 90.0:
                self.flee_direction = -1.0
            self.flee_until = now + random.uniform(0.75, 1.25)
            self.flee_cooldown_until = now + 2.3
            self.tongue_state = "IDLE"
            self.target_bug = None
            if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
                play_audio(600, 20, 800, 25)

        # 3. State-based Movement Kinematics
        if self.state == "FLEE":
            self.is_fleeing = True
            self.target_angle = 0.0 if self.flee_direction > 0 else math.pi
            self.vx = self.flee_direction * (4.2 * self.scale)
            self.x += self.vx
            self.vy = 0.0
            self.walk_phase += 0.42  # Fast, rapid stride cycles during sprint

            if now >= self.flee_until or self.x < left_limit + 20.0 or self.x > right_limit - 20.0:
                self.state = "ALERT"
                self.alert_until = now + random.uniform(0.6, 1.1)
                self.vx = 0.0

        elif self.state == "ALERT":
            self.is_fleeing = False
            self.vx = 0.0
            self.vy = 0.0
            if now >= self.alert_until:
                self.state = "CALM"
                self.pause_timer = now + random.uniform(0.6, 1.5)

        else:  # "CALM"
            self.is_fleeing = False
            if self.tongue_state == "IDLE":
                if self.insects and random.random() < 0.035:
                    target_bug = self.insects[0]
                    dx = target_bug['x'] - self.x
                    dy = target_bug['y'] - self.y
                    self.target_angle = math.atan2(dy, dx)
                    self.trigger_hunt()
                else:
                    if now > self.pause_timer:
                        # Sleek, steady scurry crawl
                        self.vx = self.cruise_direction * (1.6 * self.scale)
                        self.x += self.vx
                        self.walk_phase += 0.18
                        self.target_angle = 0.0 if self.cruise_direction > 0 else math.pi

                        if self.x < left_limit + 70.0 or self.x > right_limit - 70.0:
                            self.cruise_direction *= -1.0
                            self.pause_timer = now + random.uniform(0.4, 1.0)
                        elif random.random() < 0.012:
                            self.cruise_direction *= -1.0
                            self.pause_timer = now + random.uniform(0.7, 1.6)
                    else:
                        # Pausing / Freezing alertly like a real gecko
                        self.vx = 0.0
            elif self.tongue_state == "EXTENDING":
                self.tongue_progress += 0.28
                if self.tongue_progress >= 1.0:
                    self.tongue_progress = 1.0
                    self.tongue_state = "RETRACTING"
            elif self.tongue_state == "RETRACTING":
                self.tongue_progress -= 0.24
                if self.target_bug:
                    cos_a = math.cos(self.angle)
                    sin_a = math.sin(self.angle)
                    snout_x = self.x + cos_a * (20.0 * self.scale)
                    snout_y = self.y + sin_a * (20.0 * self.scale)
                    self.target_bug['x'] = snout_x + (self.tongue_target_x - snout_x) * self.tongue_progress
                    self.target_bug['y'] = snout_y + (self.tongue_target_y - snout_y) * self.tongue_progress

                if self.tongue_progress <= 0.0:
                    self.tongue_progress = 0.0
                    self.tongue_state = "IDLE"
                    if self.target_bug and self.target_bug in self.insects:
                        self.insects.remove(self.target_bug)
                        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
                            play_audio(850, 20, 600, 25)
                    self.target_bug = None

        # Smooth head/body angle alignment
        diff = self.target_angle - self.angle
        while diff < -math.pi: diff += math.pi * 2
        while diff > math.pi: diff -= math.pi * 2
        self.angle += diff * (0.28 if self.state == "FLEE" else 0.12)

        # Enforce screen boundaries
        if self.x < left_limit:
            self.x = left_limit
            self.cruise_direction = 1.0
            self.flee_direction = 1.0
        if self.x > right_limit:
            self.x = right_limit
            self.cruise_direction = -1.0
            self.flee_direction = -1.0
        if self.y < sy + 50.0:
            self.y = sy + 50.0
            self.vy = 0.0
        if self.y > bottom_limit:
            self.y = bottom_limit
            self.vy = 0.0

    def draw(self, canvas):
        """Draws the sleek, anatomically authentic Asian House Gecko with clean realistic rendering."""
        canvas.delete("chameleon_creature")
        try:
            pal = self.colors[self.color_idx]
            s = self.scale
            now = time.time()

            # ------------------------------------------------------------------
            # 1. Flying Prey Moths (fluttering soft night insects)
            # ------------------------------------------------------------------
            for b in self.insects:
                bx, by = b['x'], b['y']
                f_ang = math.sin(b.get('flutter_phase', 0.0) + now * 16.0) * 4.0
                canvas.create_oval(bx - 2.2, by - 1.4, bx + 2.2, by + 1.4,
                                   fill="#1e293b", outline="", tags="chameleon_creature")
                canvas.create_polygon([
                    bx, by,
                    bx - 6.0, by - 3.5 - f_ang,
                    bx - 2.5, by - 6.5 - f_ang,
                    bx, by
                ], fill="#cbd5e1", outline="#94a3b8", width=0.5, tags="chameleon_creature")
                canvas.create_polygon([
                    bx, by,
                    bx + 6.0, by - 3.5 - f_ang,
                    bx + 2.5, by - 6.5 - f_ang,
                    bx, by
                ], fill="#cbd5e1", outline="#94a3b8", width=0.5, tags="chameleon_creature")

            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)
            norm_x = -sin_a
            norm_y = cos_a

            # ------------------------------------------------------------------
            # 2. Sinuous 12-Joint Undulating S-Curve Spine (প্রাকৃতিক স্লিক মেরুদণ্ড)
            # ------------------------------------------------------------------
            spine = []
            spine_angles = []
            num_spine = self.num_spine_joints

            # Dynamic lateral wave amplitude (gentle, natural reptile S-wave)
            wave_amp = (2.8 if self.is_fleeing else (1.8 if self.vx != 0.0 else 0.5)) * s

            for i in range(num_spine):
                dist = i * (4.2 * s)  # Torso length ~ 46-52px
                lat = math.sin(self.walk_phase - i * 0.44) * wave_amp
                px = self.x - cos_a * dist + norm_x * lat
                py = self.y - sin_a * dist + norm_y * lat
                spine.append((px, py))

            # Compute local vertebral orientation tangent angles
            for i in range(num_spine):
                if i < num_spine - 1:
                    dx_s = spine[i][0] - spine[i+1][0]
                    dy_s = spine[i][1] - spine[i+1][1]
                else:
                    dx_s = spine[i-1][0] - spine[i][0]
                    dy_s = spine[i-1][1] - spine[i][1]
                spine_angles.append(math.atan2(dy_s, dx_s))

            # Realistic, slender half-widths:
            # Neck (3.8) -> Shoulders (6.6) -> Mid-torso (7.5) -> Waist (6.5) -> Pelvis (5.8) -> Tail base (4.4)
            # Total width across body is ~15-17px (slender & sleek, NOT a fat balloon!)
            spine_widths = [3.8, 5.2, 6.6, 7.2, 7.5, 7.4, 7.0, 6.5, 6.2, 5.8, 5.0, 4.4]

            # ------------------------------------------------------------------
            # 3. Soft Ambient Contact Shadow Under Body & Tail
            # ------------------------------------------------------------------
            sh_left, sh_right = [], []
            for i, (sx_i, sy_i) in enumerate(spine):
                w = spine_widths[i] * s * 0.95
                s_ang = spine_angles[i]
                snx = -math.sin(s_ang)
                sny = math.cos(s_ang)
                sh_left.append((sx_i + snx * w + 1.5*s, sy_i + sny * w + 2.2*s))
                sh_right.append((sx_i - snx * w + 1.5*s, sy_i - sny * w + 2.2*s))
            flat_shadow = [c for pt in sh_left for c in pt] + [c for pt in reversed(sh_right) for c in pt]
            canvas.create_polygon(flat_shadow, fill=pal['shadow'], outline="", smooth=True, tags="chameleon_creature")

            # ------------------------------------------------------------------
            # 4. Sprawling Reptile Legs & Clean Fan-Shaped Toes
            # Diagonal Trot Gait: LF+RH move in sync, RF+LH move in sync
            # ------------------------------------------------------------------
            leg_configs = [
                # (spine_idx, side, phase_offset, is_hind)
                (2, -1, 0.0,     False),   # Left front (LF) - shoulder
                (2,  1, math.pi, False),   # Right front (RF) - shoulder
                (8, -1, math.pi, True),    # Left hind (LH) - hips
                (8,  1, 0.0,     True)     # Right hind (RH) - hips
            ]

            for seg_idx, side, phase_offset, is_hind in leg_configs:
                joint_x, joint_y = spine[seg_idx]
                seg_ang = spine_angles[seg_idx]
                seg_nx = -math.sin(seg_ang)
                seg_ny = math.cos(seg_ang)

                # Diagonal trot swing & reach
                swing = math.sin(self.walk_phase + phase_offset) * (6.0 * s)
                lift = max(0.0, math.sin(self.walk_phase + phase_offset)) * (1.8 * s)

                if not is_hind:
                    # Forelimb: Upper arm points outward & back, elbow bends forward,
                    # forearm extends forward and inward beside chin
                    shoulder_w = 4.8 * s
                    base_x = joint_x + side * seg_nx * shoulder_w + math.cos(seg_ang) * (2.0 * s)
                    base_y = joint_y + side * seg_ny * shoulder_w + math.sin(seg_ang) * (2.0 * s)

                    # Elbow joint
                    elbow_out = (8.5 * s) * side
                    elbow_fwd = (2.5 * s) + swing * 0.65
                    elbow_x = base_x + seg_nx * elbow_out + math.cos(seg_ang) * elbow_fwd
                    elbow_y = base_y + seg_ny * elbow_out + math.sin(seg_ang) * elbow_fwd - lift * 0.5

                    # Wrist / Foot base
                    wrist_out = (6.0 * s) * side
                    wrist_fwd = (9.5 * s) + swing * 1.1
                    foot_x = base_x + seg_nx * wrist_out + math.cos(seg_ang) * wrist_fwd
                    foot_y = base_y + seg_ny * wrist_out + math.sin(seg_ang) * wrist_fwd - lift

                    foot_angle = seg_ang + side * 0.28
                else:
                    # Hindlimb: Thigh points outward & forward, knee bends backward,
                    # shin extends backward and outward behind hip
                    hip_w = 4.5 * s
                    base_x = joint_x + side * seg_nx * hip_w - math.cos(seg_ang) * (1.2 * s)
                    base_y = joint_y + side * seg_ny * hip_w - math.sin(seg_ang) * (1.2 * s)

                    # Knee joint
                    knee_out = (9.2 * s) * side
                    knee_fwd = (-1.5 * s) + swing * 0.65
                    elbow_x = base_x + seg_nx * knee_out + math.cos(seg_ang) * knee_fwd
                    elbow_y = base_y + seg_ny * knee_out + math.sin(seg_ang) * knee_fwd - lift * 0.5

                    # Ankle / Foot base
                    ankle_out = (7.0 * s) * side
                    ankle_fwd = (-8.0 * s) + swing * 1.1
                    foot_x = base_x + seg_nx * ankle_out + math.cos(seg_ang) * ankle_fwd
                    foot_y = base_y + seg_ny * ankle_out + math.sin(seg_ang) * ankle_fwd - lift

                    foot_angle = seg_ang + side * 0.72

                # Upper Limb (Humerus / Femur) - Sleek contoured stroke
                canvas.create_line(base_x, base_y, elbow_x, elbow_y,
                                   fill=pal['shadow'], width=3.6 * s, capstyle="round", tags="chameleon_creature")
                canvas.create_line(base_x, base_y, elbow_x, elbow_y,
                                   fill=pal['body'], width=2.8 * s, capstyle="round", tags="chameleon_creature")

                # Lower Limb (Radius-Ulna / Shin)
                canvas.create_line(elbow_x, elbow_y, foot_x, foot_y,
                                   fill=pal['shadow'], width=2.8 * s, capstyle="round", tags="chameleon_creature")
                canvas.create_line(elbow_x, elbow_y, foot_x, foot_y,
                                   fill=pal['body'], width=2.2 * s, capstyle="round", tags="chameleon_creature")

                # Neat palm / ankle base oval
                canvas.create_oval(foot_x - 1.8*s, foot_y - 1.8*s, foot_x + 1.8*s, foot_y + 1.8*s,
                                   fill=pal['lamellae'], outline=pal['dark'], width=0.5, tags="chameleon_creature")

                # --------------------------------------------------------------
                # 5 Crisp Radiating Fan-Shaped Gecko Toes (পরিষ্কার ৫টি আঙুল ও ল্যামেলা)
                # --------------------------------------------------------------
                toe_spread = [-0.92, -0.44, 0.0, 0.44, 0.92]
                toe_lengths = [4.8, 6.2, 7.5, 7.2, 5.2]

                for t_idx, t_ang in enumerate(toe_spread):
                    ang_t = foot_angle + t_ang
                    total_len = toe_lengths[t_idx] * s
                    cos_t = math.cos(ang_t)
                    sin_t = math.sin(ang_t)

                    # Slender digit stalk
                    tx = foot_x + cos_t * total_len
                    ty = foot_y + sin_t * total_len
                    canvas.create_line(foot_x, foot_y, tx, ty,
                                       fill=pal['body'], width=1.4 * s, capstyle="round", tags="chameleon_creature")

                    # Expanded adhesive lamellae pad oval at tip
                    canvas.create_oval(tx - 1.3*s, ty - 1.3*s, tx + 1.3*s, ty + 1.3*s,
                                       fill=pal['lamellae'], outline=pal['dark'], width=0.5, tags="chameleon_creature")

                    # Tiny sharp micro-claw tip dot
                    canvas.create_oval(tx + cos_t*0.8 - 0.4, ty + sin_t*0.8 - 0.4,
                                       tx + cos_t*0.8 + 0.4, ty + sin_t*0.8 + 0.4,
                                       fill=pal['claw'], outline="", tags="chameleon_creature")

            # ------------------------------------------------------------------
            # 5. Seamless Slender Tapering Muscular Tail (মসৃণ সরু ঢেউ খেলানো লেজ)
            # ------------------------------------------------------------------
            tail_base_x, tail_base_y = spine[-1]
            tail_pts = [(tail_base_x, tail_base_y)]
            cur_x, cur_y = tail_base_x, tail_base_y
            num_tail = self.num_tail_joints

            # Sinusoidal wave undulation trailing behind body
            for j in range(1, num_tail + 1):
                wave = math.sin(self.walk_phase * 0.82 - j * 0.36) * (0.15 + j * 0.024)
                if self.vx == 0.0:
                    wave += math.sin(now * 2.4 - j * 0.45) * (0.08 if j > 8 else 0.02)
                t_ang = spine_angles[-1] + math.pi + wave
                cur_x += math.cos(t_ang) * (4.8 * s)
                cur_y += math.sin(t_ang) * (4.8 * s)
                tail_pts.append((cur_x, cur_y))

            # Tail polygon with continuous progressive width taper down to needle tip
            tail_poly_left, tail_poly_right = [], []
            for k, (tx, ty) in enumerate(tail_pts):
                w_tail = max(0.7, (4.2 - k * 0.27) * s)
                if k < len(tail_pts) - 1:
                    dx_t = tail_pts[k+1][0] - tx
                    dy_t = tail_pts[k+1][1] - ty
                else:
                    dx_t = tx - tail_pts[k-1][0]
                    dy_t = ty - tail_pts[k-1][1]
                t_norm_ang = math.atan2(dy_t, dx_t) + math.pi / 2.0
                nx_t = math.cos(t_norm_ang) * w_tail
                ny_t = math.sin(t_norm_ang) * w_tail
                tail_poly_left.append((tx + nx_t, ty + ny_t))
                tail_poly_right.append((tx - nx_t, ty - ny_t))

            flat_tail = [c for pt in tail_poly_left for c in pt] + [c for pt in reversed(tail_poly_right) for c in pt]
            canvas.create_polygon(flat_tail, fill=pal['body'], outline=pal['dark'], width=1.0, smooth=True, tags="chameleon_creature")

            # ------------------------------------------------------------------
            # 6. Sleek, Slender Lizard Torso (চ্যাপ্টা স্বাভাবিক শরীর)
            # ------------------------------------------------------------------
            body_left, body_right = [], []
            belly_left, belly_right = [], []

            for i, (sx_i, sy_i) in enumerate(spine):
                w = spine_widths[i] * s
                s_ang = spine_angles[i]
                v_nx = -math.sin(s_ang)
                v_ny = math.cos(s_ang)

                # Translucent ventral belly rim (soft pale glow along flanks)
                belly_left.append((sx_i + v_nx * (w * 1.08), sy_i + v_ny * (w * 1.08)))
                belly_right.append((sx_i - v_nx * (w * 1.08), sy_i - v_ny * (w * 1.08)))

                # Dorsal skin polygon
                body_left.append((sx_i + v_nx * w, sy_i + v_ny * w))
                body_right.append((sx_i - v_nx * w, sy_i - v_ny * w))

            # Pale ventral belly margin
            flat_belly = [c for pt in belly_left for c in pt] + [c for pt in reversed(belly_right) for c in pt]
            canvas.create_polygon(flat_belly, fill=pal['belly'], outline="", smooth=True, tags="chameleon_creature")

            # Main dorsal body coat
            flat_body = [c for pt in body_left for c in pt] + [c for pt in reversed(body_right) for c in pt]
            canvas.create_polygon(flat_body, fill=pal['body'], outline=pal['dark'], width=1.0, smooth=True, tags="chameleon_creature")

            # Subtle soft dorsal midline contour (নরম প্রাকৃতিক পিঠের ছায়া)
            spine_pts_flat = [c for pt in spine for c in pt]
            if len(spine_pts_flat) >= 4:
                canvas.create_line(spine_pts_flat, fill=pal['mottle'], width=1.4 * s, smooth=True, tags="chameleon_creature")

            # Fine natural micro-freckles along flanks (প্রাকৃতিক ছোট ছোট হালকা দানা)
            for i in range(2, 10, 2):
                sx_i, sy_i = spine[i]
                s_ang = spine_angles[i]
                v_nx = -math.sin(s_ang)
                v_ny = math.cos(s_ang)
                for side in [-1, 1]:
                    tub_x = sx_i + side * v_nx * (spine_widths[i] * 0.72 * s)
                    tub_y = sy_i + side * v_ny * (spine_widths[i] * 0.72 * s)
                    canvas.create_oval(tub_x - 0.7, tub_y - 0.7, tub_x + 0.7, tub_y + 0.7,
                                       fill=pal['mottle_light'], outline="", tags="chameleon_creature")

            # ------------------------------------------------------------------
            # 7. Streamlined Teardrop-Wedge Head (মসৃণ ডিম্বাকৃতির চ্যাপ্টা মাথা)
            # ------------------------------------------------------------------
            neck_x, neck_y = spine[0]
            head_ang = spine_angles[0]
            head_cos = math.cos(head_ang)
            head_sin = math.sin(head_ang)
            head_nx = -head_sin
            head_ny = head_cos

            snout_reach = 16.5 * s
            snout_x = neck_x + head_cos * snout_reach
            snout_y = neck_y + head_sin * snout_reach

            # Gular breathing pulsation (গলার মৃদু শ্বাস স্পন্দন)
            gular_pulse = math.sin(now * 4.2) * (0.5 * s) if self.vx == 0.0 else 0.0

            # Smooth temporal jaw contours (widest at 6.8 * s, NOT 13.5!)
            jaw_fwd = 5.0 * s
            jaw_w = 6.8 * s + gular_pulse * 0.3
            temporal_l = (neck_x + head_cos * jaw_fwd + head_nx * jaw_w, neck_y + head_sin * jaw_fwd + head_ny * jaw_w)
            temporal_r = (neck_x + head_cos * jaw_fwd - head_nx * jaw_w, neck_y + head_sin * jaw_fwd - head_ny * jaw_w)

            # Mid-snout gentle taper
            mid_fwd = 11.5 * s
            mid_w = 4.8 * s
            mid_l = (neck_x + head_cos * mid_fwd + head_nx * mid_w, neck_y + head_sin * mid_fwd + head_ny * mid_w)
            mid_r = (neck_x + head_cos * mid_fwd - head_nx * mid_w, neck_y + head_sin * mid_fwd - head_ny * mid_w)

            # Rounded snout tip
            tip_l = (snout_x + head_nx * (2.0 * s), snout_y + head_ny * (2.0 * s))
            tip_r = (snout_x - head_nx * (2.0 * s), snout_y - head_ny * (2.0 * s))

            head_poly = [
                (neck_x + head_nx * (4.2 * s), neck_y + head_ny * (4.2 * s)),
                temporal_l, mid_l, tip_l, tip_r, mid_r, temporal_r,
                (neck_x - head_nx * (4.2 * s), neck_y - head_ny * (4.2 * s))
            ]
            flat_head = [c for pt in head_poly for c in pt]

            # Head drop shadow
            flat_head_sh = [c + (1.5*s if idx % 2 == 0 else 2.0*s) for idx, c in enumerate(flat_head)]
            canvas.create_polygon(flat_head_sh, fill=pal['shadow'], outline="", smooth=True, tags="chameleon_creature")

            # Head dorsal polygon (smooth streamlined wedge)
            canvas.create_polygon(flat_head, fill=pal['body'], outline=pal['dark'], width=1.0, smooth=True, tags="chameleon_creature")

            # Pale Gular Throat patch
            gular_x = neck_x + head_cos * (4.8 * s)
            gular_y = neck_y + head_sin * (4.8 * s)
            canvas.create_oval(gular_x - (3.5*s + gular_pulse), gular_y - (3.5*s + gular_pulse),
                               gular_x + (3.5*s + gular_pulse), gular_y + (3.5*s + gular_pulse),
                               fill=pal['throat'], outline="", tags="chameleon_creature")

            # Nostrils at tip of snout
            nos_l = (snout_x - head_cos * (1.6*s) + head_nx * (1.2*s), snout_y - head_sin * (1.6*s) + head_ny * (1.2*s))
            nos_r = (snout_x - head_cos * (1.6*s) - head_nx * (1.2*s), snout_y - head_sin * (1.6*s) - head_ny * (1.2*s))
            for nx_pt, ny_pt in [nos_l, nos_r]:
                canvas.create_oval(nx_pt - 0.6, ny_pt - 0.6, nx_pt + 0.6, ny_pt + 0.6,
                                   fill=pal['dark'], outline="", tags="chameleon_creature")

            # ------------------------------------------------------------------
            # 8. Glassy, Prominent Lateral Gecko Eyes (উজ্জ্বল সোনালী চোখ)
            # ------------------------------------------------------------------
            eye_fwd = 9.5 * s
            eye_lat = 5.8 * s
            eye_l = (neck_x + head_cos * eye_fwd + head_nx * eye_lat, neck_y + head_sin * eye_fwd + head_ny * eye_lat)
            eye_r = (neck_x + head_cos * eye_fwd - head_nx * eye_lat, neck_y + head_sin * eye_fwd - head_ny * eye_lat)

            for ex, ey in [eye_l, eye_r]:
                # 1. Raised fleshy orbital brow contour
                canvas.create_oval(ex - 2.4*s, ey - 2.2*s, ex + 2.4*s, ey + 2.2*s,
                                   fill=pal['eye_socket'], outline=pal['dark'], width=0.6, tags="chameleon_creature")
                # 2. Rich luminous golden-amber iris
                canvas.create_oval(ex - 1.8*s, ey - 1.6*s, ex + 1.8*s, ey + 1.6*s,
                                   fill=pal['iris'], outline="", tags="chameleon_creature")

                # 3. Authentic Vertical Slit Pupil
                slit_len = 1.5 * s
                canvas.create_line(ex - head_sin * slit_len, ey + head_cos * slit_len,
                                   ex + head_sin * slit_len, ey - head_cos * slit_len,
                                   fill=pal['pupil'], width=1.1 * s, tags="chameleon_creature")

                # 4. Bright glassy specular highlight reflection dot
                canvas.create_oval(ex - 0.9*s, ey - 0.9*s, ex - 0.2*s, ey - 0.2*s,
                                   fill="#ffffff", outline="", tags="chameleon_creature")

            # ------------------------------------------------------------------
            # 9. Precision Ballistic Tongue Strike (১০০% নির্ভুল পোকা শিকার)
            # ------------------------------------------------------------------
            if self.tongue_state in ["EXTENDING", "RETRACTING"]:
                mouth_x = snout_x
                mouth_y = snout_y
                tip_x = mouth_x + (self.tongue_target_x - mouth_x) * self.tongue_progress
                tip_y = mouth_y + (self.tongue_target_y - mouth_y) * self.tongue_progress

                # Elastic coral-pink tongue line
                canvas.create_line(mouth_x, mouth_y, tip_x, tip_y,
                                   fill="#f43f5e", width=2.0 * s, tags="chameleon_creature")
                # Bulbous sticky tongue tip
                canvas.create_oval(tip_x - 3.2*s, tip_y - 3.2*s, tip_x + 3.2*s, tip_y + 3.2*s,
                                   fill="#be123c", outline="#fda4af", width=1.0, tags="chameleon_creature")

        except Exception as e:
            pass
