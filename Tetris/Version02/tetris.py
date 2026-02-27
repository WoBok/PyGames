import pygame
import random
import sys
import math

pygame.init()

BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
INFO_WIDTH = 180
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

pygame.font.init()
FONT_PATH = None
try:
    font_names = ['microsoftyahei', 'microsoftyaheiui', 'simhei', 'simsun', 'mingliu', 'kaiti']
    for name in font_names:
        FONT_PATH = pygame.font.match_font(name)
        if FONT_PATH:
            break
except:
    FONT_PATH = None

if FONT_PATH:
    font_title = pygame.font.Font(FONT_PATH, 18)
    font_text = pygame.font.Font(FONT_PATH, 14)
    font_small = pygame.font.Font(FONT_PATH, 10)
else:
    font_title = pygame.font.Font(None, 18)
    font_text = pygame.font.Font(None, 14)
    font_small = pygame.font.Font(None, 10)

NEON_COLORS = [
    (255, 0, 85),
    (0, 255, 127),
    (0, 170, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 127, 0),
    (255, 0, 127),
    (127, 0, 255),
    (127, 255, 0)
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("霓虹俄罗斯方块")
clock = pygame.time.Clock()

class Trail:
    def __init__(self):
        self.trails = []
        self.max_trails = 200

    def add(self, x, y, color):
        if len(self.trails) < self.max_trails:
            self.trails.append({
                'x': x, 'y': y, 
                'color': list(color), 
                'alpha': 220,
                'size': BLOCK_SIZE - 6,
                'hue_offset': random.randint(-30, 30)
            })

    def update(self):
        for t in self.trails:
            t['alpha'] -= 20
            t['size'] -= 1.0
            t['hue_offset'] += 8
        self.trails = [t for t in self.trails if t['alpha'] > 0 and t['size'] > 4]

    def draw(self, surface):
        for t in self.trails:
            if 0 <= t['x'] < GRID_WIDTH and 0 <= t['y'] < GRID_HEIGHT:
                color = list(t['color'])
                h = t['hue_offset'] % 60 - 30
                color = [
                    min(255, max(0, color[0] + h)),
                    min(255, max(0, color[1] + h)),
                    min(255, max(0, color[2] + h))
                ]
                size = max(6, int(t['size']))
                s = pygame.Surface((size, size), pygame.SRCALPHA)
                
                center = size // 2
                for r in range(center, 0, -1):
                    alpha = int(t['alpha'] * (r / center) * 0.6)
                    pygame.draw.circle(s, (*color, alpha), (center, center), r)
                
                surface.blit(s, (t['x'] * BLOCK_SIZE + (BLOCK_SIZE - size) // 2, 
                               t['y'] * BLOCK_SIZE + (BLOCK_SIZE - size) // 2))

class Particle:
    def __init__(self, x, y, color, count=40):
        self.particles = []
        for _ in range(count):
            self.particles.append({
                'x': x + random.uniform(-20, 20),
                'y': y + random.uniform(-20, 20),
                'color': list(color),
                'vx': random.uniform(-6, 6),
                'vy': random.uniform(-10, 4),
                'life': random.randint(35, 65),
                'max_life': 65,
                'size': random.randint(3, 7),
                'hue_shift': random.randint(-40, 40)
            })

    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.25
            p['life'] -= 1

    def is_alive(self):
        return any(p['life'] > 0 for p in self.particles)

    def draw(self, surface):
        for p in self.particles:
            if p['life'] > 0:
                alpha = int(p['life'] / p['max_life'] * 230)
                size = int(p['size'] * (p['life'] / p['max_life']) + 1)
                if size > 0:
                    color = list(p['color'])
                    h = p['hue_shift']
                    color = [
                        min(255, max(0, color[0] + h)),
                        min(255, max(0, color[1] + h)),
                        min(255, max(0, color[2] + h))
                    ]
                    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*color, alpha), (size, size), size)
                    surface.blit(s, (p['x'] - size, p['y'] - size))

class ClearEffect:
    def __init__(self, rows):
        self.rows = list(rows)
        self.timer = 45
        self.max_timer = 45
        self.particles = []
        
        for row in self.rows:
            base_color = NEON_COLORS[row % len(NEON_COLORS)]
            for _ in range(8):
                self.particles.append({
                    'x': random.randint(0, GRID_WIDTH * BLOCK_SIZE),
                    'y': row * BLOCK_SIZE + BLOCK_SIZE // 2,
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-8, 8),
                    'life': random.randint(25, 45),
                    'color': base_color,
                    'size': random.randint(3, 6)
                })

    def update(self):
        self.timer -= 1
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.4
            p['life'] -= 1

    def is_alive(self):
        return self.timer > 0

    def draw(self, surface):
        if self.timer <= 0:
            return
            
        progress = 1.0 - (self.timer / self.max_timer)
        
        for idx, row in enumerate(self.rows):
            color = NEON_COLORS[row % len(NEON_COLORS)]
            
            brightness = int(180 + 75 * math.sin(progress * math.pi * 3))
            
            for x in range(0, GRID_WIDTH * BLOCK_SIZE, 3):
                wave = math.sin((x / 30.0) + progress * math.pi * 8 + row) * 40
                alpha = int(brightness + wave)
                alpha = max(0, min(255, alpha))
                pygame.draw.line(surface, (*color, min(255, alpha)), 
                              (x, row * BLOCK_SIZE), 
                              (x + 2, (row + 1) * BLOCK_SIZE))
            
            if progress < 0.3:
                flash = int(255 * (1 - progress / 0.3))
                for x in range(0, GRID_WIDTH * BLOCK_SIZE, 8):
                    if random.random() < 0.5:
                        pygame.draw.line(surface, (255, 255, 255, flash),
                                      (x, row * BLOCK_SIZE),
                                      (x + 4, (row + 1) * BLOCK_SIZE))

        for p in self.particles:
            if p['life'] > 0:
                alpha = int(p['life'] / 45.0 * 220)
                size = max(1, int(p['size'] * (p['life'] / 45.0)))
                if size > 0:
                    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*p['color'], alpha), (size, size), size)
                    surface.blit(s, (p['x'] - size, p['y'] - size))

