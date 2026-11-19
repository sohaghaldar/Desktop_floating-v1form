# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Spider Sub-Entities (Prey Insect & Baby Spiderlings)
"""

import math
import random
import time

class Insect:
    """Rich variety of insects: Realistic Mosquito, Butterfly, and Bioluminescent Firefly!"""
    TYPE_MOSQUITO = 'MOSQUITO'
    TYPE_BUTTERFLY = 'BUTTERFLY'
    TYPE_FIREFLY = 'FIREFLY'

    def __init__(self, target_hub, web_radius):
        self.type = random.choice([self.TYPE_MOSQUITO, self.TYPE_BUTTERFLY, self.TYPE_FIREFLY])
        angle = random.uniform(0, 2 * math.pi)
        dist = web_radius + random.uniform(90, 160)
        self.x = target_hub[0] + math.cos(angle) * dist
        self.y = target_hub[1] + math.sin(angle) * dist
        self.target_hub = target_hub
        self.web_radius = web_radius
        self.angle = math.atan2(target_hub[1] - self.y, target_hub[0] - self.x)
        self.wing_phase = 0.0
        self.trapped = False
        self.trapped_point = None
        self.size_scale = 1.0

    def update(self):
        # Flapping speed based on insect type
        if self.type == self.TYPE_MOSQUITO:
            self.wing_phase += 1.2
        elif self.type == self.TYPE_BUTTERFLY:
            self.wing_phase += 0.32
        else: # FIREFLY
            self.wing_phase += 0.65

        if self.trapped:
            if self.trapped_point:
                self.x = self.trapped_point[0] + (random.random() - 0.5) * 1.0
                self.y = self.trapped_point[1] + (random.random() - 0.5) * 1.0
            return

        dx = self.target_hub[0] - self.x
        dy = self.target_hub[1] - self.y
        dist = math.hypot(dx, dy)
        self.angle = math.atan2(dy, dx)

        if dist < self.web_radius * 0.90:
            self.trapped = True
            self.trapped_point = (self.x, self.y)
        else:
            speed = 2.2 if self.type == self.TYPE_MOSQUITO else (1.6 if self.type == self.TYPE_BUTTERFLY else 1.9)
            wave = math.sin(self.wing_phase * 0.5) * 0.6
            self.x += math.cos(self.angle + wave) * speed
            self.y += math.sin(self.angle + wave) * speed

class BabySpider:
    """Cute tiny baby spider that emerges from egg sac and can scatter."""
    def __init__(self, mother, offset_x, offset_y):
        self.mother = mother
        self.ox = offset_x
        self.oy = offset_y
        self.x = mother.x
        self.y = mother.y
        self.vx = 0.0
        self.vy = 0.0
        self.on_back = True
        self.scatter_timer = 0.0
        self.walk_phase = random.uniform(0, 10)

    def scatter(self):
        self.on_back = False
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(4.5, 7.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.scatter_timer = time.time() + random.uniform(3.0, 5.0)

    def update(self):
        cos_a = math.cos(self.mother.angle)
        sin_a = math.sin(self.mother.angle)
        rx = self.ox * cos_a - self.oy * sin_a
        ry = self.ox * sin_a + self.oy * cos_a
        target_x = self.mother.x + rx
        target_y = self.mother.y + ry

        if self.on_back:
            self.x = target_x
            self.y = target_y
        else:
            self.walk_phase += 0.28
            now = time.time()
            if now < self.scatter_timer:
                self.vx *= 0.965
                self.vy *= 0.965
                self.x += self.vx
                self.y += self.vy
            else:
                # Return quickly to mother's back with adaptive catchup speed
                dx = target_x - self.x
                dy = target_y - self.y
                dist = math.hypot(dx, dy)
                if dist > 16.0:
                    ang = math.atan2(dy, dx)
                    spd = min(15.0, max(5.5, dist / 6.0))
                    self.x += math.cos(ang) * spd
                    self.y += math.sin(ang) * spd
                else:
                    self.on_back = True
                    self.x = target_x
                    self.y = target_y

            # Keep babies within virtual screen boundaries so they never get lost/stuck off-screen
            pad = 20
            min_x = self.mother.screen_x + pad
            max_x = self.mother.screen_x + self.mother.screen_w - pad
            min_y = self.mother.screen_y + pad
            max_y = self.mother.screen_y + self.mother.screen_h - pad
            if self.x < min_x: self.x = min_x; self.vx = abs(self.vx)
            elif self.x > max_x: self.x = max_x; self.vx = -abs(self.vx)
            if self.y < min_y: self.y = min_y; self.vy = abs(self.vy)
            elif self.y > max_y: self.y = max_y; self.vy = -abs(self.vy)


