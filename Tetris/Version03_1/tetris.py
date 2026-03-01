import pygame
import random
import math
import json
import os
from typing import List, Tuple, Optional

pygame.init()

GRID_SIZE = 32
GRID_WIDTH = 10
GRID_HEIGHT = 20
BOARD_WIDTH = GRID_WIDTH * GRID_SIZE
BOARD_HEIGHT = GRID_HEIGHT * GRID_SIZE
BOARD_X = 0
BOARD_Y = 0
PANEL_WIDTH = 180
PANEL_X = BOARD_X + BOARD_WIDTH
SCREEN_WIDTH = BOARD_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT

NEON_COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (255, 0, 255),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 128, 255),
    'L': (255, 128, 0),
}

SPARK_COLORS = [
    (255, 100, 50),
    (255, 150, 50),
    (255, 200, 100),
    (255, 255, 150),
    (255, 200, 200),
    (255, 100, 100),
    (100, 255, 255),
    (255, 100, 255),
]

SHAPES = {
    'I': [[(0, 0), (1, 0), (2, 0), (3, 0)],
          [(1, 0), (1, 1), (1, 2), (1, 3)]],
    'O': [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (1, 2)],
          [(1, 0), (0, 1), (1, 1), (1, 2)]],
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)],
          [(1, 0), (1, 1), (2, 1), (2, 2)]],
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
          [(2, 0), (1, 1), (2, 1), (1, 2)]],
    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (2, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (0, 2), (1, 2)]],
    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]],
}

class Particle:
    # 类级别的 Surface 缓存
    _glow_cache = {}  # 缓存光晕 Surface

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
    
    def update(self):
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
    
    def draw(self, surface: pygame.Surface):
        if self.life <= 0:
            return
        trail_len = len(self.trail)
        alpha_multiplier = 1.5 + self.alpha_bonus

        # 简化拖尾绘制 - 只在必要时创建 Surface
        if trail_len > 0:
            for i, (tx, ty, tc, tl) in enumerate(self.trail):
                progress = (i + 1) / trail_len
                trail_alpha = min(255, int(100 * alpha_multiplier * tl * progress * 0.6))
                trail_size = max(1, int(self.size * progress * 0.7))
                # 使用缓存的 key
                cache_key = (trail_size, tc, trail_alpha)
                if cache_key not in Particle._glow_cache:
                    trail_surf = pygame.Surface((trail_size * 2 + 4, trail_size * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (*tc, trail_alpha), (trail_size + 2, trail_size + 2), trail_size)
                    Particle._glow_cache[cache_key] = trail_surf
                    # 限制缓存大小
                    if len(Particle._glow_cache) > 200:
                        # 清除一半缓存
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
            # 简化光晕层数
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

class FloatingText:
    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int], size: int = 24, is_tetris: bool = False, combo_count: int = 0):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.base_size = int(size * 1.3)
        self.life = 1.0
        self.vy = -1.0  # 减慢上升速度
        self.scale = 0.5  # 初始缩放较小
        self.alpha = 0  # 初始透明度为0（淡入）
        self.is_tetris = is_tetris
        self.combo_count = combo_count
        self.shake_offset = 0
        self.neon_pulse = 0
        self.shake_phase = 0
        self.shake_speed = 8
        self.rainbow_phase = 0  # TETRIS 彩虹效果
        # 动画阶段：'fade_in' -> 'hold' -> 'fade_out'
        self.phase = 'fade_in'
        self.phase_timer = 0
        self.fade_in_duration = 0.25  # 淡入时间
        self.hold_duration = 0.8  # 停留时间
        self.fade_out_duration = 0.5  # 淡出时间

    def update(self, dt: float = 0.016):
        # 更新脉冲效果
        self.neon_pulse += 8 * dt
        self.shake_phase += self.shake_speed * dt * 6
        self.rainbow_phase += 6 * dt

        # 更新震动
        if self.shake_offset > 0:
            self.shake_offset *= 0.95

        # 平滑上升
        self.y += self.vy * dt * 60

        # 阶段动画
        self.phase_timer += dt

        if self.phase == 'fade_in':
            # 淡入阶段：缩放 0.5 -> 1.0，透明度 0 -> 255
            progress = min(1, self.phase_timer / self.fade_in_duration)
            # 使用 easeOutQuad 缓动
            ease_progress = 1 - (1 - progress) ** 2
            self.scale = 0.7 + 0.3 * ease_progress  # 从0.7平滑到1.0
            self.alpha = int(255 * ease_progress)

            if progress >= 1:
                self.phase = 'hold'
                self.phase_timer = 0
                self.scale = 1.0
                self.alpha = 255
                if self.is_tetris or self.combo_count > 0:
                    self.shake_offset = 2

        elif self.phase == 'hold':
            # 停留阶段：保持
            self.scale = 1.0
            self.alpha = 255

            if self.phase_timer >= self.hold_duration:
                self.phase = 'fade_out'
                self.phase_timer = 0

        elif self.phase == 'fade_out':
            # 淡出阶段：保持大小，透明度 255 -> 0
            progress = min(1, self.phase_timer / self.fade_out_duration)
            # 使用 easeInQuad 缓动
            ease_progress = progress ** 2
            self.scale = 1.0  # 保持原大小，不再放大
            self.alpha = int(255 * (1 - ease_progress))
            self.life = 1 - progress

    def get_rainbow_color(self, offset: float = 0) -> Tuple[int, int, int]:
        """获取彩虹颜色 - TETRIS 专用"""
        phase = self.rainbow_phase + offset
        return (
            int(127 + 127 * math.sin(phase)),
            int(127 + 127 * math.sin(phase + 2.094)),
            int(127 + 127 * math.sin(phase + 4.189)),
        )

    def get_gold_color(self, pulse: float) -> Tuple[int, int, int]:
        """获取金色脉冲颜色 - TETRIS 专用"""
        base_gold = (255, 215, 0)
        pulse_intensity = 0.5 + 0.5 * math.sin(pulse)
        return (
            255,
            int(215 + 40 * pulse_intensity),
            int(50 + 50 * pulse_intensity),
        )

    def draw_tetris_text(self, surface: pygame.Surface, font: pygame.font.Font, text: str, x: int, y: int, alpha: int):
        """绘制 TETRIS 专用炫酷文字 - 彩虹光晕 + 金色核心"""
        pulse = 0.7 + 0.3 * math.sin(self.neon_pulse)

        text_surf = font.render(text, True, (255, 255, 255))
        text_width = text_surf.get_width()
        text_height = text_surf.get_height()

        # 创建大尺寸光晕 Surface
        glow_size = 8
        total_width = text_width + glow_size * 4
        total_height = text_height + glow_size * 4
        glow_surf = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

        # 绘制多层彩虹光晕
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

        # 绘制金色中层光晕
        gold_color = self.get_gold_color(self.neon_pulse * 2)
        for dx in range(-2, 3, 1):
            for dy in range(-2, 3, 1):
                if dx != 0 or dy != 0:
                    temp_surf = font.render(text, True, gold_color)
                    temp_surf.set_alpha(int(150 * pulse))
                    glow_surf.blit(temp_surf, (glow_size * 2 + dx, glow_size * 2 + dy))

        glow_surf.set_alpha(alpha)
        surface.blit(glow_surf, (x - glow_size * 2, y - glow_size * 2))

        # 绘制白色核心文字
        core_surf = font.render(text, True, (255, 255, 255))
        core_surf.set_alpha(alpha)
        surface.blit(core_surf, (x, y))

        # 绘制金色高光
        highlight_surf = font.render(text, True, gold_color)
        highlight_surf.set_alpha(int(alpha * 0.6 * pulse))
        surface.blit(highlight_surf, (x + 1, y + 1))

        # 绘制闪烁星星效果
        for i in range(5):
            star_phase = self.rainbow_phase * 3 + i * 1.2
            star_alpha = int(alpha * 0.8 * (0.5 + 0.5 * math.sin(star_phase)))
            if star_alpha > 30:
                star_x = x + random.randint(0, text_width)
                star_y = y + random.randint(0, text_height // 2)
                star_size = random.randint(2, 4)
                star_surf = pygame.Surface((star_size * 4, star_size * 4), pygame.SRCALPHA)
                pygame.draw.circle(star_surf, (*self.get_rainbow_color(i), star_alpha),
                                 (star_size * 2, star_size * 2), star_size)
                surface.blit(star_surf, (star_x - star_size * 2, star_y - star_size * 2))
    
    def draw_neon_text(self, surface: pygame.Surface, font: pygame.font.Font, text: str, x: int, y: int, color: Tuple[int, int, int], alpha: int):
        pulse = 0.7 + 0.3 * math.sin(self.neon_pulse)
        
        text_surf = font.render(text, True, color)
        
        glow_size = 2
        glow_surf = pygame.Surface((text_surf.get_width() + glow_size * 4, text_surf.get_height() + glow_size * 4), pygame.SRCALPHA)
        
        for i in range(glow_size * 2, 0, -1):
            g_alpha = int(40 * pulse * (1 - i / (glow_size * 2)))
            glow_color = (*color, g_alpha)
            for dx in range(-i, i + 1):
                for dy in range(-i, i + 1):
                    if dx * dx + dy * dy <= i * i:
                        temp_surf = font.render(text, True, glow_color[:3])
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
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, font_name: str = None):
        if self.alpha <= 0:
            return

        shake_x = int(math.sin(self.shake_phase) * self.shake_offset) if self.shake_offset > 0.5 else 0
        shake_y = int(math.cos(self.shake_phase * 1.3) * self.shake_offset) if self.shake_offset > 0.5 else 0

        new_size = max(8, int(self.base_size * self.scale))
        # TETRIS 文字放大 1.5 倍
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

        # TETRIS 使用专用炫酷文字效果
        if self.is_tetris:
            self.draw_tetris_text(surface, scaled_font, self.text, draw_x, draw_y, self.alpha)
        else:
            self.draw_neon_text(surface, scaled_font, self.text,
                              draw_x, draw_y,
                              self.color, self.alpha)

