"""浮动文字效果类"""

import math
import random
import pygame
from typing import Tuple

from ..config import SCREEN_WIDTH, SCREEN_HEIGHT


class FloatingText:
    """浮动文字动画效果"""

    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        color: Tuple[int, int, int],
        size: int = 24,
        is_tetris: bool = False,
        combo_count: int = 0
    ):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.base_size = int(size * 1.3)
        self.life = 1.0
        self.vy = -1.0
        self.scale = 0.5
        self.alpha = 0
        self.is_tetris = is_tetris
        self.combo_count = combo_count
        self.shake_offset = 0
        self.neon_pulse = 0
        self.shake_phase = 0
        self.shake_speed = 8
        self.rainbow_phase = 0

        # 动画阶段
        self.phase = 'fade_in'
        self.phase_timer = 0
        self.fade_in_duration = 0.25
        self.hold_duration = 0.8
        self.fade_out_duration = 0.5

    def update(self, dt: float = 0.016) -> None:
        """更新动画状态"""
        self.neon_pulse += 8 * dt
        self.shake_phase += self.shake_speed * dt * 6
        self.rainbow_phase += 6 * dt

        if self.shake_offset > 0:
            self.shake_offset *= 0.95

        self.y += self.vy * dt * 60
        self.phase_timer += dt

        if self.phase == 'fade_in':
            progress = min(1, self.phase_timer / self.fade_in_duration)
            ease_progress = 1 - (1 - progress) ** 2
            self.scale = 0.7 + 0.3 * ease_progress
            self.alpha = int(255 * ease_progress)

            if progress >= 1:
                self.phase = 'hold'
                self.phase_timer = 0
                self.scale = 1.0
                self.alpha = 255
                if self.is_tetris or self.combo_count > 0:
                    self.shake_offset = 2

        elif self.phase == 'hold':
            self.scale = 1.0
            self.alpha = 255

            if self.phase_timer >= self.hold_duration:
                self.phase = 'fade_out'
                self.phase_timer = 0

        elif self.phase == 'fade_out':
            progress = min(1, self.phase_timer / self.fade_out_duration)
            ease_progress = progress ** 2
            self.scale = 1.0
            self.alpha = int(255 * (1 - ease_progress))
            self.life = 1 - progress

    def get_rainbow_color(self, offset: float = 0) -> Tuple[int, int, int]:
        """获取彩虹颜色"""
        phase = self.rainbow_phase + offset
        return (
            int(127 + 127 * math.sin(phase)),
            int(127 + 127 * math.sin(phase + 2.094)),
            int(127 + 127 * math.sin(phase + 4.189)),
        )

    def get_gold_color(self, pulse: float) -> Tuple[int, int, int]:
        """获取金色脉冲颜色"""
        pulse_intensity = 0.5 + 0.5 * math.sin(pulse)
        return (
            255,
            int(215 + 40 * pulse_intensity),
            int(50 + 50 * pulse_intensity),
        )

    def draw_tetris_text(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        x: int,
        y: int,
        alpha: int
    ) -> None:
        """绘制TETRIS专用炫酷文字"""
        pulse = 0.7 + 0.3 * math.sin(self.neon_pulse)

        text_surf = font.render(text, True, (255, 255, 255))
        text_width = text_surf.get_width()
        text_height = text_surf.get_height()

        glow_size = 8
        total_width = text_width + glow_size * 4
        total_height = text_height + glow_size * 4
        glow_surf = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

        # 多层彩虹光晕
        for layer in range(glow_size, 0, -1):
            layer_progress = layer / glow_size
            rainbow_offset = layer * 0.3
            rainbow_color = self.get_rainbow_color(rainbow_offset)
            g_alpha = int(60 * pulse * layer_progress)

            for dx in range(-layer, layer + 1, 1):
                for dy in range(-layer, layer + 1, 1):
                    if dx * dx + dy * dy <= layer * layer:
                        temp_surf = font.render(text, True, rainbow_color)
                        temp_surf.set_alpha(g_alpha)
                        glow_surf.blit(temp_surf, (glow_size * 2 + dx, glow_size * 2 + dy))

        # 金色中层光晕
        gold_color = self.get_gold_color(self.neon_pulse * 2)
        for dx in range(-2, 3, 1):
            for dy in range(-2, 3, 1):
                if dx != 0 or dy != 0:
                    temp_surf = font.render(text, True, gold_color)
                    temp_surf.set_alpha(int(150 * pulse))
                    glow_surf.blit(temp_surf, (glow_size * 2 + dx, glow_size * 2 + dy))

        glow_surf.set_alpha(alpha)
        surface.blit(glow_surf, (x - glow_size * 2, y - glow_size * 2))

        # 白色核心文字
        core_surf = font.render(text, True, (255, 255, 255))
        core_surf.set_alpha(alpha)
        surface.blit(core_surf, (x, y))

        # 金色高光
        highlight_surf = font.render(text, True, gold_color)
        highlight_surf.set_alpha(int(alpha * 0.6 * pulse))
        surface.blit(highlight_surf, (x + 1, y + 1))

        # 闪烁星星效果
        for i in range(5):
            star_phase = self.rainbow_phase * 3 + i * 1.2
            star_alpha = int(alpha * 0.8 * (0.5 + 0.5 * math.sin(star_phase)))
            if star_alpha > 30:
                star_x = x + random.randint(0, text_width)
                star_y = y + random.randint(0, text_height // 2)
                star_size = random.randint(2, 4)
                star_surf = pygame.Surface((star_size * 4, star_size * 4), pygame.SRCALPHA)
                pygame.draw.circle(
                    star_surf,
                    (*self.get_rainbow_color(i), star_alpha),
                    (star_size * 2, star_size * 2),
                    star_size
                )
                surface.blit(star_surf, (star_x - star_size * 2, star_y - star_size * 2))

    def draw_neon_text(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        alpha: int
    ) -> None:
        """绘制霓虹文字"""
        pulse = 0.7 + 0.3 * math.sin(self.neon_pulse)

        text_surf = font.render(text, True, color)

        glow_size = 2
        glow_surf = pygame.Surface(
            (text_surf.get_width() + glow_size * 4, text_surf.get_height() + glow_size * 4),
            pygame.SRCALPHA
        )

        for i in range(glow_size * 2, 0, -1):
            g_alpha = int(40 * pulse * (1 - i / (glow_size * 2)))
            for dx in range(-i, i + 1):
                for dy in range(-i, i + 1):
                    if dx * dx + dy * dy <= i * i:
                        temp_surf = font.render(text, True, color)
                        temp_surf.set_alpha(g_alpha)
                        glow_surf.blit(temp_surf, (glow_size * 2 + dx, glow_size * 2 + dy))

        glow_surf.set_alpha(alpha)
        surface.blit(glow_surf, (x - glow_size * 2, y - glow_size * 2))

        inner_surf = font.render(text, True, color)
        inner_surf.set_alpha(alpha)
        surface.blit(inner_surf, (x, y))

        highlight_surf = font.render(text, True, (255, 255, 255))
        highlight_surf.set_alpha(int(alpha * 0.3 * pulse))
        surface.blit(highlight_surf, (x + 1, y + 1))

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, font_name: str = None) -> None:
        """绘制浮动文字"""
        if self.alpha <= 0:
            return

        shake_x = int(math.sin(self.shake_phase) * self.shake_offset) if self.shake_offset > 0.5 else 0
        shake_y = int(math.cos(self.shake_phase * 1.3) * self.shake_offset) if self.shake_offset > 0.5 else 0

        new_size = max(8, int(self.base_size * self.scale))
        if self.is_tetris:
            new_size = int(new_size * 1.5)

        if font_name:
            scaled_font = pygame.font.SysFont(font_name, new_size, bold=True)
        else:
            scaled_font = pygame.font.Font(None, new_size, bold=True)

        text_surf = scaled_font.render(self.text, True, self.color)
        scaled_width = text_surf.get_width()
        scaled_height = text_surf.get_height()

        draw_x = int(self.x - scaled_width // 2 + shake_x)
        draw_y = int(self.y - scaled_height // 2 + shake_y)

        if self.is_tetris:
            self.draw_tetris_text(surface, scaled_font, self.text, draw_x, draw_y, self.alpha)
        else:
            self.draw_neon_text(surface, scaled_font, self.text, draw_x, draw_y, self.color, self.alpha)