# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Celestial Sky Dragon / Serpentine Companion (Image 5)
Features:
- Segmented serpentine body with glowing golden dorsal jewel spots.
- Elegant flapping celestial wings on thorax.
- Dragon head with golden antennae feelers and glowing eyes.
- DYNAMIC COLOR EMISSION (চলমান অবস্থায় পেছন থেকে রঙিন মহাজাগতিক কণা নির্গমন):
  As the dragon glides across the screen, its tail continuously sheds a stream of
  glowing multicolored stardust particles (pink, violet, cyan, gold, emerald, white).
- Interactive mouse following and starlight ember breath (Shift+B).
"""

import math
import random
import time
from core.platform_helper import play_audio, PlatformHelper

class CelestialDragon:
    """Majestic Celestial Winged Sky Dragon (Image 5 Companion)"""
    def __init__(self, app):
        self.app = app
        self.x = float(app.screen_x + 400.0)
        self.y = float(app.screen_y + 300.0)
        self.vx = 2.4
        self.vy = 0.0
        self.angle = 0.0
        self.target_angle = 0.0
        self.wave_phase = 0.0
        self.wing_phase = 0.0
        self.num_segments = 13
        self.scale = 1.1

        # Inverse-kinematic trailing segments
        self.segments = [{'x': self.x - i * 15.0, 'y': self.y} for i in range(self.num_segments)]

        # Glowing stardust particles emitted from tail
        self.embers = []
        self.trail_colors = [
            "#ec4899", # Cosmic Magenta
            "#8b5cf6", # Nebula Violet
            "#38bdf8", # Celestial Sky
            "#06b6d4", # Electric Cyan
            "#facc15", # Solar Gold
            "#34d399", # Aurora Emerald
            "#f97316", # Starfire Amber
            "#ffffff"  # Pure White
        ]

    def trigger_breath(self):
        """Starlight Ember Breath / Starfire Burst (Shift+B or click)"""
        for i in range(24):
            ang = self.angle - math.pi / 2 + random.uniform(-0.55, 0.55)
            spd = random.uniform(6.0, 11.0)
            self.embers.append({
                'x': self.x, 'y': self.y,
                'vx': math.cos(ang) * spd,
                'vy': math.sin(ang) * spd,
                'life': 1.0,
                'decay': random.uniform(0.02, 0.035),
                'r': random.uniform(2.5, 4.5),
                'color': random.choice(self.trail_colors)
            })
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(350, 40, 720, 60)

    def update(self, now):
        # 1. Update Glowing Stardust Embers
        alive = []
        for e in self.embers:
            e['x'] += e['vx']
            e['y'] += e['vy']
            e['vx'] *= 0.96
            e['vy'] *= 0.96
            e['life'] -= e.get('decay', 0.028)
            if e['life'] > 0:
                alive.append(e)
        self.embers = alive

        # 2. Smooth Mouse Following & Sinuous Flight Dynamics
        mx, my = self.app.get_mouse_pos()
        dx = mx - self.x
        dy = my - self.y
        dist = math.hypot(dx, dy)

        if dist > 60.0:
            target_ang = math.atan2(dy, dx) + math.pi / 2
            diff = target_ang - self.angle
            while diff < -math.pi: diff += math.pi * 2
            while diff > math.pi: diff -= math.pi * 2
            self.angle += diff * 0.07
            spd = 4.2 + min(2.8, dist / 100.0)
        else:
            spd = 3.2

        self.vx = math.cos(self.angle - math.pi / 2) * spd
        self.vy = math.sin(self.angle - math.pi / 2) * spd
        self.x += self.vx
        self.y += self.vy

        self.wave_phase += 0.22
        self.wing_phase += 0.35

        # 3. CONTINUOUS COLOR EMISSION FROM TAIL (চলমান অবস্থায় লেজ থেকে রঙ নির্গমন)
        # As requested: "galaxi tar jokhon colbe tar peson tekhe color ber hobe"
        if len(self.embers) < 70 and random.random() < 0.75:
            tail_s = self.segments[-1]
            drift_ang = self.angle + math.pi / 2 + random.uniform(-0.6, 0.6)
            drift_spd = random.uniform(0.8, 2.5)
            self.embers.append({
                'x': tail_s['x'] + random.uniform(-3, 3),
                'y': tail_s['y'] + random.uniform(-3, 3),
                'vx': math.cos(drift_ang) * drift_spd - self.vx * 0.15,
                'vy': math.sin(drift_ang) * drift_spd - self.vy * 0.15,
                'life': 1.0,
                'decay': random.uniform(0.018, 0.032),
                'r': random.uniform(2.0, 3.8),
                'color': random.choice(self.trail_colors)
            })

        # 4. Trailing Spine Segments Inverse Kinematics
        lead_x, lead_y = self.x, self.y
        for i, s in enumerate(self.segments):
            dx_s = lead_x - s['x']
            dy_s = lead_y - s['y']
            d = math.hypot(dx_s, dy_s)
            target_dist = 13.0 * self.scale
            if d > target_dist:
                ratio = (d - target_dist) / d
                s['x'] += dx_s * ratio * 0.68
                s['y'] += dy_s * ratio * 0.68
            lead_x, lead_y = s['x'], s['y']

        # Boundary bounce
        sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
        pad = 55.0
        if self.x < sx + pad: self.x = sx + pad
        if self.x > sx + sw - pad: self.x = sx + sw - pad
        if self.y < sy + pad: self.y = sy + pad
        if self.y > sy + sh - pad: self.y = sy + sh - pad

    def draw(self, canvas):
        canvas.delete("dragon_creature")
        try:
            s = self.scale

            # 1. Trailing Glowing Rainbow Stardust Embers (পেছন থেকে নির্গত কণা)
            for e in self.embers:
                rad = max(0.8, e['r'] * e['life'])
                canvas.create_oval(e['x']-rad, e['y']-rad, e['x']+rad, e['y']+rad,
                                   fill=e['color'], outline="", tags="dragon_creature")

            # 2. Celestial Flapping Wings on Thorax (Segments 1-2)
            norm_x = -math.sin(self.angle - math.pi / 2)
            norm_y = math.cos(self.angle - math.pi / 2)
            wing_root_x = self.segments[1]['x']
            wing_root_y = self.segments[1]['y']
            f_flap = math.sin(self.wing_phase)
            wing_span = (26.0 + 8.0 * f_flap) * s
            wing_back = 12.0 * s

            for side in [-1, 1]:
                tip_x = wing_root_x + side * norm_x * wing_span - math.cos(self.angle - math.pi/2) * wing_back
                tip_y = wing_root_y + side * norm_y * wing_span - math.sin(self.angle - math.pi/2) * wing_back
                mid_x = wing_root_x + side * norm_x * (wing_span * 0.6) + math.cos(self.angle - math.pi/2) * (5.0 * s)
                mid_y = wing_root_y + side * norm_y * (wing_span * 0.6) + math.sin(self.angle - math.pi/2) * (5.0 * s)

                wing_poly = [
                    wing_root_x, wing_root_y,
                    mid_x, mid_y,
                    tip_x, tip_y,
                    wing_root_x - math.cos(self.angle - math.pi/2) * (18.0 * s),
                    wing_root_y - math.sin(self.angle - math.pi/2) * (18.0 * s)
                ]
                canvas.create_polygon(wing_poly, fill="#38bdf8", outline="#bae6fd", width=1.2, smooth=True, tags="dragon_creature")
                canvas.create_line(wing_root_x, wing_root_y, tip_x, tip_y, fill="#f0f9ff", width=1.0, tags="dragon_creature")

            # 3. Serpentine Segmented Body with Golden Jewel Dots (Image 5)
            for i in reversed(range(len(self.segments))):
                seg = self.segments[i]
                # Tapering radius from head to tail tip
                r = max(2.5, (8.5 - (i * 0.48)) * s)
                wave = math.sin(self.wave_phase + i * 0.55) * (4.2 * s)
                cx = seg['x'] + norm_x * wave
                cy = seg['y'] + norm_y * wave

                col = "#38bdf8" if i % 2 == 0 else "#0284c7"
                # Segment circle
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                   fill=col, outline="#e0f2fe", width=1.2, tags="dragon_creature")
                # Golden dorsal jewel dot (Image 5)
                canvas.create_oval(cx - 1.8, cy - 1.8, cx + 1.8, cy + 1.8,
                                   fill="#facc15", outline="#fef08a", width=0.5, tags="dragon_creature")

            # 4. Dragon Head & Expressive Features (Image 5)
            hx, hy = self.x, self.y
            hr = 9.5 * s
            canvas.create_oval(hx - hr, hy - hr, hx + hr, hy + hr,
                               fill="#0369a1", outline="#38bdf8", width=1.6, tags="dragon_creature")

            # Dragon Horns / Antennae Feelers (Image 5 - Yellow Feelers)
            ant_len = 13.0 * s
            for side in [-1, 1]:
                base_x = hx + side * norm_x * (3.5 * s) - math.cos(self.angle - math.pi/2) * (2.0 * s)
                base_y = hy + side * norm_y * (3.5 * s) - math.sin(self.angle - math.pi/2) * (2.0 * s)
                tip_x = base_x + side * norm_x * (6.5 * s) + math.cos(self.angle - math.pi/2) * ant_len
                tip_y = base_y + side * norm_y * (6.5 * s) + math.sin(self.angle - math.pi/2) * ant_len

                canvas.create_line(base_x, base_y, tip_x, tip_y,
                                   fill="#facc15", width=1.8, tags="dragon_creature")
                canvas.create_oval(tip_x - 1.8, tip_y - 1.8, tip_x + 1.8, tip_y + 1.8,
                                   fill="#fef08a", outline="#f59e0b", width=0.6, tags="dragon_creature")

            # Glowing Red Dragon Eyes (Image 5)
            eye_lat = 4.5 * s
            eye_fwd = 3.0 * s
            for side in [-1, 1]:
                ex = hx + side * norm_x * eye_lat + math.cos(self.angle - math.pi/2) * eye_fwd
                ey = hy + side * norm_y * eye_lat + math.sin(self.angle - math.pi/2) * eye_fwd
                # Red iris
                canvas.create_oval(ex - 2.4, ey - 2.4, ex + 2.4, ey + 2.4,
                                   fill="#ef4444", outline="#ffffff", width=0.8, tags="dragon_creature")
                # White gleam pupil
                canvas.create_oval(ex - 1.0, ey - 1.0, ex + 1.0, ey + 1.0,
                                   fill="#ffffff", outline="", tags="dragon_creature")
        except Exception:
            pass
