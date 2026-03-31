"""统一渲染器"""

import math
import random
import pygame
from typing import Optional, List, Tuple

from ..config import (
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT,
    BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT,
    PANEL_WIDTH, PANEL_X, SCREEN_WIDTH, SCREEN_HEIGHT,
    NEON_COLORS, GameConfig
)
from ..core import Board, Tetromino, GameEngine, GameState
from ..effects import Particle, FloatingText, Star
from .surface_cache import SurfaceCache
from .block_renderer import BlockRenderer
from .fonts import FontManager


class Renderer:
    """统一渲染器"""

    def __init__(self, screen: pygame.Surface, config: Optional[GameConfig] = None):
        self.screen = screen
        self.config = config or GameConfig()
        self.cache = SurfaceCache.get_instance()
        self.block_renderer = BlockRenderer(self.cache)
        self.fonts = FontManager.get_instance()
        self.time = 0

        # 预创建Surface
        self._init_surfaces()

    def _init_surfaces(self) -> None:
        """预创建常用Surface"""
        # 背景缓存（与窗口大小一致）
        self.bg_surface = pygame.Surface((self.config.screen_width, self.config.screen_height))
        self.bg_surface.fill((10, 10, 20))

        # 面板背景缓存（面板宽度固定为180）
        grid_height = self.config.grid_height * self.config.grid_size
        self.panel_bg_surface = pygame.Surface((self.config.panel_width, grid_height), pygame.SRCALPHA)
        for y in range(grid_height):
            pygame.draw.line(
                self.panel_bg_surface, (20, 20, 40, 50),
                (0, y), (self.config.panel_width, y)
            )

    def update(self, dt: float) -> None:
        """更新渲染状态"""
        self.time += dt
        self.block_renderer.update_time(dt)

    def update_config(self, config: GameConfig) -> None:
        """更新配置（窗口大小变化时）"""
        self.config = config
        self._init_surfaces()

    def set_block_flash(self, flash: float) -> None:
        """设置方块闪光"""
        self.block_renderer.set_block_flash(flash)

    # ==================== 背景渲染 ====================

    def draw_background(self, stars: Optional[List[Star]] = None) -> None:
        """绘制背景"""
        self.screen.blit(self.bg_surface, (0, 0))

        if stars:
            for star in stars:
                star.update(self.time)
                star.draw(self.screen)

    def draw_grid(self, board: Board, offset: Tuple[int, int] = (0, 0)) -> None:
        """绘制网格"""
        x = self.config.board_x + offset[0]
        y = self.config.board_y + offset[1]

        # 动态绘制网格线（使用实际 board 宽度）
        grid_width = board.width * self.config.grid_size
        grid_height = self.config.grid_height * self.config.grid_size

        for gx in range(board.width + 1):
            line_x = x + gx * self.config.grid_size
            pygame.draw.line(
                self.screen, (40, 40, 60, 100),
                (line_x, y),
                (line_x, y + grid_height)
            )
        for gy in range(self.config.grid_height + 1):
            line_y = y + gy * self.config.grid_size
            pygame.draw.line(
                self.screen, (40, 40, 60, 100),
                (x, line_y),
                (x + grid_width, line_y)
            )

    # ==================== 方块渲染 ====================

    def draw_board(self, board: Board, offset: Tuple[int, int] = (0, 0)) -> None:
        """绘制游戏板"""
        for y in range(2, self.config.grid_height + 2):
            for x in range(board.width):
                cell = board.get_cell(x, y)
                if cell is not None:
                    color = NEON_COLORS.get(cell, (255, 255, 255))
                    draw_x = self.config.board_x + x * self.config.grid_size + offset[0]
                    draw_y = self.config.board_y + (y - 2) * self.config.grid_size + offset[1]
                    self.block_renderer.draw_neon_block(self.screen, draw_x, draw_y, color)

    def draw_piece(
        self,
        piece: Tetromino,
        offset: Tuple[int, int] = (0, 0),
        draw_ghost: bool = True,
        ghost_positions: Optional[List[Tuple[int, int]]] = None,
        board: Optional['Board'] = None
    ) -> None:
        """绘制当前方块"""
        if not piece:
            return

        # 绘制幽灵方块
        if draw_ghost:
            # 使用传入的幽灵位置或计算
            if ghost_positions:
                ghost_blocks = ghost_positions
            else:
                # 计算幽灵位置（简单版本，不考虑碰撞）
                ghost_y = piece.y
                if board:
                    # 使用Board进行碰撞检测
                    while True:
                        valid = True
                        for x, y in piece.get_blocks():
                            ny = y + (ghost_y - piece.y + 1)
                            if ny >= self.config.grid_height + 2:
                                valid = False
                                break
                            if ny >= 0 and board.get_cell(x, ny) is not None:
                                valid = False
                                break
                        if not valid:
                            break
                        ghost_y += 1
                else:
                    ghost_y = piece.y + 10  # 默认下落10格

                shape = piece.shapes[piece.rotation % len(piece.shapes)]
                ghost_blocks = [(piece.x + dx, ghost_y + dy) for dx, dy in shape]

            for gx, gy in ghost_blocks:
                if gy >= 2:
                    draw_x = self.config.board_x + gx * self.config.grid_size + offset[0]
                    draw_y = self.config.board_y + (gy - 2) * self.config.grid_size + offset[1]
                    self.block_renderer.draw_ghost_block(self.screen, draw_x, draw_y, piece.color)

        # 绘制当前方块
        for x, y in piece.get_blocks():
            if y >= 0:
                draw_x = self.config.board_x + x * self.config.grid_size + offset[0]
                draw_y = self.config.board_y + (y - 2) * self.config.grid_size + offset[1]
                self.block_renderer.draw_neon_block(self.screen, draw_x, draw_y, piece.color)

    def draw_next_piece(self, piece: Tetromino, offset: Tuple[int, int] = (0, 0)) -> None:
        """绘制预览方块"""
        if not piece:
            return

        min_x, max_x, min_y, max_y = piece.get_bounds()
        width = (max_x - min_x + 1) * 22
        height = (max_y - min_y + 1) * 22

        preview_x = self.config.panel_x + (self.config.panel_width - width) // 2 - min_x * 22
        preview_y = self.config.board_y + 130 + (88 - height) // 2 - min_y * 22

        shape = piece.shapes[0]
        for dx, dy in shape:
            x = preview_x + dx * 22
            y = preview_y + dy * 22
            self.block_renderer.draw_neon_block(self.screen, x, y, piece.color, 20)

    # ==================== 面板渲染 ====================

    def draw_panel(
        self,
        high_score: int,
        score: int,
        lines: int,
        level: int,
        level_up_effect: int = 0
    ) -> None:
        """绘制右侧面板"""
        self.screen.blit(self.panel_bg_surface, (self.config.panel_x, self.config.board_y))

        # 标题
        title_text = "TETRIS"
        title_x = self.config.panel_x + (self.config.panel_width - self.fonts.title_medium.size(title_text)[0]) // 2
        self.draw_rainbow_title(title_text, self.fonts.title_medium, title_x, self.config.board_y + 40)

        # 标签
        labels = [
            ("下一个", self.config.board_y + 120),
            ("最高分", self.config.board_y + 240),
            ("得分", self.config.board_y + 330),
            ("消行", self.config.board_y + 400),
            ("关卡", self.config.board_y + 470),
        ]

        for label, y in labels:
            self.draw_neon_text(label, self.fonts.tiny, self.config.panel_x + 20, y, (150, 150, 180))

        # 数值
        best_text = self.fonts.medium.render(str(high_score), True, (255, 200, 0))
        self.screen.blit(best_text, (self.config.panel_x + 20, self.config.board_y + 260))

        score_text = self.fonts.small.render(str(score), True, (255, 255, 255))
        self.screen.blit(score_text, (self.config.panel_x + 20, self.config.board_y + 350))

        lines_text = self.fonts.small.render(str(lines), True, (255, 255, 255))
        self.screen.blit(lines_text, (self.config.panel_x + 20, self.config.board_y + 420))

        level_text = self.fonts.small.render(str(level), True, (255, 255, 255))
        if level_up_effect > 0:
            scale = 1.0 + 0.3 * math.sin(self.time * 20)
            scaled = pygame.transform.scale(
                level_text,
                (int(level_text.get_width() * scale), int(level_text.get_height() * scale))
            )
            self.screen.blit(scaled, (self.config.panel_x + 20, self.config.board_y + 490))
        else:
            self.screen.blit(level_text, (self.config.panel_x + 20, self.config.board_y + 490))

        # 帮助提示
        help_text = self.fonts.tiny.render("H - 帮助", True, (100, 100, 120))
        self.screen.blit(help_text, (self.config.panel_x + 20, self.config.board_y + self.config.board_height - 30))

    def draw_divider(self) -> None:
        """绘制分隔线"""
        divider_x = self.config.board_x + self.config.board_width

        hue = (self.time * 50) % 360
        r = int(128 + 127 * math.sin(math.radians(hue)))
        g = int(128 + 127 * math.sin(math.radians(hue + 120)))
        b = int(128 + 127 * math.sin(math.radians(hue + 240)))

        pygame.draw.line(
            self.screen, (r, g, b),
            (divider_x, self.config.board_y),
            (divider_x, self.config.board_y + self.config.board_height), 1
        )

    # ==================== 特效渲染 ====================

    def draw_particles(self, particles: List[Particle]) -> None:
        """绘制粒子"""
        for particle in particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.life <= 0:
                particles.remove(particle)

    def draw_floating_texts(
        self,
        texts: List[FloatingText],
        dt: float = 0.016
    ) -> None:
        """绘制浮动文字"""
        for text in texts[:]:
            text.update(dt)
            text.draw(self.screen, self.fonts.medium, self.fonts.font_name)
            if text.alpha <= 0:
                texts.remove(text)

    def draw_trails(self, trails: List[Tuple[float, float, Tuple[int, int, int], float]]) -> None:
        """绘制拖影"""
        new_trails = []
        total_trails = len(trails)
        for idx, (x, y, color, life) in enumerate(trails):
            if life > 0:
                if total_trails > 1:
                    gradient_factor = 0.1 + 0.7 * (idx / (total_trails - 1))
                else:
                    gradient_factor = 0.5
                alpha = int(255 * gradient_factor * life)

                trail_surf = pygame.Surface((self.config.grid_size, self.config.grid_size), pygame.SRCALPHA)
                pygame.draw.rect(
                    trail_surf, (*color, alpha),
                    (0, 0, self.config.grid_size, self.config.grid_size),
                    border_radius=3
                )
                self.screen.blit(trail_surf, (int(x - self.config.grid_size // 2), int(y - self.config.grid_size // 2)))
                new_trails.append((x, y, color, life - 0.05))
        return new_trails

    # ==================== 文字渲染 ====================

    def draw_neon_text(
        self,
        text: str,
        font: pygame.font.Font,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        glow_size: int = 2,
        pulse: bool = False
    ) -> None:
        """绘制霓虹文字"""
        pulse_val = 0.7 + 0.3 * math.sin(self.time * 3) if pulse else 1.0

        for radius, base_a in [(4, 25), (2, 50)]:
            gs = font.render(text, True, color)
            gs.set_alpha(int(base_a * pulse_val))
            for dx in range(-radius, radius + 1, max(1, radius // 2)):
                for dy in range(-radius, radius + 1, max(1, radius // 2)):
                    if dx != 0 or dy != 0:
                        self.screen.blit(gs, (x + dx, y + dy))

        ec = tuple(min(255, c + 100) for c in color)
        es = font.render(text, True, ec)
        es.set_alpha(int(180 * pulse_val))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.screen.blit(es, (x + dx, y + dy))

        s = font.render(text, True, color)
        self.screen.blit(s, (x, y))

    def draw_rainbow_title(self, text: str, font: pygame.font.Font, x: int, y: int) -> None:
        """绘制彩虹标题"""
        t = self.time

        def rainbow_color(offset=0):
            return (
                int(127 + 127 * math.sin(t * 0.8 + offset)),
                int(127 + 127 * math.sin(t * 0.8 + offset + 2.094)),
                int(127 + 127 * math.sin(t * 0.8 + offset + 4.189)),
            )

        color = rainbow_color()

        for radius, base_a in [(4, 25), (2, 50)]:
            gs = font.render(text, True, color)
            gs.set_alpha(base_a)
            for dx in range(-radius, radius + 1, max(1, radius // 2)):
                for dy in range(-radius, radius + 1, max(1, radius // 2)):
                    if dx != 0 or dy != 0:
                        self.screen.blit(gs, (x + dx, y + dy))

        ec = tuple(min(255, c + 100) for c in color)
        es = font.render(text, True, ec)
        es.set_alpha(180)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.screen.blit(es, (x + dx, y + dy))

        s = font.render(text, True, color)
        self.screen.blit(s, (x, y))

    # ==================== 屏幕渲染 ====================

    def draw_start_screen(self) -> None:
        """绘制开始屏幕"""
        self.draw_background()

        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title_text = "TETRIS"
        title_x = (self.config.screen_width - self.fonts.title_xlarge.size(title_text)[0]) // 2
        self.draw_rainbow_title(title_text, self.fonts.title_xlarge, title_x, 120)

        instructions = [
            "← → : 移动",
            "↑ : 旋转",
            "↓ : 加速下落",
            "空格 : 硬降",
            "P : 暂停",
            "R : 重新开始",
            "H : 帮助",
        ]

        y = 280
        for line in instructions:
            text = self.fonts.small.render(line, True, (200, 200, 220))
            self.screen.blit(text, ((self.config.screen_width - text.get_width()) // 2, y))
            y += 35

        # 开始提示
        text = self.fonts.tiny.render("按 空格 开始游戏", True, (150, 150, 180))
        self.screen.blit(text, ((self.config.screen_width - text.get_width()) // 2, self.config.screen_height - 50))

    def draw_pause_screen(self) -> None:
        """绘制暂停屏幕"""
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_x = (self.config.screen_width - self.fonts.title_large.size("暂停")[0]) // 2
        self.draw_rainbow_title("暂停", self.fonts.title_large, title_x, 150)

        resume_text = self.fonts.small.render("按 P 继续", True, (200, 200, 220))
        self.screen.blit(resume_text, ((self.config.screen_width - resume_text.get_width()) // 2, self.config.screen_height * 2 // 3 - 100))

    def draw_help_screen(self) -> None:
        """绘制帮助屏幕"""
        self.draw_background()

        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        self.draw_rainbow_title("帮助", self.fonts.title_medium, (self.config.screen_width - 70) // 2, 30)

        help_sections = [
            ("操作", [
                "← → : 左右移动",
                "↑ : 旋转方块",
                "↓ : 加速下落（长按）",
                "空格 : 硬降到底",
                "P : 暂停游戏",
                "R : 重新开始",
                "H : 打开/关闭帮助",
            ]),
            ("计分", [
                "倍率 = 2^(关卡-1)",
                "消行得分 = 行数² × 倍率",
                "1行: 1×  |  2行: 4×",
                "3行: 9×  |  4行: 16×",
                "连击加分 = 2^(连击-1) × 关卡²",
            ]),
            ("关卡", [
                "每消除10行升一关",
                "速度随关卡提升",
                "第12关达到最快速度",
            ]),
        ]

        title_font = self.fonts.get_font('help_title', 17, bold=True)
        content_font = self.fonts.get_font('help_content', 15)

        y = 100
        for section_title, lines in help_sections:
            title_surf = title_font.render(section_title, True, (255, 200, 0))
            self.screen.blit(title_surf, (50, y))
            y += 28

            for line in lines:
                text = content_font.render(line, True, (200, 200, 220))
                self.screen.blit(text, (50, y))
                y += 24
            y += 8

        close_text = content_font.render("按 H 关闭", True, (150, 150, 180))
        self.screen.blit(close_text, (50, y))

    def draw_gameover_screen(self, score: int, is_new_record: bool) -> None:
        """绘制游戏结束屏幕"""
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_text = "游戏结束"
        title_x = (self.config.screen_width - self.fonts.title_large.size(title_text)[0]) // 2
        self.draw_rainbow_title(title_text, self.fonts.title_large, title_x, 150)

        score_text = self.fonts.small.render(f"得分: {score}", True, (200, 200, 220))
        self.screen.blit(score_text, ((self.config.screen_width - score_text.get_width()) // 2, self.config.screen_height * 2 // 3 - 100))

        if is_new_record:
            best_text = self.fonts.small.render("新纪录!", True, (255, 200, 0))
            self.screen.blit(best_text, ((self.config.screen_width - best_text.get_width()) // 2, self.config.screen_height * 2 // 3 + 35))

        text = self.fonts.tiny.render("按 R 重新开始", True, (150, 150, 180))
        self.screen.blit(text, ((self.config.screen_width - text.get_width()) // 2, self.config.screen_height - 50))