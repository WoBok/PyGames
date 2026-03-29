"""方块渲染器"""

import math
import pygame
from typing import Tuple, Optional

from ..config import GRID_SIZE
from .surface_cache import SurfaceCache


class BlockRenderer:
    """方块渲染器 - 霓虹风格"""

    def __init__(self, cache: Optional[SurfaceCache] = None):
        self.cache = cache or SurfaceCache.get_instance()
        self.time = 0
        self.block_flash = 0

    def update_time(self, dt: float) -> None:
        """更新时间（用于动画）"""
        self.time += dt

    def set_block_flash(self, flash: float) -> None:
        """设置方块闪光效果"""
        self.block_flash = flash

    def draw_neon_block(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        size: int = GRID_SIZE
    ) -> None:
        """绘制霓虹方块"""
        breath = 0.92 + 0.08 * math.sin(self.time * 3)
        r, g, b = color

        # 升级闪光效果
        if self.block_flash > 0:
            flash_intensity = self.block_flash ** 0.7
            r = min(255, int(r + (255 - r) * flash_intensity * 0.8))
            g = min(255, int(g + (255 - g) * flash_intensity * 0.7))
            b = min(255, int(b + (255 - b) * flash_intensity * 0.5))
            breath = min(1.5, breath + flash_intensity * 0.5)
        else:
            r = min(255, int(r * breath))
            g = min(255, int(g * breath))
            b = min(255, int(b * breath))

        # 创建光晕层
        glow_surf = pygame.Surface((size + 16, size + 16), pygame.SRCALPHA)
        for i in range(8, 0, -2):
            alpha = int(25 * (1 - i / 8))
            pygame.draw.rect(glow_surf, (r, g, b, alpha), (8 - i, 8 - i, size + i * 2, size + i * 2), border_radius=5)
        surface.blit(glow_surf, (x - 8, y - 8))

        # 创建方块主体
        block_surf = pygame.Surface((size, size), pygame.SRCALPHA)

        pygame.draw.rect(block_surf, (r // 4, g // 4, b // 4, 200), (0, 0, size, size), border_radius=4)

        inner_margin = 3
        inner_size = size - inner_margin * 2
        pygame.draw.rect(block_surf, (r, g, b, 60), (inner_margin, inner_margin, inner_size, inner_size), border_radius=3)

        # 玻璃高光效果
        for i in range(inner_size // 3):
            alpha = int(80 * (1 - i / (inner_size // 3)))
            pygame.draw.line(
                block_surf, (255, 255, 255, alpha),
                (inner_margin + 2, inner_margin + 2 + i),
                (inner_size + inner_margin - 2, inner_margin + 2 + i)
            )

        pygame.draw.rect(block_surf, (255, 255, 255, 40), (inner_margin + 2, inner_margin + 2, 3, inner_size - 4), border_radius=2)
        pygame.draw.rect(block_surf, (0, 0, 0, 60), (size - inner_margin - 5, inner_margin + 2, 3, inner_size - 4), border_radius=2)
        pygame.draw.rect(block_surf, (0, 0, 0, 40), (inner_margin + 2, size - inner_margin - 4, inner_size - 4, 3), border_radius=2)
        pygame.draw.rect(block_surf, (r, g, b, 200), (0, 0, size, size), 2, border_radius=4)
        pygame.draw.rect(
            block_surf,
            (min(255, r + 50), min(255, g + 50), min(255, b + 50), 150),
            (1, 1, size - 2, size - 2), 1, border_radius=3
        )

        surface.blit(block_surf, (x, y))

    def draw_ghost_block(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        size: int = GRID_SIZE
    ) -> None:
        """绘制幽灵方块"""
        breath = 0.7 + 0.3 * math.sin(self.time * 2)
        ghost_surf = pygame.Surface((size, size), pygame.SRCALPHA)

        # 光晕
        glow_surf = pygame.Surface((size + 8, size + 8), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            alpha = int(30 * breath * (1 - i / 4))
            pygame.draw.rect(glow_surf, (*color, alpha), (4 - i, 4 - i, size + i * 2, size + i * 2), border_radius=4)
        ghost_surf.blit(glow_surf, (-4, -4))

        # 主体
        pygame.draw.rect(ghost_surf, (*color, int(30 * breath)), (0, 0, size, size), border_radius=3)
        pygame.draw.rect(ghost_surf, (*color, int(120 * breath)), (0, 0, size, size), 2, border_radius=3)

        # 高光
        highlight_color = (min(255, color[0] + 100), min(255, color[1] + 100), min(255, color[2] + 100))
        pygame.draw.rect(ghost_surf, (*highlight_color, int(80 * breath)), (1, 1, size - 2, size - 2), 1, border_radius=2)

        surface.blit(ghost_surf, (x, y))