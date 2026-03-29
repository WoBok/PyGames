"""粒子效果类"""

import math
import random
import pygame
from typing import List, Tuple

from ..config import SPARK_COLORS


class Particle:
    """粒子效果类"""

    # 类级别的 Surface 缓存
    _glow_cache: dict = {}

    def __init__(self, x: float, y: float, color: Tuple[int, int, int], lines_cleared: int = 1):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        base_speed = random.uniform(3, 7)
        speed_multiplier = 1 + (lines_cleared - 1) * 0.2
        speed = base_speed * speed_multiplier
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(3, 5) * speed_multiplier
        self.color = random.choice(SPARK_COLORS) if random.random() > 0.3 else color
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.03)
        self.size = random.randint(3, 6)
        self.trail: List[Tuple[float, float, Tuple[int, int, int], float]] = []
        self.wind = random.uniform(-0.2, 0.2)
        self.turbulence = random.uniform(0, 0.3)
        self.turbulence_phase = random.uniform(0, math.pi * 2)
        self.alpha_bonus = (lines_cleared - 1) * 0.05

    def update(self) -> None:
        """更新粒子状态"""
        self.trail.append((self.x, self.y, self.color, self.life))
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.turbulence_phase += 0.1
        turbulence_x = math.sin(self.turbulence_phase) * self.turbulence
        turbulence_y = math.cos(self.turbulence_phase) * self.turbulence

        self.x += self.vx + self.wind + turbulence_x
        self.y += self.vy + turbulence_y
        self.vy += 0.12
        self.vx *= 0.985
        self.vy *= 0.985
        self.life -= self.decay

    def draw(self, surface: pygame.Surface) -> None:
        """绘制粒子"""
        if self.life <= 0:
            return
        trail_len = len(self.trail)
        alpha_multiplier = 1.5 + self.alpha_bonus

        # 绘制拖尾
        if trail_len > 0:
            for i, (tx, ty, tc, tl) in enumerate(self.trail):
                progress = (i + 1) / trail_len
                trail_alpha = min(255, int(100 * alpha_multiplier * tl * progress * 0.6))
                trail_size = max(1, int(self.size * progress * 0.7))
                cache_key = (trail_size, tc, trail_alpha)
                if cache_key not in Particle._glow_cache:
                    trail_surf = pygame.Surface((trail_size * 2 + 4, trail_size * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (*tc, trail_alpha), (trail_size + 2, trail_size + 2), trail_size)
                    Particle._glow_cache[cache_key] = trail_surf
                    if len(Particle._glow_cache) > 200:
                        keys = list(Particle._glow_cache.keys())[:100]
                        for k in keys:
                            del Particle._glow_cache[k]
                trail_surf = Particle._glow_cache[cache_key]
                surface.blit(trail_surf, (int(tx - trail_size - 2), int(ty - trail_size - 2)))

        alpha = min(255, int(240 * alpha_multiplier * self.life))
        size = max(1, int(self.size * self.life))

        # 缓存主粒子光晕
        cache_key = (size, self.color, alpha)
        if cache_key not in Particle._glow_cache:
            glow_surf = pygame.Surface((size * 4 + 4, size * 4 + 4), pygame.SRCALPHA)
            center = size * 2 + 2
            for i in range(size + 2, size, -1):
                g_alpha = min(255, int(alpha * 0.15 * (1 - (i - size) / 2)))
                pygame.draw.circle(glow_surf, (*self.color, g_alpha), (center, center), i)
            pygame.draw.circle(glow_surf, (*self.color, min(255, int(alpha * 0.7))), (center, center), size)
            Particle._glow_cache[cache_key] = glow_surf
            if len(Particle._glow_cache) > 200:
                keys = list(Particle._glow_cache.keys())[:100]
                for k in keys:
                    del Particle._glow_cache[k]
        glow_surf = Particle._glow_cache[cache_key]
        center = size * 2 + 2
        surface.blit(glow_surf, (int(self.x - center), int(self.y - center)))

    @classmethod
    def clear_cache(cls) -> None:
        """清除缓存"""
        cls._glow_cache.clear()