class Star:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.brightness = random.uniform(0.3, 1.0)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.5, 2.0)
        self.life_phase = random.uniform(0, math.pi * 2)
        self.fading_out = False
        self.fade_speed = random.uniform(0.002, 0.005)
    
    def update(self, time: float):
        self.life_phase += self.fade_speed
        fade_factor = 0.5 + 0.5 * math.sin(self.life_phase)
        
        if fade_factor < 0.2:
            self.fading_out = True
        elif fade_factor > 0.8 and self.fading_out:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.fading_out = False
            self.life_phase = random.uniform(0, math.pi * 2)
        
        self.brightness = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(time * self.speed + self.phase)) * fade_factor
    
    def draw(self, surface: pygame.Surface):
        alpha = int(255 * self.brightness)
        color = (alpha, alpha, alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

class Tetromino:
    def __init__(self, shape_type: str):
        self.type = shape_type
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 1
        self.y = 0
        self.color = NEON_COLORS[shape_type]
        self.shapes = SHAPES[shape_type]
    
    def get_blocks(self) -> List[Tuple[int, int]]:
        shape = self.shapes[self.rotation % len(self.shapes)]
        return [(self.x + dx, self.y + dy) for dx, dy in shape]
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        shape = self.shapes[0]
        min_x = min(dx for dx, dy in shape)
        max_x = max(dx for dx, dy in shape)
        min_y = min(dy for dx, dy in shape)
        max_y = max(dy for dx, dy in shape)
        return min_x, max_x, min_y, max_y
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shapes)
    
    def rotate_back(self):
        self.rotation = (self.rotation - 1) % len(self.shapes)

