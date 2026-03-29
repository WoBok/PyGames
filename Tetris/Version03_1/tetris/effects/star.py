"""背景星星效果类"""

import math
import random
import pygame

from ..config import SCREEN_WIDTH, SCREEN_HEIGHT


class Star:
    """背景星星闪烁效果"""

    def __init__(self, x: float, y: float, screen_width: int = SCREEN_WIDTH, screen_height: int = SCREEN_HEIGHT):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = random.randint(1, 3)
        self.brightness = random.uniform(0.3, 1.0)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.5, 2.0)
        self.life_phase = random.uniform(0, math.pi * 2)
        self.fading_out = False
        self.fade_speed = random.uniform(0.002, 0.005)

    def update(self, time: float) -> None:
        """更新星星状态"""
        self.life_phase += self.fade_speed
        fade_factor = 0.5 + 0.5 * math.sin(self.life_phase)

        if fade_factor < 0.2:
            self.fading_out = True
        elif fade_factor > 0.8 and self.fading_out:
            self.x = random.randint(0, self.screen_width)
            self.y = random.randint(0, self.screen_height)
            self.fading_out = False
            self.life_phase = random.uniform(0, math.pi * 2)

        self.brightness = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(time * self.speed + self.phase)) * fade_factor

    def draw(self, surface: pygame.Surface) -> None:
        """绘制星星"""
        alpha = int(255 * self.brightness)
        color = (alpha, alpha, alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)