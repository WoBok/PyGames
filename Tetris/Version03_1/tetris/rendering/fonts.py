"""字体管理"""

import pygame
from typing import Optional, List, Tuple


class FontManager:
    """字体管理器"""

    _instance: Optional['FontManager'] = None

    # 中文字体列表
    CHINESE_FONTS = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei']

    def __init__(self):
        self.font_name: Optional[str] = None
        self._fonts = {}
        self._init_fonts()

    @classmethod
    def get_instance(cls) -> 'FontManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _init_fonts(self) -> None:
        """初始化字体"""
        # 尝试加载中文字体
        for name in self.CHINESE_FONTS:
            try:
                test_font = pygame.font.SysFont(name, 24)
                if test_font:
                    self.font_name = name
                    break
            except Exception:
                continue

        # 预加载常用字体
        self.get_font('tiny', 14)
        self.get_font('small', 16)
        self.get_font('medium', 32)
        self.get_font('large', 48)
        self.get_font('title_medium', 32, bold=True)
        self.get_font('title_large', 48, bold=True)
        self.get_font('title_xlarge', 72, bold=True)
        self.get_font('score', 20, bold=True)

    def get_font(self, name: str, size: int, bold: bool = False) -> pygame.font.Font:
        """获取字体"""
        cache_key = (name, size, bold)
        if cache_key not in self._fonts:
            if self.font_name:
                self._fonts[cache_key] = pygame.font.SysFont(self.font_name, size, bold=bold)
            else:
                self._fonts[cache_key] = pygame.font.Font(None, size, bold=bold)
        return self._fonts[cache_key]

    @property
    def tiny(self) -> pygame.font.Font:
        return self.get_font('tiny', 14)

    @property
    def small(self) -> pygame.font.Font:
        return self.get_font('small', 16)

    @property
    def medium(self) -> pygame.font.Font:
        return self.get_font('medium', 32)

    @property
    def large(self) -> pygame.font.Font:
        return self.get_font('large', 48)

    @property
    def title_medium(self) -> pygame.font.Font:
        return self.get_font('title_medium', 32, bold=True)

    @property
    def title_large(self) -> pygame.font.Font:
        return self.get_font('title_large', 48, bold=True)

    @property
    def title_xlarge(self) -> pygame.font.Font:
        return self.get_font('title_xlarge', 72, bold=True)

    @property
    def score(self) -> pygame.font.Font:
        return self.get_font('score', 20, bold=True)

    def render_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int]
    ) -> pygame.Surface:
        """渲染文本"""
        return font.render(text, True, color)