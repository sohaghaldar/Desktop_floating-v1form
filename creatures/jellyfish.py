# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Deep-Sea Bioluminescent Jellyfish
Features:
- Translucent, glowing crystalline bell with pulsing contraction propulsion.
- Radial meridian striations with bioluminescent node lights.
- 4 cascading, frilled silk-ribbon oral arms.
- 12 trailing marginal tentacles with fluid wave physics.
- Gentle mouse attraction and radiant bioluminescent shockwave burst (Shift+F).
"""

import math
import random
import time
from core.platform_helper import play_audio, PlatformHelper

JELLYFISH_PALETTES = [
    {
        "name": "Crimson Ocean Glow",
        "bell_outer": "#0369a1", "bell_inner": "#fb7185", "bell_glow": "#67e8f9",
        "rim": "#e0f2fe", "striae": "#fbcfe8", "tentacles": "#f472b6",
        "oral_arms": "#fb7185", "particles": "#cffafe"
    },
    {
        "name": "Azure Deep Glow",
        "bell_outer": "#0c4a6e", "bell_inner": "#0284c7", "bell_glow": "#38bdf8",
        "rim": "#e0f2fe", "striae": "#bae6fd", "tentacles": "#38bdf8",
        "oral_arms": "#0369a1", "particles": "#f0f9ff"
    },
    {
        "name": "Emerald Hydrozoa",
        "bell_outer": "#064e3b", "bell_inner": "#059669", "bell_glow": "#34d399",
        "rim": "#d1fae5", "striae": "#a7f3d0", "tentacles": "#34d399",
        "oral_arms": "#047857", "particles": "#ecfdf5"
    },
    {
        "name": "Solar Aurelia",
        "bell_outer": "#7c2d12", "bell_inner": "#ea580c", "bell_glow": "#fb923c",
        "rim": "#ffedd5", "striae": "#fed7aa", "tentacles": "#fb923c",
        "oral_arms": "#c2410c", "particles": "#fff7ed"
    }
]

class CosmicJellyfish:
    """Mesmerizing, anatomically realistic Bioluminescent Jellyfish"""
    def __init__(self, app):
        self.app = app
        self.x = float(app.screen_x + app.screen_w // 2)
        self.y = float(app.screen_y + app.screen_h // 2)
        self.vx = 0.0
        self.vy = -0.45
        self.angle = -math.pi / 2 # Upward floating posture
        self.target_angle = -math.pi / 2
        self.swim_target_x = self.x + app.screen_w * 0.18
        self.swim_target_y = self.y - app.screen_h * 0.12
        self.next_waypoint_time = time.time() + 2.0

        self.pulse_phase = 0.0
        self.pulse_speed = 0.048
        self.theme_idx = 0
        self.themes = JELLYFISH_PALETTES
        self.scale = 1.05

        # Fine, long marginal tentacles and oral arms trail behind the bell.
        self.num_tentacles = 16
        self.tentacle_nodes = 13
        self.tentacles = []
        for i in range(self.num_tentacles):
            t_pts = [{'x': self.x, 'y': self.y + j * 10.0} for j in range(self.tentacle_nodes)]
            self.tentacles.append(t_pts)

        # 4 Central frilled silk oral arms (each with 8 physics nodes)
        self.oral_arms = []
        for i in range(4):
            arm_pts = [{'x': self.x, 'y': self.y + j * 12.0} for j in range(8)]
            self.oral_arms.append(arm_pts)

        self.particles = []
        self.shockwave_radius = 0.0
        self.shockwave_alpha = 0.0

    def cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(self.themes)
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(600, 30, 900, 40)

    def trigger_ripple(self):
        """Powerful propulsion stroke and expanding radiant shockwave (Shift+F)."""
        self.pulse_phase = 0.0
        self.shockwave_radius = 12.0
        self.shockwave_alpha = 1.0
        self.vy = max(-3.0, self.vy - 2.8)
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(420, 50, 850, 80)

    def update(self, now):
        pal = self.themes[self.theme_idx]
        self.pulse_phase += self.pulse_speed
        tau = self.pulse_phase % (2 * math.pi)

        # Forceful contraction squeeze pushing upward, followed by gentle serene glide
        if tau < 1.2:
            power = math.sin((tau / 1.2) * math.pi)
            thrust = power * 2.8
            # Eject bioluminescent water droplets
            if random.random() < 0.40 and len(self.particles) < 35:
                self.particles.append({
                    'x': self.x + random.uniform(-15, 15),
                    'y': self.y + random.uniform(10, 25),
                    'vx': random.uniform(-0.6, 0.6),
                    'vy': random.uniform(0.8, 2.2),
                    'life': 1.0, 'color': pal['particles']
                })
        else:
            thrust = 0.0
            self.vx *= 0.96
            self.vy *= 0.96

        # Choose a roaming waypoint across the whole usable monitor area. A
        # small cursor influence keeps it interactive without making it climb
        # toward the pointer or scrape the top edge continuously.
        sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
        left_limit, right_limit = sx + 90.0, sx + sw - 90.0
        top_limit, bottom_limit = sy + 135.0, sy + sh - 150.0
        target_dx = self.swim_target_x - self.x
        target_dy = self.swim_target_y - self.y
        if now >= self.next_waypoint_time or (
            math.hypot(target_dx, target_dy) < 70.0 and now >= self.next_waypoint_time - 1.0
        ):
            # Alternate between broad left/right bands so it actually crosses
            # the monitor instead of circling around the center.
            center_x = sx + sw * 0.5
            if self.swim_target_x >= center_x:
                self.swim_target_x = random.uniform(left_limit, min(right_limit, left_limit + 150.0))
            else:
                self.swim_target_x = random.uniform(max(left_limit, right_limit - 150.0), right_limit)
            self.swim_target_y = random.uniform(top_limit + 25.0, bottom_limit - 25.0)
            self.next_waypoint_time = now + random.uniform(5.0, 8.0)

        mx, my = self.app.get_mouse_pos()
        dx = target_dx * 0.88 + (mx - self.x) * 0.12
        cursor_y = max(top_limit, min(bottom_limit, my))
        dy = target_dy * 0.88 + (cursor_y - self.y) * 0.12
        self.target_angle = math.atan2(dy, dx)

        diff = self.target_angle - self.angle
        while diff < -math.pi: diff += math.pi * 2
        while diff > math.pi: diff -= math.pi * 2
        self.angle += diff * 0.05

        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        side_x, side_y = -sin_a, cos_a
        # A gentle forward drift plus the bell pulse creates continuous swimming.
        self.vx += cos_a * (0.08 + thrust * 0.16)
        self.vy += sin_a * (0.08 + thrust * 0.16)

        # Gentle natural buoyancy, with a capped glide speed.
        self.vy += math.sin(now * 1.5) * 0.07
        speed = math.hypot(self.vx, self.vy)
        if speed > 3.8:
            self.vx *= 3.8 / speed
            self.vy *= 3.8 / speed

        self.x += self.vx
        self.y += self.vy

        # Update shockwave
        if self.shockwave_alpha > 0:
            self.shockwave_radius += 2.8
            self.shockwave_alpha -= 0.035
            if self.shockwave_alpha <= 0:
                self.shockwave_alpha = 0.0

        # Update particles
        alive_p = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.03
            if p['life'] > 0:
                alive_p.append(p)
        self.particles = alive_p

        # Update trailing tentacles physics (fluid trailing drag)
        rim_width = 34.0 * self.scale
        for i, t_pts in enumerate(self.tentacles):
            t_pct = (i / float(max(1, self.num_tentacles - 1))) * 2.0 - 1.0
            # Attach across the trailing rim, then let each strand stream behind.
            root_x = self.x + side_x * t_pct * rim_width - cos_a * 4.0
            root_y = self.y + side_y * t_pct * rim_width - sin_a * 4.0
            t_pts[0]['x'] = root_x
            t_pts[0]['y'] = root_y

            for j in range(1, len(t_pts)):
                prev = t_pts[j-1]
                curr = t_pts[j]
                # Wave wave motion
                w_wave = math.sin(now * 3.5 + i * 0.6 + j * 0.4) * 1.7
                desired_x = prev['x'] - cos_a * (15.0 * self.scale) + side_x * w_wave
                desired_y = prev['y'] - sin_a * (15.0 * self.scale) + side_y * w_wave
                dx_t = desired_x - curr['x']
                dy_t = desired_y - curr['y']
                curr['x'] += dx_t * 0.38
                curr['y'] += dy_t * 0.38

        # Update oral arms physics (silky cascading ribbons)
        for i, a_pts in enumerate(self.oral_arms):
            arm_ox = (i - 1.5) * (7.0 * self.scale)
            root_x = self.x + side_x * arm_ox - cos_a * 3.0
            root_y = self.y + side_y * arm_ox - sin_a * 3.0
            a_pts[0]['x'] = root_x
            a_pts[0]['y'] = root_y

            for j in range(1, len(a_pts)):
                prev = a_pts[j-1]
                curr = a_pts[j]
                flutter = math.sin(now * 4.0 + i * 0.9 + j * 0.5) * 2.8
                desired_x = prev['x'] - cos_a * (14.0 * self.scale) + side_x * flutter
                desired_y = prev['y'] - sin_a * (14.0 * self.scale) + side_y * flutter
                dx_a = desired_x - curr['x']
                dy_a = desired_y - curr['y']
                curr['x'] += dx_a * 0.42
                curr['y'] += dy_a * 0.42

        # Screen boundaries
        if self.x < left_limit:
            self.x = left_limit
            self.vx = abs(self.vx) * 0.5
            self.swim_target_x = right_limit
        if self.x > right_limit:
            self.x = right_limit
            self.vx = -abs(self.vx) * 0.5
            self.swim_target_x = left_limit
        # Keep the whole bell away from the monitor edge and turn upward thrust
        # into a gentle downward drift instead of repeatedly scraping the ceiling.
        if self.y < top_limit:
            self.y = top_limit
            self.vy = max(0.75, abs(self.vy) * 0.25)
        if self.y > bottom_limit:
            self.y = bottom_limit
            self.vy = -max(0.55, abs(self.vy) * 0.25)

    def draw(self, canvas):
        canvas.delete("jellyfish_creature")
        try:
            pal = self.themes[self.theme_idx]
            s = self.scale

            # 1. Bioluminescent Wake Particles
            for pt in self.particles:
                r = 2.4 * pt['life']
                canvas.create_oval(pt['x']-r, pt['y']-r, pt['x']+r, pt['y']+r,
                                   fill=pt['color'], outline="", tags="jellyfish_creature")

            # 2. Expanding Shockwave Ring
            if self.shockwave_alpha > 0:
                sr = self.shockwave_radius
                canvas.create_oval(self.x - sr, self.y - sr, self.x + sr, self.y + sr,
                                   outline=pal['bell_glow'], width=2.0, tags="jellyfish_creature")

            # 3. 12 Trailing Marginal Tentacles with Luminous Nodes
            for t_pts in self.tentacles:
                coords = [c for p in t_pts for c in (p['x'], p['y'])]
                canvas.create_line(coords, fill=pal['tentacles'], width=1.2, smooth=True, tags="jellyfish_creature")
                tip = t_pts[-1]
                canvas.create_oval(tip['x']-1.6, tip['y']-1.6, tip['x']+1.6, tip['y']+1.6,
                                   fill=pal['rim'], outline="", tags="jellyfish_creature")

            # 4. 4 Cascading Ruffled Silk Oral Arms
            for a_pts in self.oral_arms:
                arm_coords = [c for p in a_pts for c in (p['x'], p['y'])]
                canvas.create_line(arm_coords, fill=pal['oral_arms'], width=2.8, smooth=True, tags="jellyfish_creature")

            # 5. Parabolic Translucent Bell Dome (স্বচ্ছ প্যারাবলিক ছাতা)
            tau = self.pulse_phase % (2 * math.pi)
            contraction = max(0.0, math.sin(tau))
            bw = 42.0 * s * (1.0 - 0.18 * contraction)
            bh = 32.0 * s * (1.0 + 0.12 * contraction)

            cos_a = math.cos(self.angle + math.pi/2)
            sin_a = math.sin(self.angle + math.pi/2)

            def rot(lx, ly):
                return (self.x + lx * cos_a - ly * sin_a, self.y + lx * sin_a + ly * cos_a)

            # Outer Exumbrella Dome
            bell_pts = []
            num_pts = 20
            for i in range(num_pts + 1):
                t = (i / float(num_pts)) * math.pi
                lx = math.cos(t) * bw
                ly = -math.sin(t) ** 1.35 * bh
                bell_pts.append(rot(lx, ly))

            # Bottom undulating margin rim
            num_scallops = 10
            for i in range(num_scallops + 1):
                t = (i / float(num_scallops)) * 2.0 - 1.0
                lx = t * bw
                ly = math.sin(i * math.pi) * 2.5 + 2.0
                bell_pts.append(rot(lx, ly))

            flat_bell = [c for pt in bell_pts for c in pt]
            canvas.create_polygon(flat_bell, fill=pal['bell_outer'], outline=pal['bell_glow'],
                                  width=1.6, smooth=True, tags="jellyfish_creature")

            # Inner Glowing Subumbrella Dome
            inner_w = bw * 0.75
            inner_h = bh * 0.75
            inner_pts = []
            for i in range(num_pts + 1):
                t = (i / float(num_pts)) * math.pi
                lx = math.cos(t) * inner_w
                ly = -math.sin(t) ** 1.35 * inner_h
                inner_pts.append(rot(lx, ly))
            flat_inner = [c for pt in inner_pts for c in pt]
            canvas.create_polygon(flat_inner, fill=pal['bell_inner'], outline="", smooth=True, tags="jellyfish_creature")

            # Luminous marginal bulbs follow the bell rim, giving it a soft,
            # rounded medusa silhouette instead of a plain umbrella shape.
            rim_curve = []
            for i in range(17):
                t = -1.0 + 2.0 * i / 16.0
                rim_curve.append(rot(t * bw, 1.5 + 2.2 * (1.0 - t * t)))
            canvas.create_line([c for pt in rim_curve for c in pt], fill=pal['rim'],
                               width=1.6, smooth=True, tags="jellyfish_creature")
            for i in range(9):
                t = -0.9 + i * 0.225
                nx, ny = rot(t * bw, 1.5 + 2.2 * (1.0 - t * t))
                nr = (1.7 if i % 2 else 2.1) * s
                canvas.create_oval(nx - nr, ny - nr, nx + nr, ny + nr,
                                   fill=pal['rim'], outline=pal['bell_outer'],
                                   width=0.5, tags="jellyfish_creature")

            # Radiant Meridian Striations / Canal Ribs (আলোকিত শিরা)
            for m in [-0.75, -0.45, -0.15, 0.15, 0.45, 0.75]:
                apex_pt = rot(0.0, -bh * 0.95)
                mid_pt = rot(m * bw * 0.85, -bh * 0.5)
                rim_pt = rot(m * bw, 1.5)
                canvas.create_line(apex_pt[0], apex_pt[1], mid_pt[0], mid_pt[1], rim_pt[0], rim_pt[1],
                                   fill=pal['striae'], width=1.1, smooth=True, tags="jellyfish_creature")
                # Luminous node along the canal
                canvas.create_oval(mid_pt[0]-1.2, mid_pt[1]-1.2, mid_pt[0]+1.2, mid_pt[1]+1.2,
                                   fill=pal['rim'], outline="", tags="jellyfish_creature")

            # Scalloped bottom rim glow band
            canvas.create_line([c for p in [rot(t * bw, 2.0) for t in [-1.0, -0.6, -0.2, 0.2, 0.6, 1.0]] for c in p],
                               fill=pal['rim'], width=1.8, smooth=True, tags="jellyfish_creature")
        except Exception:
            pass
