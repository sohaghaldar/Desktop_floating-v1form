# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Royal Crested Bird & Chick Nest
Features graceful long-legged bird, royal crown plumage, custom nest placement, and parent-chick interactions.
"""

import math
import random
import time
from core.platform_helper import play_audio, PlatformHelper
from core.config import save_config_value, load_config

BIRD_PLUMAGE_THEMES = [
    {
        "name": "Royal Crown Crane",
        "primary": "#f8fafc", "secondary": "#0f172a", "crest": "#facc15",
        "crest_tip": "#dc2626", "beak": "#d97706", "legs": "#334155",
        "wing": "#1e293b", "tail": "#0f172a", "nest_wood": "#78350f", "nest_down": "#fef3c7"
    },
    {
        "name": "Peacock of Paradise",
        "primary": "#0284c7", "secondary": "#047857", "crest": "#10b981",
        "crest_tip": "#38bdf8", "beak": "#ca8a04", "legs": "#1e293b",
        "wing": "#0369a1", "tail": "#059669", "nest_wood": "#713f12", "nest_down": "#a7f3d0"
    },
    {
        "name": "Solar Phoenix",
        "primary": "#ea580c", "secondary": "#b91c1c", "crest": "#fde047",
        "crest_tip": "#ef4444", "beak": "#f59e0b", "legs": "#451a03",
        "wing": "#c2410c", "tail": "#f97316", "nest_wood": "#854d0e", "nest_down": "#fef08a"
    },
    {
        "name": "Celestial Heron",
        "primary": "#e0e7ff", "secondary": "#4338ca", "crest": "#818cf8",
        "crest_tip": "#38bdf8", "beak": "#6366f1", "legs": "#1e1b4b",
        "wing": "#4f46e5", "tail": "#6366f1", "nest_wood": "#475569", "nest_down": "#e0e7ff"
    }
]

class RoyalCrestedBird:
    """Magnificent Royal Crested Crane / Bird of Paradise & Nest (ঝুটিওয়ালা পাখি ও বাসা):
    - Slender elongated wading legs with articulated knee & ankle joints ("halka patla boro leg").
    - Spectacular radiating crown crest plume on head with jewel teardrop tufts ("mathay boro juti").
    - Exquisitely woven round twig and soft feather nest ("bassa").
    - NEST POSITION CUSTOMIZATION: Press Shift + ` to relocate nest directly to mouse cursor!
    - Dynamic behaviors: Preens crest feathers, bobs head, perches on nest, flies majestically,
      circles mouse cursor, catches golden seeds, and lands peacefully back in its nest!"""
    def __init__(self, app):
        self.app = app
        self.theme_idx = int(app.config.get("BIRD_THEME_INDEX", 0)) % len(BIRD_PLUMAGE_THEMES)
        self.theme = BIRD_PLUMAGE_THEMES[self.theme_idx]

        # Nest Location (Customizable via Shift+`)
        self.nest_x = float(app.config.get("BIRD_NEST_X", app.screen_x + app.screen_w - 240))
        self.nest_y = float(app.config.get("BIRD_NEST_Y", app.screen_y + 190))

        # Bird state & kinematic variables
        self.state = "PERCHED" # PERCHED, FLYING, WALKING
        self.x = self.nest_x
        self.y = self.nest_y - 18.0
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.target_angle = 0.0
        self.wing_flap = 0.0
        self.walk_phase = 0.0
        self.preen_phase = 0.0
        self.flight_target_x = self.nest_x
        self.flight_target_y = self.nest_y
        self.last_flight_time = time.time()
        self.seeds = []
        self.song_notes = []

    def set_nest_spot_from_cursor(self):
        mx, my = self.app.get_mouse_pos()
        self.nest_x = float(mx)
        self.nest_y = float(my)
        save_config_value("BIRD_NEST_X", int(self.nest_x))
        save_config_value("BIRD_NEST_Y", int(self.nest_y))
        if self.state == "PERCHED":
            self.x = self.nest_x
            self.y = self.nest_y - 18.0
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(900, 50, 1200, 60)
        print(f"[*] Bird Nest Relocated to: ({int(self.nest_x)}, {int(self.nest_y)})")

    def cycle_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(BIRD_PLUMAGE_THEMES)
        self.theme = BIRD_PLUMAGE_THEMES[self.theme_idx]
        save_config_value("BIRD_THEME_INDEX", self.theme_idx)
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(650, 40, 950, 50)

    def trigger_song_flight(self):
        """Melodic call and majestic flight take-off (Shift+F)."""
        self.state = "FLYING"
        self.last_flight_time = time.time()
        mx, my = self.app.get_mouse_pos()
        self.flight_target_x = float(mx)
        self.flight_target_y = float(my)
        for i in range(4):
            self.song_notes.append({
                'x': self.x + random.uniform(-10, 10),
                'y': self.y - 20 - i * 8,
                'life': 1.0, 'note': random.choice(["♪", "♫", "✨"])
            })
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(1050, 60, 1450, 80)

    def return_to_nest(self):
        self.flight_target_x = self.nest_x
        self.flight_target_y = self.nest_y - 18.0

    def update(self, now):
        try:
            # 1. Melodic song notes floating upward
            for note in self.song_notes[:]:
                note['y'] -= 1.2
                note['life'] -= 0.024
                if note['life'] <= 0:
                    self.song_notes.remove(note)

            mx, my = self.app.get_mouse_pos()

            # Target position directly companioning the mouse cursor (above-left)
            target_ox = -26.0
            target_oy = -34.0
            tx = mx + target_ox
            ty = my + target_oy

            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if self.state == "PERCHED":
                self.x = self.nest_x
                self.y = self.nest_y - 18.0
                self.angle = 0.0
                self.preen_phase += 0.05
                # If mouse moves or after 4s, take off to companion cursor
                dist_to_mouse = math.hypot(mx - self.x, my - self.y)
                if dist_to_mouse < 200.0 or (now - self.last_flight_time > 4.5):
                    self.trigger_song_flight()
            else:
                self.state = "FLYING"
                self.wing_flap += 0.28

                # Smoothly track mouse cursor with banking tilt
                if dist > 14.0:
                    self.target_angle = math.atan2(dy, dx)
                    # Dynamic responsive flight speed up to 8.5px/frame
                    spd = min(8.5, 3.2 + (dist / 38.0))
                else:
                    # Hovering peacefully right next to cursor
                    spd = dist * 0.16
                    self.target_angle = self.angle + math.sin(now * 2.2) * 0.12
                    # Sweet occasional singing when near mouse
                    if random.random() < 0.02:
                        self.song_notes.append({
                            'x': self.x + random.uniform(-10, 10),
                            'y': self.y - 15.0,
                            'note': random.choice(["♪", "♫", "♬", "♩"]),
                            'life': 1.0
                        })
                        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED and random.random() < 0.25:
                            play_audio(random.choice([1200, 1450, 1650]), 25, random.choice([1800, 2100]), 35)

                diff = self.target_angle - self.angle
                while diff < -math.pi: diff += math.pi * 2
                while diff > math.pi: diff -= math.pi * 2
                self.angle += diff * 0.14

                self.vx = math.cos(self.angle) * spd
                self.vy = math.sin(self.angle) * spd
                self.x += self.vx
                self.y += self.vy

            # Boundary safety clamps
            sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h
            pad = 35.0
            if self.x < sx + pad: self.x = sx + pad
            if self.x > sx + sw - pad: self.x = sx + sw - pad
            if self.y < sy + pad: self.y = sy + pad
            if self.y > sy + sh - pad: self.y = sy + sh - pad
        except Exception:
            pass

    def draw(self, canvas):
        canvas.delete("bird_creature")
        try:
            pal = self.theme

            # 1. Melodic Song Notes
            for note in self.song_notes:
                canvas.create_text(note['x'], note['y'], text=note['note'],
                                   font=("Segoe UI", 12, "bold"), fill=pal['crest'], tags="bird_creature")

            # 2. Woven Twig & Feather Nest ("বাসা")
            nx, ny = self.nest_x, self.nest_y
            # Woven twig ring base
            canvas.create_oval(nx - 28, ny - 10, nx + 28, ny + 12,
                               fill=pal['nest_wood'], outline="#451a03", width=1.5, tags="bird_creature")
            # Interior cosy down cushion
            canvas.create_oval(nx - 22, ny - 8, nx + 22, ny + 8,
                               fill=pal['nest_down'], outline="#a16207", width=1.0, tags="bird_creature")
            # Criss-cross woven twigs
            for twig_deg in [-30, -10, 15, 35]:
                rad = math.radians(twig_deg)
                canvas.create_line(nx - math.cos(rad)*26, ny + math.sin(rad)*8,
                                   nx + math.cos(rad)*26, ny - math.sin(rad)*8,
                                   fill="#451a03", width=1.2, tags="bird_creature")

            # 3. Bird Body & Long Legs Kinematics
            bx, by = self.x, self.y
            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)

            if self.state == "PERCHED":
                # Perched on nest with legs resting and long neck upright
                # Long Slender Legs ("halka patla boro leg")
                leg_col = pal['legs']
                # Left leg
                canvas.create_line(bx - 4, by + 4, bx - 6, by + 12, bx - 8, ny,
                                   fill=leg_col, width=1.8, tags="bird_creature")
                canvas.create_line(bx - 8, ny, bx - 13, ny + 1, fill=leg_col, width=1.4, tags="bird_creature")
                # Right leg
                canvas.create_line(bx + 4, by + 4, bx + 6, by + 12, bx + 8, ny,
                                   fill=leg_col, width=1.8, tags="bird_creature")
                canvas.create_line(bx + 8, ny, bx + 13, ny + 1, fill=leg_col, width=1.4, tags="bird_creature")

                # Long flowing paradise tail feathers hanging down
                canvas.create_line(bx - 12, by + 6, bx - 22, by + 26, bx - 26, by + 38,
                                   fill=pal['tail'], width=2.4, smooth=True, tags="bird_creature")
                canvas.create_line(bx - 10, by + 6, bx - 18, by + 28, bx - 20, by + 42,
                                   fill=pal['secondary'], width=1.8, smooth=True, tags="bird_creature")

                # Sleek body oval
                canvas.create_oval(bx - 14, by - 8, bx + 14, by + 8,
                                   fill=pal['primary'], outline=pal['secondary'], width=1.2, tags="bird_creature")

                # Folded wing with primary feather lines
                canvas.create_polygon([bx - 10, by - 4, bx + 8, by - 5, bx + 12, by + 2, bx - 8, by + 6],
                                      fill=pal['wing'], outline="#020617", width=1.0, tags="bird_creature")

                # Elegant S-curved crane neck
                head_x = bx + 14.0
                head_y = by - 16.0 + math.sin(self.preen_phase) * 2.0
                canvas.create_line(bx + 8, by - 2, bx + 11, by - 9, head_x, head_y,
                                   fill=pal['primary'], width=3.8, smooth=True, tags="bird_creature")

                # Graceful head capsule
                canvas.create_oval(head_x - 5, head_y - 4, head_x + 5, head_y + 4,
                                   fill=pal['primary'], outline=pal['secondary'], width=0.8, tags="bird_creature")

                # Sharp slender beak
                canvas.create_polygon([head_x + 4, head_y - 1.5, head_x + 14, head_y, head_x + 4, head_y + 1.5],
                                      fill=pal['beak'], outline="#78350f", width=0.6, tags="bird_creature")

                # Bright golden eye
                canvas.create_oval(head_x + 1, head_y - 2.5, head_x + 3.5, head_y - 0.5,
                                   fill="#fef08a", outline="#0f172a", width=0.6, tags="bird_creature")

                # SPECTACULAR CROWN CREST PLUME ("mathay boro juti")
                # Fans out proudly from the top of the head with jewel teardrop plumes
                for crest_i, c_angle in enumerate([-45, -25, -5, 15, 35]):
                    rad = math.radians(c_angle - 70)
                    cx1 = head_x + math.cos(rad) * 6.0
                    cy1 = head_y + math.sin(rad) * 6.0
                    cx2 = head_x + math.cos(rad) * 16.0
                    cy2 = head_y + math.sin(rad) * 16.0
                    canvas.create_line(head_x, head_y - 2, cx1, cy1, cx2, cy2,
                                       fill=pal['crest'], width=1.4, tags="bird_creature")
                    # Jewel teardrop tuft at tip
                    canvas.create_oval(cx2 - 1.8, cy2 - 1.8, cx2 + 1.8, cy2 + 1.8,
                                       fill=pal['crest_tip'], outline="#ffffff", width=0.6, tags="bird_creature")

            elif self.state == "FLYING":
                # In Flight: Aerodynamic body, broad flapping wings, trailing long legs
                flap_scale = math.sin(self.wing_flap)
                # Broad wings
                w_span = 32.0
                wing_tip_y = flap_scale * 18.0
                norm_x = -sin_a
                norm_y = cos_a

                # Wing Left & Right
                w_l = (bx + norm_x * w_span, by + norm_y * w_span + wing_tip_y)
                w_r = (bx - norm_x * w_span, by - norm_y * w_span - wing_tip_y)

                # Wing polygons with flight feathers
                canvas.create_polygon([bx - cos_a * 8, by - sin_a * 8, w_l[0], w_l[1], bx + cos_a * 8, by + sin_a * 8],
                                      fill=pal['wing'], outline=pal['secondary'], width=1.2, tags="bird_creature")
                canvas.create_polygon([bx - cos_a * 8, by - sin_a * 8, w_r[0], w_r[1], bx + cos_a * 8, by + sin_a * 8],
                                      fill=pal['wing'], outline=pal['secondary'], width=1.2, tags="bird_creature")

                # Trailing long legs tucked back
                canvas.create_line(bx - cos_a * 10, by - sin_a * 10, bx - cos_a * 24, by - sin_a * 24,
                                   fill=pal['legs'], width=1.8, tags="bird_creature")

                # Flowing paradise tail streaming behind
                canvas.create_line(bx - cos_a * 10, by - sin_a * 10, bx - cos_a * 32, by - sin_a * 32,
                                   fill=pal['tail'], width=2.4, tags="bird_creature")

                # Aerodynamic body
                canvas.create_oval(bx - 7, by - 7, bx + 7, by + 7,
                                   fill=pal['primary'], outline=pal['secondary'], width=1.0, tags="bird_creature")

                # Head & Beak pointing in direction of flight
                hx = bx + cos_a * 14.0
                hy = by + sin_a * 14.0
                canvas.create_oval(hx - 4, hy - 4, hx + 4, hy + 4, fill=pal['primary'], outline="", tags="bird_creature")
                canvas.create_line(hx, hy, hx + cos_a * 8, hy + sin_a * 8, fill=pal['beak'], width=2.0, tags="bird_creature")

                # Crest swept back dynamically in flight
                for c_deg in [-20, 0, 20]:
                    rad = self.angle + math.pi + math.radians(c_deg)
                    cx2 = hx + math.cos(rad) * 12.0
                    cy2 = hy + math.sin(rad) * 12.0
                    canvas.create_line(hx, hy, cx2, cy2, fill=pal['crest'], width=1.2, tags="bird_creature")
                    canvas.create_oval(cx2 - 1.5, cy2 - 1.5, cx2 + 1.5, cy2 + 1.5,
                                       fill=pal['crest_tip'], outline="", tags="bird_creature")
        except Exception:
            pass

