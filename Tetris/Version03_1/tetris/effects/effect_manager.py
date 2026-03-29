"""特效管理器"""

import random
import math
from typing import List, Tuple, Optional

import pygame

from ..config import BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, NEON_COLORS, GameConfig
from .particle import Particle
from .floating_text import FloatingText


class EffectManager:
    """特效统一管理器"""

    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []

        # 特效状态
        self.clear_flash_lines: List[int] = []
        self.clear_flash_timer = 0
        self.flash_effects: List[List] = []  # [row, color, alpha, lines_count]
        self.scan_lines: List[List] = []  # [y_pos, color, alpha]

        # 震动
        self.shake_offset = [0, 0]
        self.combo_shake = 0

        # 升级特效
        self.level_up_effect = 0
        self.edge_pulse = 0
        self.block_flash = 0
        self.level_up_pause = False

        # TETRIS特效
        self.slow_motion_timer = 0
        self.slow_motion_factor = 1.0

    def trigger_line_clear(
        self,
        lines: List[int],
        board_x: int = None,
        board_y: int = None,
        grid: List[List[Optional[str]]] = None
    ) -> None:
        """触发消行特效"""
        if not lines:
            return

        board_x = board_x or self.config.board_x
        board_y = board_y or self.config.board_y

        self.clear_flash_lines = lines
        self.clear_flash_timer = 20

        lines_count = len(lines)
        neon_colors_list = list(NEON_COLORS.values())

        for y in lines:
            # 生成粒子
            for x in range(self.config.grid_width):
                if grid and y < len(grid) and x < len(grid[y]):
                    piece_type = grid[y][x]
                else:
                    piece_type = None
                color = NEON_COLORS.get(piece_type, (255, 255, 255))

                px = board_x + x * self.config.grid_size + self.config.grid_size // 2
                py = board_y + (y - 2) * self.config.grid_size + self.config.grid_size // 2
                num_particles = 4 + lines_count * 3

                for _ in range(num_particles):
                    self.particles.append(Particle(px, py, color, lines_count))

            # 添加闪光效果
            flash_color = random.choice(neon_colors_list)
            self.flash_effects.append([y - 2, flash_color, 255, lines_count])
            self.scan_lines.append([
                (y - 2) * self.config.grid_size,
                neon_colors_list[lines_count % len(neon_colors_list)],
                255
            ])

    def trigger_level_up(self, center_x: float = None, center_y: float = None) -> None:
        """触发升级特效"""
        center_x = center_x or self.config.board_x + self.config.board_width // 2
        center_y = center_y or self.config.board_y + self.config.board_height // 2

        self.level_up_effect = 45
        self.edge_pulse = 1.0
        self.block_flash = 1.0
        self.level_up_pause = True

        # 粒子爆发
        self.spawn_level_up_particles(int(center_x), int(center_y))

        # 浮动文字
        self.floating_texts.append(
            FloatingText(center_x, center_y - 50, "LEVEL UP!", (255, 215, 0), 32, True, 0)
        )

        # 震动
        self.shake_offset = [random.randint(-10, 10), random.randint(-10, 10)]

    def trigger_tetris(self, center_y: float = None) -> None:
        """触发TETRIS特效"""
        center_y = center_y or self.config.board_y + self.config.board_height // 2
        center_x = self.config.board_x + self.config.board_width // 2

        # 震动
        self.shake_offset = [random.randint(-12, 12), random.randint(-12, 12)]

        # 慢动作
        self.slow_motion_timer = 0.5
        self.slow_motion_factor = 0.3

        # 金色粒子
        for _ in range(40):
            self.particles.append(Particle(center_x, center_y, (255, 215, 0), 4))

    def trigger_combo(self, combo_count: int, center_y: float = None) -> None:
        """触发连击特效"""
        center_y = center_y or self.config.board_y + self.config.board_height // 2
        center_x = self.config.board_x + self.config.board_width // 2

        shake_intensity = min(5, combo_count)
        self.combo_shake = shake_intensity * 15

    def add_floating_text(
        self,
        x: float,
        y: float,
        text: str,
        color: Tuple[int, int, int],
        size: int = 24,
        is_tetris: bool = False,
        combo_count: int = 0
    ) -> None:
        """添加浮动文字"""
        self.floating_texts.append(FloatingText(x, y, text, color, size, is_tetris, combo_count))

    def spawn_level_up_particles(self, cx: int, cy: int) -> None:
        """生成升级粒子"""
        # 中心爆发
        for _ in range(30):
            self.particles.append(Particle(cx, cy, (255, 215, 0), 4))

        # 四角爆发
        corners = [
            (0, 0),
            (self.config.screen_width, 0),
            (0, self.config.screen_height),
            (self.config.screen_width, self.config.screen_height)
        ]
        for corner_x, corner_y in corners:
            for _ in range(10):
                self.particles.append(Particle(corner_x, corner_y, (255, 200, 50), 4))

    def update(self, dt: float) -> None:
        """更新特效状态"""
        # 慢动作计时
        if self.slow_motion_timer > 0:
            self.slow_motion_timer -= dt
        else:
            self.slow_motion_factor = 1.0

        # 更新闪光计时器
        if self.clear_flash_timer > 0:
            self.clear_flash_timer -= 1

        # 更新闪光效果
        for fe in self.flash_effects:
            fe[2] -= 10
        self.flash_effects = [fe for fe in self.flash_effects if fe[2] > 0]

        # 更新扫描线
        for sl in self.scan_lines:
            sl[2] -= 8
        self.scan_lines = [sl for sl in self.scan_lines if sl[2] > 0]

        # 更新升级效果
        if self.level_up_effect > 0:
            self.level_up_effect -= 1
        if self.edge_pulse > 0:
            self.edge_pulse -= 1.0 / 45
        if self.block_flash > 0:
            self.block_flash -= 1.0 / 45

        # 升级暂停结束
        if self.edge_pulse <= 0 and self.level_up_pause:
            self.level_up_pause = False

        # 更新震动
        if self.combo_shake > 0:
            self.combo_shake -= 1

        # TETRIS持续震动
        if self.slow_motion_timer > 0:
            shake_intensity = self.slow_motion_timer * 24
            self.shake_offset = [
                random.randint(-int(shake_intensity), int(shake_intensity)),
                random.randint(-int(shake_intensity), int(shake_intensity))
            ]
        elif self.level_up_effect > 0:
            intensity = self.level_up_effect / 45
            shake_magnitude = int(10 * intensity)
            self.shake_offset = [
                random.randint(-shake_magnitude, shake_magnitude),
                random.randint(-shake_magnitude, shake_magnitude)
            ]
        elif self.combo_shake > 0:
            intensity = self.combo_shake / 50
            shake_magnitude = int(3 * intensity)
            self.shake_offset = [
                random.randint(-shake_magnitude, shake_magnitude),
                random.randint(-shake_magnitude, shake_magnitude)
            ]
        else:
            self.shake_offset = [0, 0]

    def update_particles(self) -> None:
        """更新粒子"""
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def update_floating_texts(self, dt: float = 0.016) -> None:
        """更新浮动文字"""
        for text in self.floating_texts[:]:
            text.update(dt)
            if text.alpha <= 0:
                self.floating_texts.remove(text)

    def draw_particles(self, surface: pygame.Surface) -> None:
        """绘制粒子"""
        for particle in self.particles:
            particle.draw(surface)

    def draw_floating_texts(self, surface: pygame.Surface, font: pygame.font.Font, font_name: str = None) -> None:
        """绘制浮动文字"""
        for text in self.floating_texts:
            text.draw(surface, font, font_name)

    def draw_effects(self, surface: pygame.Surface, shake_offset: Tuple[int, int] = None) -> None:
        """绘制特效"""
        shake = shake_offset or tuple(self.shake_offset)
        board_x = self.config.board_x + shake[0]
        board_y = self.config.board_y + shake[1]

        # 清行闪光
        if self.clear_flash_timer > 0:
            for y in self.clear_flash_lines:
                flash_alpha = int(255 * (self.clear_flash_timer / 20))
                flash_surf = pygame.Surface((self.config.board_width, self.config.grid_size), pygame.SRCALPHA)
                pygame.draw.rect(
                    flash_surf, (255, 255, 255, flash_alpha),
                    (0, 0, self.config.board_width, self.config.grid_size)
                )
                surface.blit(flash_surf, (board_x, board_y + (y - 2) * self.config.grid_size))

        # 闪光效果
        for fe in self.flash_effects:
            row, color, alpha, n = fe
            fs = pygame.Surface((self.config.board_width, self.config.grid_size), pygame.SRCALPHA)
            fs.fill((*color, min(200, alpha)))
            surface.blit(fs, (board_x, board_y + row * self.config.grid_size))

        # 扫描线
        for sl in self.scan_lines:
            y_pos, color, alpha = sl
            ss = pygame.Surface((self.config.board_width, 3), pygame.SRCALPHA)
            ss.fill((*color, min(255, alpha * 2)))
            surface.blit(ss, (board_x, board_y + y_pos))

    def draw_level_up_effects(self, surface: pygame.Surface) -> None:
        """绘制升级特效"""
        if self.edge_pulse > 0:
            self.draw_edge_glow(surface)

    def draw_edge_glow(self, surface: pygame.Surface) -> None:
        """绘制边缘光晕"""
        edge_alpha = int(200 * self.edge_pulse)

        def gold_color(progress):
            if progress < 0.5:
                return (255, 215, 0)
            else:
                return (255, 230, 150)

        edge_height = 40

        # 上边缘
        edge_surf = pygame.Surface((self.config.screen_width, edge_height), pygame.SRCALPHA)
        for y in range(edge_height):
            alpha = int(edge_alpha * (1 - y / edge_height) ** 1.5)
            color = gold_color(y / edge_height)
            pygame.draw.line(edge_surf, (*color, alpha), (0, y), (self.config.screen_width, y))
        surface.blit(edge_surf, (0, 0))

        # 下边缘
        edge_surf = pygame.Surface((self.config.screen_width, edge_height), pygame.SRCALPHA)
        for y in range(edge_height):
            alpha = int(edge_alpha * (y / edge_height) ** 1.5)
            color = gold_color(y / edge_height)
            pygame.draw.line(edge_surf, (*color, alpha), (0, y), (self.config.screen_width, y))
        surface.blit(edge_surf, (0, self.config.screen_height - edge_height))

        edge_width = 40

        # 左边缘
        edge_surf = pygame.Surface((edge_width, self.config.screen_height), pygame.SRCALPHA)
        for x in range(edge_width):
            alpha = int(edge_alpha * (1 - x / edge_width) ** 1.5)
            color = gold_color(x / edge_width)
            pygame.draw.line(edge_surf, (*color, alpha), (x, 0), (x, self.config.screen_height))
        surface.blit(edge_surf, (0, 0))

        # 右边缘
        edge_surf = pygame.Surface((edge_width, self.config.screen_height), pygame.SRCALPHA)
        for x in range(edge_width):
            alpha = int(edge_alpha * (x / edge_width) ** 1.5)
            color = gold_color(x / edge_width)
            pygame.draw.line(edge_surf, (*color, alpha), (x, 0), (x, self.config.screen_height))
        surface.blit(edge_surf, (self.config.screen_width - edge_width, 0))

    def clear(self) -> None:
        """清除所有特效"""
        self.particles.clear()
        self.floating_texts.clear()
        self.clear_flash_lines.clear()
        self.clear_flash_timer = 0
        self.flash_effects.clear()
        self.scan_lines.clear()
        self.shake_offset = [0, 0]
        self.combo_shake = 0
        self.level_up_effect = 0
        self.edge_pulse = 0
        self.block_flash = 0
        self.level_up_pause = False
        self.slow_motion_timer = 0
        self.slow_motion_factor = 1.0

    def get_state(self) -> dict:
        """获取状态（用于网络同步）"""
        return {
            'shake_offset': self.shake_offset,
            'level_up_effect': self.level_up_effect,
            'slow_motion_timer': self.slow_motion_timer,
        }

    def restore_state(self, state: dict) -> None:
        """恢复状态"""
        self.shake_offset = state.get('shake_offset', [0, 0])
        self.level_up_effect = state.get('level_up_effect', 0)
        self.slow_motion_timer = state.get('slow_motion_timer', 0)