class Game:
    def __init__(self):
        # 尝试使用硬件加速
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
            self.hw_accelerated = True
        except:
            # 如果硬件加速不支持，回退到普通模式
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.hw_accelerated = False
        pygame.display.set_caption("Tetris - Neon Edition")
        self.clock = pygame.time.Clock()

        # 预创建并转换常用的 Surface 为硬件加速格式
        self._init_surfaces()
        self.clock = pygame.time.Clock()
        
        try:
            font_names = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei']
            self.font_name = None
            for name in font_names:
                try:
                    test_font = pygame.font.SysFont(name, 24)
                    if test_font:
                        self.font_name = name
                        break
                except:
                    continue
            if self.font_name:
                self.font_large = pygame.font.SysFont(self.font_name, 48)
                self.font_medium = pygame.font.SysFont(self.font_name, 32)
                self.font_small = pygame.font.SysFont(self.font_name, 16)
                self.font_tiny = pygame.font.SysFont(self.font_name, 14)
                # 加粗字体用于标题
                self.font_title_large = pygame.font.SysFont(self.font_name, 48, bold=True)
                self.font_title_medium = pygame.font.SysFont(self.font_name, 32, bold=True)
            else:
                self.font_large = pygame.font.Font(None, 48)
                self.font_medium = pygame.font.Font(None, 32)
                self.font_small = pygame.font.Font(None, 20)
                self.font_tiny = pygame.font.Font(None, 16)
                # 加粗字体用于标题
                self.font_title_large = pygame.font.Font(None, 48, bold=True)
                self.font_title_medium = pygame.font.Font(None, 32, bold=True)
        except:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 20)
            self.font_tiny = pygame.font.Font(None, 16)
        
        self.high_score = self.load_high_score()
        self.reset_game()
        
        self.stars: List[Star] = []
        for _ in range(80):
            self.stars.append(Star(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))
        
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []
        
        self.trail_positions: List[Tuple[float, float, Tuple[int, int, int], float]] = []
        
        self.level_up_effect = 0
        self.rainbow_effect = 0
        self.shake_offset = [0, 0]
        self.clear_flash_lines: List[int] = []
        self.clear_flash_timer = 0
        self.tetris_flash_effect = 0
        self.combo_shake = 0
        self.flash_effects: List[List] = []
        self.scan_lines: List[List] = []

        # 升级特效
        self.shockwaves: List[dict] = []  # 冲击波
        self.edge_pulse = 0  # 边缘脉冲
        self.block_flash = 0  # 方块闪光
        self.level_up_pause = False  # 升级暂停标志

        # TETRIS 特效
        self.tetris_effects: List[TetrisEffect] = []
        self.slow_motion_timer = 0  # 慢动作计时器
        self.slow_motion_factor = 1.0  # 慢动作系数

        self.state = "start"
        self.previous_state = "start"
        self.time = 0
        
        self.key_repeat_timers = {
            pygame.K_LEFT: 0,
            pygame.K_RIGHT: 0,
            pygame.K_DOWN: 0,
        }
        self.key_repeat_delay = 170
        self.key_repeat_interval = 50

    def _init_surfaces(self):
        """预创建常用的 Surface 缓存"""
        # 背景缓存 - 使用 convert 加速 blit
        self.bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_surface.fill((10, 10, 20))

        # 网格缓存
        self.grid_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.grid_surface, (40, 40, 60, 100), (x * GRID_SIZE, 0), (x * GRID_SIZE, BOARD_HEIGHT))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.grid_surface, (40, 40, 60, 100), (0, y * GRID_SIZE), (BOARD_WIDTH, y * GRID_SIZE))

        # 面板背景缓存
        self.panel_bg_surface = pygame.Surface((PANEL_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        for y in range(BOARD_HEIGHT):
            pygame.draw.line(self.panel_bg_surface, (20, 20, 40, 50), (0, y), (PANEL_WIDTH, y))
    
    def load_high_score(self) -> int:
        try:
            with open("highscore.json", "r") as f:
                return json.load(f).get("high_score", 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open("highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass
    
    def reset_game(self):
        self.grid: List[List[Optional[str]]] = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT + 2)]
        self.current_piece: Optional[Tetromino] = None
        self.next_piece = self.new_piece()
        self.spawn_piece()
        
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        
        self.fall_timer = 0
        self.fall_speed = 1.0
        
        self.particles = []
        self.floating_texts = []
        self.trail_positions = []
        self.clear_flash_lines = []
        self.clear_flash_timer = 0
        self.level_up_effect = 0
        self.rainbow_effect = 0
        self.shake_offset = [0, 0]
        self.tetris_flash_effect = 0
        self.combo_shake = 0
        self.flash_effects = []
        self.scan_lines = []
        self.shockwaves = []
        self.edge_pulse = 0
        self.block_flash = 0
        self.tetris_effects = []
        self.slow_motion_timer = 0
        self.slow_motion_factor = 1.0
        self.level_up_pause = False

    def new_piece(self) -> Tetromino:
        return Tetromino(random.choice(list(SHAPES.keys())))
    
    def spawn_piece(self) -> bool:
        self.current_piece = self.next_piece
        self.current_piece.x = GRID_WIDTH // 2 - 1
        self.current_piece.y = 0
        self.next_piece = self.new_piece()
        
        for x, y in self.current_piece.get_blocks():
            if y >= 0 and self.grid[y + 2][x] is not None:
                return False
        return True
    
    def is_valid_position(self, piece: Tetromino, dx: int = 0, dy: int = 0) -> bool:
        for x, y in piece.get_blocks():
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= GRID_WIDTH:
                return False
            if ny >= GRID_HEIGHT + 2:
                return False
            if ny >= 0 and self.grid[ny][nx] is not None:
                return False
        return True
    
    def move_piece(self, dx: int, dy: int, add_trail: bool = False) -> bool:
        if self.current_piece and self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            if dy > 0 and add_trail:
                # 对于同一列的方块，只保留最下面的那个的拖影，避免垂直重叠
                columns = {}
                for x, y in self.current_piece.get_blocks():
                    if x not in columns or y > columns[x]:
                        columns[x] = y
                for x, y in columns.items():
                    self.trail_positions.append((BOARD_X + x * GRID_SIZE + GRID_SIZE // 2,
                                                  BOARD_Y + (y - 2) * GRID_SIZE + GRID_SIZE // 2,
                                                  self.current_piece.color, 1.0))
            return True
        return False
    
    def rotate_piece(self):
        if not self.current_piece:
            return
        self.current_piece.rotate()
        if not self.is_valid_position(self.current_piece):
            for dx in [-1, 1, -2, 2]:
                if self.is_valid_position(self.current_piece, dx, 0):
                    self.current_piece.x += dx
                    return
            self.current_piece.rotate_back()
    
    def hard_drop(self):
        if not self.current_piece:
            return
        drop_distance = 0
        while self.move_piece(0, 1, add_trail=True):  # 硬降产生拖影
            drop_distance += 1
        self.lock_piece()
    
    def get_ghost_position(self) -> List[Tuple[int, int]]:
        if not self.current_piece:
            return []
        ghost_y = self.current_piece.y
        while self.is_valid_position(self.current_piece, 0, ghost_y - self.current_piece.y + 1):
            ghost_y += 1
        shape = self.current_piece.shapes[self.current_piece.rotation % len(self.current_piece.shapes)]
        return [(self.current_piece.x + dx, ghost_y + dy) for dx, dy in shape]
    
    def lock_piece(self):
        if not self.current_piece:
            return
        for x, y in self.current_piece.get_blocks():
            if 0 <= y < GRID_HEIGHT + 2 and 0 <= x < GRID_WIDTH:
                self.grid[y][x] = self.current_piece.type
        
        cleared = self.clear_lines()
        if cleared > 0:
            self.calculate_score(cleared)
        else:
            self.combo = 0
        
        if not self.spawn_piece():
            self.state = "gameover"
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
    
    def clear_lines(self) -> int:
        lines_to_clear = []
        for y in range(GRID_HEIGHT + 2):
            if all(self.grid[y][x] is not None for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            self.clear_flash_lines = lines_to_clear
            self.clear_flash_timer = 20
            
            lines_count = len(lines_to_clear)
            neon_colors_list = list(NEON_COLORS.values())
            for y in lines_to_clear:
                for x in range(GRID_WIDTH):
                    color = NEON_COLORS.get(self.grid[y][x], (255, 255, 255))
                    px = BOARD_X + x * GRID_SIZE + GRID_SIZE // 2
                    py = BOARD_Y + (y - 2) * GRID_SIZE + GRID_SIZE // 2
                    num_particles = 4 + lines_count * 3
                    for _ in range(num_particles):
                        self.particles.append(Particle(px, py, color, lines_count))
                
                flash_color = random.choice(neon_colors_list)
                self.flash_effects.append([y - 2, flash_color, 255, lines_count])
                self.scan_lines.append([(y - 2) * GRID_SIZE, neon_colors_list[lines_count % len(neon_colors_list)], 255])
            
            for y in lines_to_clear:
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
        
        return len(lines_to_clear)
    
    def calculate_score(self, lines_cleared: int):
        self.lines += lines_cleared
        multiplier = 2 ** (self.level - 1)
        line_score = (lines_cleared ** 2) * multiplier
        self.score += line_score

        self.combo += 1
        combo_bonus = 0
        if self.combo > 1:
            combo_bonus = (2 ** (self.combo - 1)) * (self.level ** 2)
            self.score += combo_bonus
            shake_intensity = min(5, self.combo)
            self.combo_shake = shake_intensity * 15

        # 先计算 y_pos 位置
        if self.current_piece:
            blocks = self.current_piece.get_blocks()
            if blocks:
                avg_y = sum(y for x, y in blocks) / len(blocks)
                y_pos = BOARD_Y + (avg_y - 2) * GRID_SIZE
            else:
                y_pos = BOARD_Y + BOARD_HEIGHT // 2
        else:
            y_pos = BOARD_Y + BOARD_HEIGHT // 2

        if lines_cleared == 4:
            # 增强 TETRIS 屏幕震动 - 持续震动
            self.shake_offset = [random.randint(-12, 12), random.randint(-12, 12)]

            # 触发慢动作
            self.slow_motion_timer = 0.5  # 0.5秒慢动作
            self.slow_motion_factor = 0.3  # 30% 速度

            # 额外金色粒子爆发 - 减少数量
            for _ in range(40):
                self.particles.append(Particle(
                    BOARD_X + BOARD_WIDTH // 2, y_pos,
                    (255, 215, 0), 4  # 金色粒子
                ))

        if lines_cleared == 4:
            text = f"TETRIS! +{line_score}"
            self.floating_texts.append(FloatingText(BOARD_X + BOARD_WIDTH // 2, y_pos, text, (255, 255, 255), 20, True, 0))
        else:
            self.floating_texts.append(FloatingText(BOARD_X + BOARD_WIDTH // 2, y_pos, f"+{line_score}", (255, 255, 255), 16, False, 0))

        if self.combo > 1:
            combo_text = f"COMBO x{self.combo}! +{combo_bonus}"
            self.floating_texts.append(FloatingText(BOARD_X + BOARD_WIDTH // 2, y_pos + 40, combo_text, (255, 200, 0), 16, False, self.combo))

        new_level = self.lines // 10 + 1
        if new_level > self.level:
            self.level = new_level
            self.level_up_effect = 45
            self.shake_offset = [random.randint(-10, 10), random.randint(-10, 10)]
            self.fall_speed = max(0.08, 1.0 - (self.level - 1) * 0.08)

            # 升级暂停：暂停方块下落，等待特效播放完成
            self.level_up_pause = True

            # 触发升级特效，传入方块位置
            self.trigger_level_up_effects(y_pos)

    def trigger_level_up_effects(self, block_y: float = None):
        """触发升级特效"""
        # 使用方块落下位置作为中心
        if block_y is None:
            block_y = BOARD_Y + BOARD_HEIGHT // 2
        center_x = BOARD_X + BOARD_WIDTH // 2
        center_y = block_y

        # 边缘脉冲
        self.edge_pulse = 1.0

        # 方块闪光
        self.block_flash = 1.0

        # 粒子爆发
        self.spawn_level_up_particles(center_x, center_y)

        # Level Up 浮动文字 - 金色
        self.floating_texts.append(FloatingText(
            center_x, center_y - 50, "LEVEL UP!", (255, 215, 0), 32, True, 0
        ))

    def spawn_level_up_particles(self, cx: int, cy: int):
        """生成升级粒子 - 优化版本：减少数量但保持视觉效果"""
        # 中心爆发 - 减少到30个
        for _ in range(30):
            self.particles.append(Particle(cx, cy, (255, 215, 0), 4))

        # 四角爆发 - 减少到每角10个
        corners = [(0, 0), (SCREEN_WIDTH, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT)]
        for corner_x, corner_y in corners:
            for _ in range(10):
                self.particles.append(Particle(corner_x, corner_y, (255, 200, 50), 4))

    def update_level_up_effects(self):
        """更新升级特效"""
        # 清理冲击波（如果有残留）
        self.shockwaves.clear()

        # 更新边缘脉冲
        if self.edge_pulse > 0:
            self.edge_pulse -= 1.0 / 45
        else:
            # 边缘脉冲结束，解除升级暂停
            if self.level_up_pause:
                self.level_up_pause = False

        # 更新方块闪光
        if self.block_flash > 0:
            self.block_flash -= 1.0 / 45

    def draw_level_up_effects(self):
        """绘制升级特效"""
        # 绘制边缘光晕
        if self.edge_pulse > 0:
            self.draw_edge_glow()

    def draw_edge_glow(self):
        """绘制边缘光晕效果 - 优化版本"""
        edge_alpha = int(200 * self.edge_pulse)

        # 简化的金色渐变
        def gold_color(progress):
            if progress < 0.5:
                return (255, 215, 0)
            else:
                return (255, 230, 150)

        edge_height = 40

        # 上边缘 - 使用渐变矩形代替逐像素绘制
        edge_surf = pygame.Surface((SCREEN_WIDTH, edge_height), pygame.SRCALPHA)
        for y in range(edge_height):
            alpha = int(edge_alpha * (1 - y / edge_height) ** 1.5)
            color = gold_color(y / edge_height)
            pygame.draw.line(edge_surf, (*color, alpha), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(edge_surf, (0, 0))

        # 下边缘
        edge_surf = pygame.Surface((SCREEN_WIDTH, edge_height), pygame.SRCALPHA)
        for y in range(edge_height):
            alpha = int(edge_alpha * (y / edge_height) ** 1.5)
            color = gold_color(y / edge_height)
            pygame.draw.line(edge_surf, (*color, alpha), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(edge_surf, (0, SCREEN_HEIGHT - edge_height))

        edge_width = 40

        # 左边缘
        edge_surf = pygame.Surface((edge_width, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(edge_width):
            alpha = int(edge_alpha * (1 - x / edge_width) ** 1.5)
            color = gold_color(x / edge_width)
            pygame.draw.line(edge_surf, (*color, alpha), (x, 0), (x, SCREEN_HEIGHT))
        self.screen.blit(edge_surf, (0, 0))

        # 右边缘
        edge_surf = pygame.Surface((edge_width, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(edge_width):
            alpha = int(edge_alpha * (x / edge_width) ** 1.5)
            color = gold_color(x / edge_width)
            pygame.draw.line(edge_surf, (*color, alpha), (x, 0), (x, SCREEN_HEIGHT))
        self.screen.blit(edge_surf, (SCREEN_WIDTH - edge_width, 0))

    def draw_neon_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font,
                        x: int, y: int, color: Tuple[int, int, int], glow_size: int = 2, pulse: bool = False):
        for radius, base_a in [(4, 25), (2, 50)]:
            gs = font.render(text, True, color)
            gs.set_alpha(base_a)
            for dx in range(-radius, radius + 1, max(1, radius // 2)):
                for dy in range(-radius, radius + 1, max(1, radius // 2)):
                    if dx != 0 or dy != 0:
                        surface.blit(gs, (x + dx, y + dy))

        ec = tuple(min(255, c + 100) for c in color)
        es = font.render(text, True, ec)
        es.set_alpha(180)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            surface.blit(es, (x + dx, y + dy))

        s = font.render(text, True, color)
        surface.blit(s, (x, y))

    def draw_rainbow_title(self, surface: pygame.Surface, text: str, font: pygame.font.Font, x: int, y: int):
        """绘制霓虹灯效果的标题 - 参考 Version01"""
        # 彩虹颜色 - 与 Version01 相同的算法
        t = self.time
        def rainbow_color(offset=0):
            return (
                int(127 + 127 * math.sin(t * 0.8 + offset)),
                int(127 + 127 * math.sin(t * 0.8 + offset + 2.094)),
                int(127 + 127 * math.sin(t * 0.8 + offset + 4.189)),
            )

        color = rainbow_color()

        # 中等边缘光晕 (无呼吸/闪烁)
        for radius, base_a in [(4, 25), (2, 50)]:
            gs = font.render(text, True, color)
            gs.set_alpha(base_a)
            for dx in range(-radius, radius + 1, max(1, radius // 2)):
                for dy in range(-radius, radius + 1, max(1, radius // 2)):
                    if dx != 0 or dy != 0:
                        surface.blit(gs, (x + dx, y + dy))

        # 边缘高亮 (明亮轮廓)
        ec = tuple(min(255, c + 100) for c in color)
        es = font.render(text, True, ec)
        es.set_alpha(180)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(es, (x + dx, y + dy))

        # 核心
        s = font.render(text, True, color)
        surface.blit(s, (x, y))
    
    def draw_neon_block(self, surface: pygame.Surface, x: int, y: int, color: Tuple[int, int, int], size: int = GRID_SIZE):
        breath = 0.92 + 0.08 * math.sin(self.time * 3)
        r, g, b = color

        # 升级闪光效果 - 更强烈的金色闪光
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

        # 简化光晕绘制 - 减少层数
        glow_surf = pygame.Surface((size + 16, size + 16), pygame.SRCALPHA)
        for i in range(8, 0, -2):  # 减少层数从10到8
            alpha = int(25 * (1 - i / 8))
            pygame.draw.rect(glow_surf, (r, g, b, alpha), (8 - i, 8 - i, size + i * 2, size + i * 2), border_radius=5)
        surface.blit(glow_surf, (x - 8, y - 8))

        block_surf = pygame.Surface((size, size), pygame.SRCALPHA)

        pygame.draw.rect(block_surf, (r // 4, g // 4, b // 4, 200), (0, 0, size, size), border_radius=4)

        inner_margin = 3
        inner_size = size - inner_margin * 2
        pygame.draw.rect(block_surf, (r, g, b, 60), (inner_margin, inner_margin, inner_size, inner_size), border_radius=3)

        # 简化玻璃高光效果
        for i in range(inner_size // 3):
            alpha = int(80 * (1 - i / (inner_size // 3)))
            pygame.draw.line(block_surf, (255, 255, 255, alpha), (inner_margin + 2, inner_margin + 2 + i), (inner_size + inner_margin - 2, inner_margin + 2 + i))

        pygame.draw.rect(block_surf, (255, 255, 255, 40), (inner_margin + 2, inner_margin + 2, 3, inner_size - 4), border_radius=2)
        pygame.draw.rect(block_surf, (0, 0, 0, 60), (size - inner_margin - 5, inner_margin + 2, 3, inner_size - 4), border_radius=2)
        pygame.draw.rect(block_surf, (0, 0, 0, 40), (inner_margin + 2, size - inner_margin - 4, inner_size - 4, 3), border_radius=2)
        pygame.draw.rect(block_surf, (r, g, b, 200), (0, 0, size, size), 2, border_radius=4)
        pygame.draw.rect(block_surf, (min(255, r + 50), min(255, g + 50), min(255, b + 50), 150), (1, 1, size - 2, size - 2), 1, border_radius=3)

        surface.blit(block_surf, (x, y))
    
    def draw_ghost_block(self, surface: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]):
        breath = 0.7 + 0.3 * math.sin(self.time * 2)
        ghost_surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        
        glow_surf = pygame.Surface((GRID_SIZE + 8, GRID_SIZE + 8), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            alpha = int(30 * breath * (1 - i / 4))
            pygame.draw.rect(glow_surf, (*color, alpha), (4 - i, 4 - i, GRID_SIZE + i * 2, GRID_SIZE + i * 2), border_radius=4)
        ghost_surf.blit(glow_surf, (-4, -4))
        
        pygame.draw.rect(ghost_surf, (*color, int(30 * breath)), (0, 0, GRID_SIZE, GRID_SIZE), border_radius=3)
        
        pygame.draw.rect(ghost_surf, (*color, int(120 * breath)), (0, 0, GRID_SIZE, GRID_SIZE), 2, border_radius=3)
        
        highlight_color = (min(255, color[0] + 100), min(255, color[1] + 100), min(255, color[2] + 100))
        pygame.draw.rect(ghost_surf, (*highlight_color, int(80 * breath)), (1, 1, GRID_SIZE - 2, GRID_SIZE - 2), 1, border_radius=2)
        
        surface.blit(ghost_surf, (x, y))
    
    def draw_grid(self):
        self.screen.blit(self.grid_surface, (BOARD_X + self.shake_offset[0], BOARD_Y + self.shake_offset[1]))
    
    def draw_board(self):
        for y in range(2, GRID_HEIGHT + 2):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    color = NEON_COLORS.get(self.grid[y][x], (255, 255, 255))
                    draw_x = BOARD_X + x * GRID_SIZE + self.shake_offset[0]
                    draw_y = BOARD_Y + (y - 2) * GRID_SIZE + self.shake_offset[1]
                    self.draw_neon_block(self.screen, draw_x, draw_y, color)
    
    def draw_current_piece(self):
        if not self.current_piece:
            return
        
        ghost_blocks = self.get_ghost_position()
        for x, y in ghost_blocks:
            if y >= 2:
                draw_x = BOARD_X + x * GRID_SIZE + self.shake_offset[0]
                draw_y = BOARD_Y + (y - 2) * GRID_SIZE + self.shake_offset[1]
                self.draw_ghost_block(self.screen, draw_x, draw_y, self.current_piece.color)
        
        for x, y in self.current_piece.get_blocks():
            if y >= 0:
                draw_x = BOARD_X + x * GRID_SIZE + self.shake_offset[0]
                draw_y = BOARD_Y + (y - 2) * GRID_SIZE + self.shake_offset[1]
                self.draw_neon_block(self.screen, draw_x, draw_y, self.current_piece.color)
    
    def draw_next_piece(self):
        if not self.next_piece:
            return
        
        min_x, max_x, min_y, max_y = self.next_piece.get_bounds()
        width = (max_x - min_x + 1) * 22
        height = (max_y - min_y + 1) * 22
        
        preview_x = PANEL_X + (PANEL_WIDTH - width) // 2 - min_x * 22
        preview_y = BOARD_Y + 130 + (88 - height) // 2 - min_y * 22
        
        shape = self.next_piece.shapes[0]
        for dx, dy in shape:
            x = preview_x + dx * 22
            y = preview_y + dy * 22
            self.draw_neon_block(self.screen, x, y, self.next_piece.color, 20)
    
    def draw_divider(self):
        divider_x = BOARD_X + BOARD_WIDTH
        
        hue = (self.time * 50) % 360
        r = int(128 + 127 * math.sin(math.radians(hue)))
        g = int(128 + 127 * math.sin(math.radians(hue + 120)))
        b = int(128 + 127 * math.sin(math.radians(hue + 240)))
        
        pygame.draw.line(self.screen, (r, g, b), (divider_x, BOARD_Y), (divider_x, BOARD_Y + BOARD_HEIGHT), 1)
    
    def draw_panel(self):
        # 使用缓存的面板背景
        self.screen.blit(self.panel_bg_surface, (PANEL_X, BOARD_Y))
        
        title_text = "TETRIS"
        title_x = PANEL_X + (PANEL_WIDTH - self.font_medium.size(title_text)[0]) // 2
        self.draw_rainbow_title(self.screen, title_text, self.font_title_medium, title_x, BOARD_Y + 40)
        
        labels = [
            ("下一个", BOARD_Y + 120),
            ("最高分", BOARD_Y + 240),
            ("得分", BOARD_Y + 330),
            ("消行", BOARD_Y + 400),
            ("关卡", BOARD_Y + 470),
        ]
        
        for label, y in labels:
            self.draw_neon_text(self.screen, label, self.font_tiny, PANEL_X + 20, y, (150, 150, 180), 1, False)
        
        best_text = self.font_medium.render(str(self.high_score), True, (255, 200, 0))
        self.screen.blit(best_text, (PANEL_X + 20, BOARD_Y + 260))
        
        score_text = self.font_small.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(score_text, (PANEL_X + 20, BOARD_Y + 350))
        
        lines_text = self.font_small.render(str(self.lines), True, (255, 255, 255))
        self.screen.blit(lines_text, (PANEL_X + 20, BOARD_Y + 420))
        
        level_text = self.font_small.render(str(self.level), True, (255, 255, 255))
        if self.level_up_effect > 0:
            scale = 1.0 + 0.3 * math.sin(self.time * 20)
            scaled = pygame.transform.scale(level_text, (int(level_text.get_width() * scale), int(level_text.get_height() * scale)))
            self.screen.blit(scaled, (PANEL_X + 20, BOARD_Y + 490))
        else:
            self.screen.blit(level_text, (PANEL_X + 20, BOARD_Y + 490))
        
        help_text = self.font_tiny.render("H - 帮助", True, (100, 100, 120))
        self.screen.blit(help_text, (PANEL_X + 20, BOARD_Y + BOARD_HEIGHT - 30))
    
    def draw_background(self):
        # 使用缓存的背景 Surface
        self.screen.blit(self.bg_surface, (0, 0))

        for star in self.stars:
            star.update(self.time)
            star.draw(self.screen)
    
    def draw_effects(self):
        if self.clear_flash_timer > 0:
            for y in self.clear_flash_lines:
                flash_alpha = int(255 * (self.clear_flash_timer / 20))
                flash_surf = pygame.Surface((BOARD_WIDTH, GRID_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(flash_surf, (255, 255, 255, flash_alpha), (0, 0, BOARD_WIDTH, GRID_SIZE))
                self.screen.blit(flash_surf, (BOARD_X + self.shake_offset[0], BOARD_Y + (y - 2) * GRID_SIZE + self.shake_offset[1]))

        for fe in self.flash_effects:
            row, color, alpha, n = fe
            fs = pygame.Surface((BOARD_WIDTH, GRID_SIZE), pygame.SRCALPHA)
            fs.fill((*color, min(200, alpha)))
            self.screen.blit(fs, (BOARD_X + self.shake_offset[0], BOARD_Y + row * GRID_SIZE + self.shake_offset[1]))
            if n >= 2:
                expand = int((255 - alpha) / 255 * GRID_SIZE * n)
                gs = pygame.Surface((BOARD_WIDTH, GRID_SIZE * n + expand * 2), pygame.SRCALPHA)
                gs.fill((*color, min(80, alpha // 2)))
                self.screen.blit(gs, (BOARD_X + self.shake_offset[0], BOARD_Y + row * GRID_SIZE - expand + self.shake_offset[1]))

        for sl in self.scan_lines:
            y_pos, color, alpha = sl
            ss = pygame.Surface((BOARD_WIDTH, 3), pygame.SRCALPHA)
            ss.fill((*color, min(255, alpha * 2)))
            self.screen.blit(ss, (BOARD_X + self.shake_offset[0], BOARD_Y + y_pos + self.shake_offset[1]))

        if self.level_up_effect > 0:
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
    
    def draw_trails(self):
        new_trails = []
        total_trails = len(self.trail_positions)
        for idx, (x, y, color, life) in enumerate(self.trail_positions):
            if life > 0:
                # 计算透明度渐变：最早的拖影透明度约10%，最新的较不透明
                # idx=0 是最早的，idx=total_trails-1 是最新的
                if total_trails > 1:
                    # 从10%渐变到80%
                    gradient_factor = 0.1 + 0.7 * (idx / (total_trails - 1))
                else:
                    gradient_factor = 0.5
                alpha = int(255 * gradient_factor * life)

                trail_surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(trail_surf, (*color, alpha), (0, 0, GRID_SIZE, GRID_SIZE), border_radius=3)
                self.screen.blit(trail_surf, (int(x - GRID_SIZE // 2), int(y - GRID_SIZE // 2)))
                new_trails.append((x, y, color, life - 0.05))
        self.trail_positions = new_trails
    
    def draw_particles(self):
        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw_floating_texts(self, dt: float = 0.016):
        for text in self.floating_texts[:]:
            text.update(dt)
            text.draw(self.screen, self.font_medium, self.font_name)
            if text.alpha <= 0:
                self.floating_texts.remove(text)
    
    def draw_start_screen(self):
        self.draw_background()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        title_text = "TETRIS"
        title_x = (SCREEN_WIDTH - self.font_large.size(title_text)[0]) // 2
        self.draw_rainbow_title(self.screen, title_text, self.font_title_large, title_x, 150)
        
        instructions = [
            "← → : 移动",
            "↑ : 旋转",
            "↓ : 加速下落",
            "空格 : 硬降",
            "P : 暂停",
            "R : 重新开始",
            "H : 帮助",
            "",
            "按 空格 开始游戏"
        ]
        
        y = 280
        for line in instructions:
            text = self.font_small.render(line, True, (200, 200, 220))
            self.screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, y))
            y += 35
    
    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_rainbow_title(self.screen, "暂停", self.font_title_large, (SCREEN_WIDTH - 70) // 2, SCREEN_HEIGHT // 2 - 50)
        
        resume_text = self.font_medium.render("按 P 继续", True, (200, 200, 220))
        self.screen.blit(resume_text, ((SCREEN_WIDTH - resume_text.get_width()) // 2, SCREEN_HEIGHT // 2 + 20))
    
    def draw_help_screen(self):
        self.draw_background()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_rainbow_title(self.screen, "帮助", self.font_title_medium, (SCREEN_WIDTH - 70) // 2, 30)
        
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
        
        if self.font_name:
            title_font = pygame.font.SysFont(self.font_name, 17, bold=True)
            content_font = pygame.font.SysFont(self.font_name, 15)
        else:
            title_font = pygame.font.Font(None, 20)
            content_font = pygame.font.Font(None, 18)

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
    
    def draw_gameover_screen(self):
        self.draw_background()
        self.draw_grid()
        self.draw_board()
        self.draw_panel()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title_text = "游戏结束"
        title_x = (SCREEN_WIDTH - self.font_title_large.size(title_text)[0]) // 2
        self.draw_rainbow_title(self.screen, title_text, self.font_title_large, title_x, int(SCREEN_HEIGHT / 4))

        # 得分字体加粗
        if self.font_name:
            score_font = pygame.font.SysFont(self.font_name, 20, bold=True)
        else:
            score_font = pygame.font.Font(None, 24, bold=True)
        score_text = score_font.render(f"得分: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, int(SCREEN_HEIGHT / 3) + 70))
        
        if self.score >= self.high_score:
            best_text = self.font_small.render("新纪录!", True, (255, 200, 0))
            self.screen.blit(best_text, ((SCREEN_WIDTH - best_text.get_width()) // 2, int(SCREEN_HEIGHT / 3) + 100))

        restart_text = self.font_tiny.render("按 R 重新开始", True, (150, 150, 180))
        self.screen.blit(restart_text, ((SCREEN_WIDTH - restart_text.get_width()) // 2, int(SCREEN_HEIGHT / 3) + 140))
    
    def update(self, dt: float):
        # 应用慢动作
        if self.slow_motion_timer > 0:
            self.slow_motion_timer -= dt
            actual_dt = dt * self.slow_motion_factor
        else:
            actual_dt = dt
            self.slow_motion_factor = 1.0

        self.time += actual_dt

        if self.clear_flash_timer > 0:
            self.clear_flash_timer -= 1

        for fe in self.flash_effects:
            fe[2] -= 10
        self.flash_effects = [fe for fe in self.flash_effects if fe[2] > 0]

        for sl in self.scan_lines:
            sl[2] -= 8
        self.scan_lines = [sl for sl in self.scan_lines if sl[2] > 0]

        if self.level_up_effect > 0:
            self.level_up_effect -= 1
        if self.rainbow_effect > 0:
            self.rainbow_effect -= 1
        if self.tetris_flash_effect > 0:
            self.tetris_flash_effect -= 1
        if self.combo_shake > 0:
            self.combo_shake -= 1

        # 更新 TETRIS 特效
        for effect in self.tetris_effects[:]:
            if not effect.update(actual_dt):
                self.tetris_effects.remove(effect)

        # TETRIS 震动持续效果
        if self.slow_motion_timer > 0:
            shake_intensity = self.slow_motion_timer * 24
            self.shake_offset = [
                random.randint(-int(shake_intensity), int(shake_intensity)),
                random.randint(-int(shake_intensity), int(shake_intensity))
            ]

        # 更新升级特效
        self.update_level_up_effects()

        if self.state == "playing":
            # 升级特效期间使用最慢速度（第一关速度）
            if self.level_up_pause:
                self.fall_timer += actual_dt
                if self.fall_timer >= 1.0:  # 第一关速度
                    self.fall_timer = 0
                    if not self.move_piece(0, 1):
                        self.lock_piece()
            else:
                self.fall_timer += actual_dt
                if self.fall_timer >= self.fall_speed:
                    self.fall_timer = 0
                    if not self.move_piece(0, 1):
                        self.lock_piece()
    
    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if self.state == "start":
                if event.key == pygame.K_SPACE:
                    self.state = "playing"
                elif event.key == pygame.K_h:
                    self.previous_state = "start"
                    self.state = "help"
            elif self.state == "help":
                if event.key == pygame.K_h or event.key == pygame.K_ESCAPE:
                    self.state = self.previous_state
            elif self.state == "playing":
                if event.key == pygame.K_p:
                    self.state = "paused"
                elif event.key == pygame.K_h:
                    self.previous_state = "playing"
                    self.state = "help"
                elif event.key == pygame.K_LEFT:
                    self.move_piece(-1, 0)
                    self.key_repeat_timers[pygame.K_LEFT] = self.key_repeat_delay
                elif event.key == pygame.K_RIGHT:
                    self.move_piece(1, 0)
                    self.key_repeat_timers[pygame.K_RIGHT] = self.key_repeat_delay
                elif event.key == pygame.K_DOWN:
                    self.move_piece(0, 1, add_trail=True)  # 玩家主动加速下落，产生拖影
                    self.key_repeat_timers[pygame.K_DOWN] = self.key_repeat_delay
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()
                elif event.key == pygame.K_r:
                    self.reset_game()
            elif self.state == "paused":
                if event.key == pygame.K_p:
                    self.state = "playing"
            elif self.state == "gameover":
                if event.key == pygame.K_r:
                    self.reset_game()
                    self.state = "playing"
        
        elif event.type == pygame.KEYUP:
            if event.key in self.key_repeat_timers:
                self.key_repeat_timers[event.key] = 0
    
    def handle_continuous_input(self, dt: int):
        if self.state != "playing":
            return
        
        keys = pygame.key.get_pressed()
        
        for key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN]:
            if keys[key]:
                if self.key_repeat_timers[key] > 0:
                    self.key_repeat_timers[key] -= dt
                    if self.key_repeat_timers[key] <= 0:
                        self.key_repeat_timers[key] = self.key_repeat_interval
                        if key == pygame.K_LEFT:
                            self.move_piece(-1, 0)
                        elif key == pygame.K_RIGHT:
                            self.move_piece(1, 0)
                        elif key == pygame.K_DOWN:
                            self.move_piece(0, 1, add_trail=True)  # 玩家主动加速下落，产生拖影
    
    def run(self):
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            dt_ms = current_time - last_time
            last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_input(event)
            
            self.handle_continuous_input(dt_ms)
            self.update(dt)
            
            if self.state == "start":
                self.draw_start_screen()
            elif self.state == "help":
                self.draw_help_screen()
            elif self.state == "playing":
                self.draw_background()
                self.draw_grid()
                self.draw_board()
                self.draw_current_piece()
                self.draw_next_piece()
                self.draw_divider()
                self.draw_panel()
                self.draw_effects()
                self.draw_trails()
                self.draw_particles()
                self.draw_floating_texts(dt)
                self.draw_level_up_effects()  # 升级特效绘制在最上层
            elif self.state == "paused":
                self.draw_background()
                self.draw_grid()
                self.draw_board()
                self.draw_current_piece()
                self.draw_next_piece()
                self.draw_divider()
                self.draw_panel()
                self.draw_pause_screen()
            elif self.state == "gameover":
                self.draw_gameover_screen()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
