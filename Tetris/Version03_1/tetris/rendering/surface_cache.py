"""Surface缓存管理"""

import pygame
from typing import Tuple, Dict, Optional


class SurfaceCache:
    """Surface缓存管理器 - 优化渲染性能"""

    _instance: Optional['SurfaceCache'] = None

    def __init__(self):
        self._cache: Dict[Tuple, pygame.Surface] = {}
        self._max_cache_size = 500

    @classmethod
    def get_instance(cls) -> 'SurfaceCache':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_block_surface(
        self,
        size: int,
        color: Tuple[int, int, int],
        alpha: int = 255,
        glow_size: int = 8
    ) -> pygame.Surface:
        """获取方块Surface（带光晕）"""
        cache_key = ('block', size, color, alpha, glow_size)
        if cache_key not in self._cache:
            surf = self._create_block_surface(size, color, alpha, glow_size)
            self._cache[cache_key] = surf
            self._check_cache_size()
        return self._cache[cache_key]

    def get_glow_surface(
        self,
        size: int,
        color: Tuple[int, int, int],
        alpha: int
    ) -> pygame.Surface:
        """获取光晕Surface"""
        cache_key = ('glow', size, color, alpha)
        if cache_key not in self._cache:
            surf = self._create_glow_surface(size, color, alpha)
            self._cache[cache_key] = surf
            self._check_cache_size()
        return self._cache[cache_key]

    def get_text_glow_surface(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        glow_size: int
    ) -> pygame.Surface:
        """获取文字光晕Surface"""
        cache_key = ('text_glow', text, id(font), color, glow_size)
        if cache_key not in self._cache:
            surf = self._create_text_glow_surface(text, font, color, glow_size)
            self._cache[cache_key] = surf
            self._check_cache_size()
        return self._cache[cache_key]

    def _create_block_surface(
        self,
        size: int,
        color: Tuple[int, int, int],
        alpha: int,
        glow_size: int
    ) -> pygame.Surface:
        """创建方块Surface"""
        total_size = size + glow_size * 2
        surf = pygame.Surface((total_size, total_size), pygame.SRCALPHA)

        # 绘制光晕
        for i in range(glow_size, 0, -1):
            g_alpha = int(alpha * 0.15 * (i / glow_size))
            r, g, b = color
            pygame.draw.rect(
                surf, (r, g, b, g_alpha),
                (glow_size - i, glow_size - i, size + i * 2, size + i * 2),
                border_radius=5
            )

        # 绘制方块主体
        block_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        r, g, b = color

        # 背景
        pygame.draw.rect(block_surf, (r // 4, g // 4, b // 4, alpha), (0, 0, size, size), border_radius=4)

        # 内部
        inner_margin = 3
        inner_size = size - inner_margin * 2
        pygame.draw.rect(block_surf, (r, g, b, int(alpha * 0.6)), (inner_margin, inner_margin, inner_size, inner_size), border_radius=3)

        # 高光
        for i in range(inner_size // 3):
            h_alpha = int(alpha * 0.8 * (1 - i / (inner_size // 3)))
            pygame.draw.line(
                block_surf, (255, 255, 255, h_alpha),
                (inner_margin + 2, inner_margin + 2 + i),
                (inner_size + inner_margin - 2, inner_margin + 2 + i)
            )

        # 边框
        pygame.draw.rect(block_surf, (r, g, b, alpha), (0, 0, size, size), 2, border_radius=4)
        pygame.draw.rect(
            block_surf,
            (min(255, r + 50), min(255, g + 50), min(255, b + 50), int(alpha * 0.6)),
            (1, 1, size - 2, size - 2), 1, border_radius=3
        )

        surf.blit(block_surf, (glow_size, glow_size))
        return surf

    def _create_glow_surface(
        self,
        size: int,
        color: Tuple[int, int, int],
        alpha: int
    ) -> pygame.Surface:
        """创建光晕Surface"""
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        for i in range(size, 0, -1):
            g_alpha = int(alpha * (i / size) * 0.5)
            pygame.draw.circle(surf, (*color, g_alpha), (size, size), i)
        return surf

    def _create_text_glow_surface(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        glow_size: int
    ) -> pygame.Surface:
        """创建文字光晕Surface"""
        text_surf = font.render(text, True, color)
        total_width = text_surf.get_width() + glow_size * 4
        total_height = text_surf.get_height() + glow_size * 4
        surf = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

        for dx in range(-glow_size, glow_size + 1):
            for dy in range(-glow_size, glow_size + 1):
                if dx * dx + dy * dy <= glow_size * glow_size:
                    temp_surf = font.render(text, True, color)
                    temp_surf.set_alpha(30)
                    surf.blit(temp_surf, (glow_size * 2 + dx, glow_size * 2 + dy))

        return surf

    def _check_cache_size(self) -> None:
        """检查缓存大小并清理"""
        if len(self._cache) > self._max_cache_size:
            # 删除一半的缓存
            keys = list(self._cache.keys())[:self._max_cache_size // 2]
            for key in keys:
                del self._cache[key]

    def clear(self) -> None:
        """清除所有缓存"""
        self._cache.clear()

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            'cache_size': len(self._cache),
            'max_size': self._max_cache_size,
        }