class TetrisGame:
    def __init__(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.lines_cleared = 0
        self.total_lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.trail = Trail()
        self.particles_list = []
        self.clear_effects = []
        self.fall_speed = 1000
        self.last_drop = pygame.time.get_ticks()

        self.rainbow_timer = 0
        self.rainbow_phase = 0
        self.is_rainbow_flashing = False
        self.screen_shake_timer = 0
        self.level_shake_timer = 0
        self.screen_shake_offset = [0, 0]
        self.level_shake_offset = [0, 0]

        self.combo_count = 0
        self.last_clear_time = 0
        self.combo_timeout = 2000

        self.spawn_piece()

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open('highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def spawn_piece(self):
        if self.next_piece is None:
            shape_idx = random.randint(0, len(SHAPES) - 1)
            color_idx = random.randint(0, len(NEON_COLORS) - 1)
            self.current_piece = {
                'shape': [row[:] for row in SHAPES[shape_idx]],
                'color': NEON_COLORS[color_idx],
                'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
                'y': 0,
                'color_idx': color_idx
            }
        else:
            self.current_piece = self.next_piece

        shape_idx = random.randint(0, len(SHAPES) - 1)
        color_idx = random.randint(0, len(NEON_COLORS) - 1)
        self.next_piece = {
            'shape': [row[:] for row in SHAPES[shape_idx]],
            'color': NEON_COLORS[color_idx],
            'x': 0,
            'y': 0,
            'color_idx': color_idx
        }

        if self.check_collision(self.current_piece['x'], self.current_piece['y'], self.current_piece['shape']):
            self.game_over = True

    def check_collision(self, x, y, shape):
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    new_x = x + col
                    new_y = y + row
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False

    def rotate_piece(self):
        shape = self.current_piece['shape']
        
        rotated = [[shape[len(shape) - 1 - j][i] for j in range(len(shape))] for i in range(len(shape[0]))]
        
        if not self.check_collision(self.current_piece['x'], self.current_piece['y'], rotated):
            self.current_piece['shape'] = rotated
        else:
            kicks = [-1, 1, -2, 2]
            for kick in kicks:
                if not self.check_collision(self.current_piece['x'] + kick, self.current_piece['y'], rotated):
                    self.current_piece['x'] += kick
                    self.current_piece['shape'] = rotated
                    break

    def move_piece(self, dx, dy):
        if not self.check_collision(self.current_piece['x'] + dx, self.current_piece['y'] + dy, self.current_piece['shape']):
            if dy > 0:
                shape = self.current_piece['shape']
                for row in range(len(shape)):
                    for col in range(len(shape[row])):
                        if shape[row][col]:
                            self.trail.add(
                                self.current_piece['x'] + col,
                                self.current_piece['y'] + row,
                                self.current_piece['color']
                            )
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy
            return True
        return False

    def lock_piece(self):
        shape = self.current_piece['shape']
        color = self.current_piece['color']
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    y = self.current_piece['y'] + row
                    x = self.current_piece['x'] + col
                    if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                        self.grid[y][x] = color

        cleared = self.clear_lines()
        
        current_time = pygame.time.get_ticks()
        if cleared > 0:
            if current_time - self.last_clear_time < self.combo_timeout:
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.last_clear_time = current_time
            
            base_score = cleared ** 2
            combo_multiplier = self.combo_count ** 2
            score_gain = base_score * combo_multiplier * (2 ** (self.level - 1))
            self.score += score_gain
            
            self.total_lines_cleared += cleared
            self.lines_cleared += cleared

            center_x = self.current_piece['x'] * BLOCK_SIZE + len(shape[0]) * BLOCK_SIZE // 2
            center_y = self.current_piece['y'] * BLOCK_SIZE + len(shape) * BLOCK_SIZE // 2
            
            particle_count = 30 + cleared * 25
            self.particles_list.append(Particle(center_x, center_y, random.choice(NEON_COLORS), particle_count))

            if self.total_lines_cleared >= self.level * 10:
                self.level_up()
        else:
            self.combo_count = 0

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

        self.spawn_piece()

    def clear_lines(self):
        cleared_rows = []
        
        for row in range(GRID_HEIGHT):
            is_full = True
            for col in range(GRID_WIDTH):
                if not self.grid[row][col]:
                    is_full = False
                    break
            if is_full:
                cleared_rows.append(row)

        if cleared_rows:
            try:
                self.clear_effects.append(ClearEffect(cleared_rows))
            except:
                pass

            new_grid = []
            rows_to_keep = [r for r in range(GRID_HEIGHT) if r not in cleared_rows]
            for row in rows_to_keep:
                new_grid.append(self.grid[row])
            
            while len(new_grid) < GRID_HEIGHT:
                new_grid.insert(0, [0] * GRID_WIDTH)
            
            self.grid = new_grid

        return len(cleared_rows)

    def level_up(self):
        self.level += 1
        self.fall_speed = max(100, 1000 - (self.level - 1) * 100)
        
        self.is_rainbow_flashing = True
        self.rainbow_timer = 78
        self.rainbow_phase = 0
        
        self.screen_shake_timer = 60
        self.level_shake_timer = 60

    def update(self):
        self.trail.update()

        for particles in self.particles_list:
            particles.update()
        self.particles_list = [p for p in self.particles_list if p.is_alive()]

        for effect in self.clear_effects:
            effect.update()
        self.clear_effects = [e for e in self.clear_effects if e.is_alive()]

        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1
            self.screen_shake_offset = [random.randint(-8, 8), random.randint(-8, 8)]
        else:
            self.screen_shake_offset = [0, 0]

        if self.level_shake_timer > 0:
            self.level_shake_timer -= 1
            self.level_shake_offset = [random.randint(-4, 4), random.randint(-4, 4)]
        else:
            self.level_shake_offset = [0, 0]

        if self.is_rainbow_flashing:
            self.rainbow_timer -= 1
            self.rainbow_phase += 0.18
            if self.rainbow_timer <= 0:
                self.is_rainbow_flashing = False

        if self.game_over or self.paused:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop >= self.fall_speed:
            self.last_drop = current_time
            if not self.move_piece(0, 1):
                self.lock_piece()

    def draw_neon_block_glass(self, surface, x, y, color, glow_intensity=1.0):
        center_x = x * BLOCK_SIZE + BLOCK_SIZE // 2
        center_y = y * BLOCK_SIZE + BLOCK_SIZE // 2
        
        time_val = pygame.time.get_ticks() / 500.0
        pulse = 0.85 + 0.15 * math.sin(time_val + x + y)
        
        for i in range(5, 0, -1):
            glow_alpha = int(22 * glow_intensity * pulse * (1 - i/6))
            glow_size = BLOCK_SIZE + i * 6
            glow_rect = pygame.Rect(
                center_x - glow_size // 2,
                center_y - glow_size // 2,
                glow_size, glow_size
            )
            glow_color = list(color)
            s = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.rect(s, (*glow_color, glow_alpha), s.get_rect(), border_radius=8)
            surface.blit(s, (glow_rect.x, glow_rect.y))

        block_rect = pygame.Rect(x * BLOCK_SIZE + 2, y * BLOCK_SIZE + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4)
        
        gradient_colors = [
            tuple(min(255, c + 60) for c in color),
            color,
            tuple(max(0, c - 40) for c in color)
        ]
        
        s = pygame.Surface((BLOCK_SIZE - 4, BLOCK_SIZE - 4), pygame.SRCALPHA)
        
        for i in range(BLOCK_SIZE - 4):
            ratio = i / (BLOCK_SIZE - 4)
            if ratio < 0.5:
                interp_color = [
                    gradient_colors[0][c] * (1 - ratio * 2) + gradient_colors[1][c] * (ratio * 2)
                    for c in range(3)
                ]
            else:
                interp_color = [
                    gradient_colors[1][c] * (1 - (ratio - 0.5) * 2) + gradient_colors[2][c] * ((ratio - 0.5) * 2)
                    for c in range(3)
                ]
            pygame.draw.line(s, [int(c) for c in interp_color], (i, 0), (i, BLOCK_SIZE - 5))
        
        surface.blit(s, (block_rect.x, block_rect.y))

        highlight = pygame.Rect(x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 4, BLOCK_SIZE - 10, BLOCK_SIZE // 3)
        highlight_s = pygame.Surface((highlight.width, highlight.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_s, (255, 255, 255, 100), highlight_s.get_rect(), border_radius=3)
        surface.blit(highlight_s, (highlight.x, highlight.y))

        border_color = tuple(min(255, c + 80) for c in color)
        pygame.draw.rect(surface, border_color, block_rect, 2, border_radius=4)

        reflection = pygame.Rect(x * BLOCK_SIZE + 6, y * BLOCK_SIZE + 6, 4, 4)
        pygame.draw.rect(surface, (255, 255, 255, 150), reflection, border_radius=2)

    def draw(self):
        if self.is_rainbow_flashing:
            progress = 1.0 - (self.rainbow_timer / 78.0)
            wave = math.sin(self.rainbow_phase) * 0.35 + 0.65
            
            screen.fill((0, 0, 0))
            
            rainbow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            for y in range(SCREEN_HEIGHT):
                hue = ((y / float(SCREEN_HEIGHT)) * 90 + pygame.time.get_ticks() / 15.0) % 360
                rainbow_color = pygame.Color(0, 0, 0)
                rainbow_color.hsva = (int(hue), 100, int(55 * wave), 100)
                
                wave_offset = math.sin((y / 40.0) + self.rainbow_phase * 2.5) * 30
                alpha = int(200 + wave_offset)
                
                pygame.draw.line(rainbow_surface, (*rainbow_color[:3], min(255, max(0, alpha))), (0, y), (SCREEN_WIDTH, y))
            
            screen.blit(rainbow_surface, (0, 0))
        else:
            screen.fill((5, 5, 15))

        offset_x, offset_y = self.screen_shake_offset
        
        game_surface = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), pygame.SRCALPHA)
        game_surface.fill((0, 0, 0, 200))

        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                pygame.draw.rect(game_surface, (20, 20, 35),
                               (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
                pygame.draw.rect(game_surface, (15, 15, 30),
                               (col * BLOCK_SIZE + 1, row * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2), 1)

        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                grid_color = self.grid[row][col]
                if grid_color:
                    self.draw_neon_block_glass(game_surface, col, row, grid_color)

        if self.current_piece:
            shape = self.current_piece['shape']
            color = self.current_piece['color']
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col]:
                        self.draw_neon_block_glass(game_surface,
                                           self.current_piece['x'] + col,
                                           self.current_piece['y'] + row,
                                           color)

        self.trail.draw(game_surface)

        for effect in self.clear_effects:
            effect.draw(game_surface)

        screen.blit(game_surface, (offset_x, offset_y))

        for particles in self.particles_list:
            particles.draw(screen)

        info_x = GRID_WIDTH * BLOCK_SIZE + 15
        info_y_start = 30
        
        label_value_gap = 70
        line_height = 35

        def draw_text_simple(text, font, color, x, y):
            return font.render(text, True, color)

        text_next = draw_text_simple("下一个", font_title, (0, 255, 255), info_x, 10)
        screen.blit(text_next, (info_x, 10))

        if self.next_piece:
            next_shape = self.next_piece['shape']
            next_color = self.next_piece['color']
            piece_width = len(next_shape[0]) * 20
            piece_height = len(next_shape) * 20
            start_x = info_x + (INFO_WIDTH - piece_width) // 2 - 5
            start_y = 45
            
            preview_surface = pygame.Surface((piece_width + 10, piece_height + 10), pygame.SRCALPHA)
            
            for row in range(len(next_shape)):
                for col in range(len(next_shape[row])):
                    if next_shape[row][col]:
                        bx = 5 + col * 20
                        by = 5 + row * 20
                        
                        for i in range(3, 0, -1):
                            glow_alpha = int(28 * (1 - i/4))
                            glow_size = 18 + i * 4
                            gx = bx + 9 - glow_size // 2
                            gy = by + 9 - glow_size // 2
                            s = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                            pygame.draw.rect(s, (*next_color, glow_alpha), s.get_rect(), border_radius=4)
                            preview_surface.blit(s, (gx, gy))
                        
                        block_rect = pygame.Rect(bx + 1, by + 1, 18, 18)
                        pygame.draw.rect(preview_surface, next_color, block_rect, border_radius=2)
                        pygame.draw.rect(preview_surface, (255, 255, 255, 150), block_rect, 1, border_radius=2)
            
            screen.blit(preview_surface, (start_x, start_y))

        y_offset = 145

        info_items = [
            ("分数", f"{self.score}"),
            ("最高分", f"{self.high_score}"),
            ("等级", f"{self.level}"),
            ("消除行", f"{self.total_lines_cleared}"),
            ("连击", f"x{self.combo_count}" if self.combo_count > 0 else "-")
        ]

        for label, value in info_items:
            label_surf = font_title.render(label, True, (255, 0, 255))
            value_surf = font_text.render(value, True, (0, 255, 127))
            
            if label == "等级":
                level_x = info_x + self.level_shake_offset[0]
                level_y = y_offset + self.level_shake_offset[1]
                screen.blit(label_surf, (level_x, level_y))
                screen.blit(value_surf, (level_x + label_value_gap, level_y + 2))
            else:
                screen.blit(label_surf, (info_x, y_offset))
                screen.blit(value_surf, (info_x + label_value_gap, y_offset + 2))
            y_offset += line_height

        controls_y = SCREEN_HEIGHT - 95
        controls = [
            ("操作说明:", True),
            ("↑ 旋转", False),
            ("← → 移动", False),
            ("↓ 加速", False),
            ("空格 下落", False),
            ("P 暂停", False)
        ]
        
        for i, (control, is_title) in enumerate(controls):
            if is_title:
                ctrl_text = font_text.render(control, True, (255, 255, 0))
            else:
                ctrl_text = font_small.render(control, True, (160, 160, 160))
            screen.blit(ctrl_text, (info_x, controls_y + i * 16))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            font_gameover = pygame.font.Font(FONT_PATH, 36) if FONT_PATH else pygame.font.Font(None, 36)
            text = font_gameover.render("游戏结束", True, (255, 50, 50))
            text_rect = text.get_rect(center=(GRID_WIDTH * BLOCK_SIZE // 2, SCREEN_HEIGHT // 2 - 20))
            
            glow_color = (255, 100, 100)
            for ox in [-2, 2]:
                for oy in [-2, 2]:
                    glow_text = font_gameover.render("游戏结束", True, glow_color)
                    screen.blit(glow_text, (text_rect.x + ox, text_rect.y + oy))
            
            screen.blit(text, text_rect)

            font_restart = pygame.font.Font(FONT_PATH, 18) if FONT_PATH else pygame.font.Font(None, 18)
            text_restart = font_restart.render("按 R 重新开始", True, (255, 255, 255))
            screen.blit(text_restart, (GRID_WIDTH * BLOCK_SIZE // 2 - 50, SCREEN_HEIGHT // 2 + 25))

        if self.paused and not self.game_over:
            overlay = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            
            font_pause = pygame.font.Font(FONT_PATH, 32) if FONT_PATH else pygame.font.Font(None, 32)
            text = font_pause.render("暂停", True, (255, 255, 0))
            text_rect = text.get_rect(center=(GRID_WIDTH * BLOCK_SIZE // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.__init__()
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.move_piece(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_piece(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move_piece(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            while self.move_piece(0, 1):
                                pass
                            self.lock_piece()

            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
