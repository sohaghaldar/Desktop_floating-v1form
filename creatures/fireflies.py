# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Bioluminescent Fireflies Swarm
Features softly hovering nocturnal fireflies with organic pulsing light lanterns.
"""

import math
import random
import time
from core.platform_helper import play_audio, PlatformHelper

class FireflySwarm:
    """Authentic Bioluminescent Firefly Swarm (জোনাকি পোকার ঝাঁক):
    - Real insect silhouette: dark beetle pronotum, folded elytra, fluttering gossamer wings!
    - Glowing abdominal lantern (photophore) with natural organic sinusoidal breathing luminescence.
    - Soft multi-layered radiant glow aura around each lantern.
    - Swarm flight dynamics: gentle organic hovering, bobbing, darting.
    - Shift+F Synchronous Swarm Flash: all fireflies flash in bright golden harmony!"""
    def __init__(self, app):
        self.app = app
        self.num_bugs = 14
        self.bugs = []
        sx, sy, sw, sh = app.screen_x, app.screen_y, app.screen_w, app.screen_h
        for _ in range(self.num_bugs):
            self.bugs.append({
                'x': random.uniform(sx + 150, sx + sw - 150),
                'y': random.uniform(sy + 100, sy + sh - 150),
                'vx': random.uniform(-0.8, 0.8),
                'vy': random.uniform(-0.6, 0.6),
                'angle': random.uniform(0, 2 * math.pi),
                'wing_phase': random.uniform(0, 6.28),
                'blink_phase': random.uniform(0, 6.28),
                'blink_speed': random.uniform(0.045, 0.085),
                'sync_burst': 0.0
            })

    def trigger_flash(self):
        """Synchronous swarm flash wave!"""
        for b in self.bugs:
            b['sync_burst'] = 1.0
        if hasattr(self.app, 'SOUND_ENABLED') and self.app.SOUND_ENABLED:
            play_audio(850, 40, 1250, 60)

    def update(self, now):
        mx, my = self.app.get_mouse_pos()
        sx, sy, sw, sh = self.app.screen_x, self.app.screen_y, self.app.screen_w, self.app.screen_h

        for b in self.bugs:
            b['wing_phase'] += 0.45
            b['blink_phase'] += b['blink_speed']
            if b['sync_burst'] > 0:
                b['sync_burst'] = max(0.0, b['sync_burst'] - 0.035)

            # Gentle attraction to mouse with chaotic flutter
            dx = mx - b['x']
            dy = my - b['y']
            dist = math.hypot(dx, dy)
            if dist > 80:
                b['vx'] += (dx / dist) * 0.045
                b['vy'] += (dy / dist) * 0.045

            b['vx'] += random.uniform(-0.15, 0.15)
            b['vy'] += random.uniform(-0.15, 0.15)
            spd = math.hypot(b['vx'], b['vy'])
            if spd > 2.8:
                b['vx'] = (b['vx'] / spd) * 2.8
                b['vy'] = (b['vy'] / spd) * 2.8

            b['x'] += b['vx']
            b['y'] += b['vy']
            b['angle'] = math.atan2(b['vy'], b['vx'])

            # Screen bounds reflection
            if b['x'] < sx + 30: b['x'] = sx + 30; b['vx'] = abs(b['vx'])
            if b['x'] > sx + sw - 30: b['x'] = sx + sw - 30; b['vx'] = -abs(b['vx'])
            if b['y'] < sy + 30: b['y'] = sy + 30; b['vy'] = abs(b['vy'])
            if b['y'] > sy + sh - 30: b['y'] = sy + sh - 30; b['vy'] = -abs(b['vy'])

    def draw(self, canvas):
        canvas.delete("firefly_creature")
        try:
            for b in self.bugs:
                bx, by = b['x'], b['y']
                ang = b['angle']
                cos_a = math.cos(ang)
                sin_a = math.sin(ang)

                # Lantern luminescence intensity
                intensity = 0.3 + 0.7 * (math.sin(b['blink_phase']) ** 2)
                if b['sync_burst'] > 0:
                    intensity = max(intensity, b['sync_burst'])

                # 1. Soft radiant glow aura
                glow_r = 10.0 + intensity * 8.0
                canvas.create_oval(bx - glow_r, by - glow_r, bx + glow_r, by + glow_r,
                                   fill="#bef264", outline="", tags="firefly_creature")

                # 2. Gossamer fluttering wings
                wing_f = math.sin(b['wing_phase']) * 5.0
                canvas.create_line(bx, by, bx - sin_a * 7.0 - cos_a * 2.0, by + cos_a * 7.0 + wing_f,
                                   fill="#e2e8f0", width=1.1, tags="firefly_creature")
                canvas.create_line(bx, by, bx + sin_a * 7.0 - cos_a * 2.0, by - cos_a * 7.0 - wing_f,
                                   fill="#e2e8f0", width=1.1, tags="firefly_creature")

                # 3. Beetle body (head, pronotum, dark abdomen)
                canvas.create_oval(bx - 2.2, by - 2.2, bx + 2.2, by + 2.2,
                                   fill="#1c1917", outline="#44403c", width=0.8, tags="firefly_creature")
                hx = bx + cos_a * 3.5
                hy = by + sin_a * 3.5
                canvas.create_oval(hx - 1.2, hy - 1.2, hx + 1.2, hy + 1.2, fill="#0c0a09", outline="", tags="firefly_creature")

                # 4. Bioluminescent Lantern (Tail Photophore)
                tx = bx - cos_a * 3.2
                ty = by - sin_a * 3.2
                lr = 2.2 + intensity * 1.5
                lantern_col = "#fef08a" if intensity > 0.6 else "#84cc16"
                canvas.create_oval(tx - lr, ty - lr, tx + lr, ty + lr,
                                   fill=lantern_col, outline="#ffffff", width=0.6, tags="firefly_creature")
        except Exception:
            pass

