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
    def __init__(self, rows, grid):
        self.rows = list(rows)
        self.timer = 40
        self.max_timer = 40
        self.cleared_blocks = []
        
        for row in self.rows:
            for col in range(GRID_WIDTH):
                if grid[row][col]:
                    self.cleared_blocks.append({
                        'x': col,
                        'y': row,
                        'color': list(grid[row][col])
                    })

    def update(self):
        self.timer -= 1

    def is_alive(self):
        return self.timer > 0

    def draw(self, surface):
        if self.timer <= 0:
            return
            
        progress = 1.0 - (self.timer / self.max_timer)
        
        if progress < 1.0:
            for block in self.cleared_blocks:
                x = block['x'] * BLOCK_SIZE
                y = block['y'] * BLOCK_SIZE
                color = block['color']
                
                flash = math.sin(progress * math.pi * 15) * 0.5 + 0.5
                flash_alpha = int(255 * flash)
                
                glow_size = BLOCK_SIZE + 6
                glow_x = x - 3
                glow_y = y - 3
                
                glow_color = list(color)
                for i in range(3, 0, -1):
                    glow_alpha = int(flash_alpha * 0.12 * (1 - i / 4))
                    glow_rect = pygame.Rect(glow_x - i * 2, glow_y - i * 2, glow_size + i * 4, glow_size + i * 4)
                    s_glow = pygame.Surface((glow_size + i * 4, glow_size + i * 4), pygame.SRCALPHA)
                    pygame.draw.rect(s_glow, (*glow_color, glow_alpha), s_glow.get_rect(), border_radius=6)
                    surface.blit(s_glow, (glow_x - i * 2, glow_y - i * 2))
                
                brightness = int(150 + 105 * flash)
                display_color = tuple(min(255, c + brightness - 150) for c in color)
                
                s = pygame.Surface((BLOCK_SIZE - 4, BLOCK_SIZE - 4), pygame.SRCALPHA)
                pygame.draw.rect(s, (*display_color, flash_alpha), s.get_rect(), border_radius=4)
                surface.blit(s, (x + 2, y + 2))
                
                highlight_color = tuple(min(255, c + 100) for c in color)
                s_highlight = pygame.Surface((BLOCK_SIZE - 8, (BLOCK_SIZE - 8) // 2), pygame.SRCALPHA)
                pygame.draw.rect(s_highlight, (*highlight_color, int(flash_alpha * 0.5)), s_highlight.get_rect(), border_radius=3)
                surface.blit(s_highlight, (x + 4, y + 4))

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
        self.display_combo = 0
        self.display_combo_score = 0
        self.display_combo_x = 0
        self.display_combo_y = 0
        self.display_combo_timer = 0
        self.pending_clear_rows = None
        self.is_clearing = False
        
        self.key_repeat_delay = 80
        self.key_repeat_interval = 15
        self.last_key_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_DOWN: 0}
        self.keys_pressed = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False}

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
            new_shape = [row[:] for row in SHAPES[shape_idx]]
            shape_width = max(len(row) for row in new_shape)
            self.current_piece = {
                'shape': new_shape,
                'color': NEON_COLORS[color_idx],
                'x': (GRID_WIDTH - shape_width) // 2,
                'y': 0,
                'color_idx': color_idx
            }
        else:
            self.current_piece = self.next_piece
            shape_width = max(len(row) for row in self.current_piece['shape'])
            self.current_piece['x'] = (GRID_WIDTH - shape_width) // 2
            self.current_piece['y'] = 0

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

    def get_ghost_position(self):
        if not self.current_piece:
            return None
        shape = self.current_piece['shape']
        x = self.current_piece['x']
        y = self.current_piece['y']
        while not self.check_collision(x, y + 1, shape):
            y += 1
        if y == self.current_piece['y']:
            return None
        return (x, y)

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
            
            if self.combo_count >= 1:
                self.display_combo = self.combo_count - 1
                self.display_combo_x = self.current_piece['x'] + len(shape[0]) // 2
                self.display_combo_y = self.current_piece['y']
                self.display_combo_timer = 60
            
            base_score = cleared ** 2
            combo_multiplier = self.combo_count ** 2
            score_gain = base_score * combo_multiplier * (2 ** (self.level - 1))
            self.score += score_gain
            
            if self.combo_count >= 1:
                self.display_combo_score = (2 ** self.display_combo) * self.level
            
            self.total_lines_cleared += cleared
            self.lines_cleared += cleared

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
            self.pending_clear_rows = cleared_rows
            self.is_clearing = True

        return len(cleared_rows)
    
    def process_pending_clear(self):
        if self.is_clearing and self.pending_clear_rows:
            cleared_rows = self.pending_clear_rows
            
            grid_copy = [row[:] for row in self.grid]
            
            try:
                self.clear_effects.append(ClearEffect(cleared_rows, grid_copy))
            except:
                pass

            new_grid = []
            rows_to_keep = [r for r in range(GRID_HEIGHT) if r not in cleared_rows]
            for row in rows_to_keep:
                new_grid.append(self.grid[row])
            
            while len(new_grid) < GRID_HEIGHT:
                new_grid.insert(0, [0] * GRID_WIDTH)
            
            self.grid = new_grid
            
            self.pending_clear_rows = None
            self.is_clearing = False

    def level_up(self):
        self.level += 1
        self.fall_speed = max(100, 1000 - (self.level - 1) * 100)
        
        self.is_rainbow_flashing = True
        self.rainbow_timer = 60
        self.rainbow_phase = 0
        
        self.screen_shake_timer = 30
        self.level_shake_timer = 30

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

        if self.is_clearing:
            if self.display_combo_timer > 0:
                self.display_combo_timer -= 1
            
            if not self.clear_effects:
                self.process_pending_clear()
            else:
                all_done = all(e.timer <= 0 for e in self.clear_effects)
                if all_done:
                    self.process_pending_clear()
            return

        if self.display_combo_timer > 0:
            self.display_combo_timer -= 1

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
            tuple(min(255, c + 80) for c in color),
            tuple(min(255, c + 30) for c in color),
            color,
            tuple(max(0, c - 30) for c in color),
            tuple(max(0, c - 60) for c in color)
        ]
        
        s = pygame.Surface((BLOCK_SIZE - 4, BLOCK_SIZE - 4), pygame.SRCALPHA)
        
        for i in range(BLOCK_SIZE - 4):
            ratio = i / (BLOCK_SIZE - 4)
            if ratio < 0.25:
                idx = 0
                local_ratio = ratio / 0.25
                interp_color = [
                    gradient_colors[1][c] * (1 - local_ratio) + gradient_colors[0][c] * local_ratio
                    for c in range(3)
                ]
            elif ratio < 0.5:
                idx = 1
                local_ratio = (ratio - 0.25) / 0.25
                interp_color = [
                    gradient_colors[2][c] * (1 - local_ratio) + gradient_colors[1][c] * local_ratio
                    for c in range(3)
                ]
            elif ratio < 0.75:
                idx = 2
                local_ratio = (ratio - 0.5) / 0.25
                interp_color = [
                    gradient_colors[3][c] * (1 - local_ratio) + gradient_colors[2][c] * local_ratio
                    for c in range(3)
                ]
            else:
                idx = 3
                local_ratio = (ratio - 0.75) / 0.25
                interp_color = [
                    gradient_colors[4][c] * (1 - local_ratio) + gradient_colors[3][c] * local_ratio
                    for c in range(3)
                ]
            pygame.draw.line(s, [int(c) for c in interp_color], (i, 0), (i, BLOCK_SIZE - 5))
        
        surface.blit(s, (block_rect.x, block_rect.y))

        highlight = pygame.Rect(x * BLOCK_SIZE + 4, y * BLOCK_SIZE + 4, BLOCK_SIZE - 10, BLOCK_SIZE // 3)
        highlight_s = pygame.Surface((highlight.width, highlight.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_s, (255, 255, 255, 150), highlight_s.get_rect(), border_radius=3)
        surface.blit(highlight_s, (highlight.x, highlight.y))
        
        highlight2 = pygame.Rect(x * BLOCK_SIZE + 6, y * BLOCK_SIZE + 6, 4, BLOCK_SIZE // 4)
        highlight2_s = pygame.Surface((highlight2.width, highlight2.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight2_s, (255, 255, 255, 120), highlight2_s.get_rect(), border_radius=2)
        surface.blit(highlight2_s, (highlight2.x, highlight2.y))

        border_color = tuple(min(255, c + 100) for c in color)
        pygame.draw.rect(surface, border_color, block_rect, 2, border_radius=4)

        reflection = pygame.Rect(x * BLOCK_SIZE + 6, y * BLOCK_SIZE + 6, 4, 4)
        pygame.draw.rect(surface, (255, 255, 255, 180), reflection, border_radius=2)
        
        reflection2 = pygame.Rect(x * BLOCK_SIZE + BLOCK_SIZE - 10, y * BLOCK_SIZE + BLOCK_SIZE - 10, 3, 3)
        pygame.draw.rect(surface, (255, 255, 255, 120), reflection2, border_radius=1)

    def draw_ghost_block(self, surface, x, y, color):
        rect = pygame.Rect(x * BLOCK_SIZE + 2, y * BLOCK_SIZE + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4)
        
        ghost_color = list(color)
        s = pygame.Surface((BLOCK_SIZE - 4, BLOCK_SIZE - 4), pygame.SRCALPHA)
        
        pygame.draw.rect(s, (*ghost_color, 40), s.get_rect(), border_radius=4)
        
        pygame.draw.rect(s, (*ghost_color, 80), s.get_rect(), 2, border_radius=4)
        
        surface.blit(s, (rect.x, rect.y))

    def draw(self):
        if self.is_rainbow_flashing:
            progress = 1.0 - (self.rainbow_timer / 60.0)
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            max_radius = math.sqrt(center_x**2 + center_y**2)
            
            screen.fill((0, 0, 0))
            
            wave_radius = progress * max_radius * 1.3
            
            num_waves = 5
            for w in range(num_waves):
                wave_dist = wave_radius - w * 40
                if wave_dist > 0:
                    wave_intensity = max(0, 1 - w / num_waves) * (1 - progress * 0.4)
                    
                    hue = (progress * 180 + w * 30) % 360
                    neon_color = pygame.Color(0, 0, 0)
                    neon_color.hsva = (int(hue), 100, int(80 * wave_intensity), 100)
                    
                    alpha = int(150 * wave_intensity)
                    
                    pygame.draw.circle(screen, (*neon_color[:3], alpha), 
                                    (center_x, center_y), int(wave_dist), 20)
                    
                    pygame.draw.circle(screen, (*neon_color[:3], int(alpha * 0.5)), 
                                    (center_x, center_y), int(wave_dist - 10), 15)
            
            if progress < 0.5:
                for i in range(3):
                    ring_radius = progress * max_radius * 1.3 * (1 + i * 0.15)
                    ring_alpha = int(100 * (1 - progress * 2) * (1 - i * 0.2))
                    if ring_alpha > 0:
                        pygame.draw.circle(screen, (255, 255, 255, ring_alpha), 
                                        (center_x, center_y), int(ring_radius), 2)
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
                elif self.is_clearing and self.pending_clear_rows and row in self.pending_clear_rows:
                    pass

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

            ghost_pos = self.get_ghost_position()
            if ghost_pos:
                ghost_x, ghost_y = ghost_pos
                for row in range(len(shape)):
                    for col in range(len(shape[row])):
                        if shape[row][col]:
                            self.draw_ghost_block(game_surface,
                                                ghost_x + col,
                                                ghost_y + row,
                                                color)

        self.trail.draw(game_surface)

        for effect in self.clear_effects:
            effect.draw(game_surface)

        screen.blit(game_surface, (offset_x, offset_y))

        for particles in self.particles_list:
            particles.draw(screen)

        if self.display_combo_timer > 0 and self.display_combo >= 1:
            combo_x = self.display_combo_x * BLOCK_SIZE + offset_x
            combo_y = self.display_combo_y * BLOCK_SIZE + offset_y
            
            pulse = math.sin(self.display_combo_timer * 0.3) * 0.3 + 0.7
            alpha = int(self.display_combo_timer / 60.0 * 255)
            
            font_combo = pygame.font.Font(FONT_PATH, 20) if FONT_PATH else pygame.font.Font(None, 20)
            combo_text = f"连击{self.display_combo}"
            combo_surf = font_combo.render(combo_text, True, (255, 200, 0))
            combo_surf.set_alpha(alpha)
            
            score_text = f"+{self.display_combo_score}"
            score_surf = font_text.render(score_text, True, (0, 255, 127))
            score_surf.set_alpha(alpha)
            
            min_x = combo_surf.get_width() // 2 + 5
            max_x = GRID_WIDTH * BLOCK_SIZE - combo_surf.get_width() // 2 - 5
            combo_x = max(min_x, min(max_x, combo_x))
            
            screen.blit(combo_surf, (combo_x - combo_surf.get_width() // 2, combo_y - 30))
            screen.blit(score_surf, (combo_x - score_surf.get_width() // 2, combo_y - 10))

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
            ("消除行", f"{self.total_lines_cleared}")
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
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            
            glow_color = (255, 100, 100)
            for ox in [-2, 2]:
                for oy in [-2, 2]:
                    glow_text = font_gameover.render("游戏结束", True, glow_color)
                    screen.blit(glow_text, (text_rect.x + ox, text_rect.y + oy))
            
            screen.blit(text, text_rect)

            font_restart = pygame.font.Font(FONT_PATH, 18) if FONT_PATH else pygame.font.Font(None, 18)
            text_restart = font_restart.render("按 R 重新开始", True, (255, 255, 255))
            text_restart_rect = text_restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))
            screen.blit(text_restart, text_restart_rect)

        if self.paused and not self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            
            font_pause = pygame.font.Font(FONT_PATH, 32) if FONT_PATH else pygame.font.Font(None, 32)
            text = font_pause.render("暂停", True, (255, 255, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            
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
                            self.keys_pressed[pygame.K_LEFT] = True
                            self.last_key_time[pygame.K_LEFT] = current_time
                            self.move_piece(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.keys_pressed[pygame.K_RIGHT] = True
                            self.last_key_time[pygame.K_RIGHT] = current_time
                            self.move_piece(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.keys_pressed[pygame.K_DOWN] = True
                            self.last_key_time[pygame.K_DOWN] = current_time
                            self.move_piece(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            while self.move_piece(0, 1):
                                pass
                            self.lock_piece()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.keys_pressed[pygame.K_LEFT] = False
                    elif event.key == pygame.K_RIGHT:
                        self.keys_pressed[pygame.K_RIGHT] = False
                    elif event.key == pygame.K_DOWN:
                        self.keys_pressed[pygame.K_DOWN] = False

            if not self.game_over and not self.paused and not self.is_clearing:
                for key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN]:
                    if self.keys_pressed[key]:
                        elapsed = current_time - self.last_key_time[key]
                        if elapsed >= self.key_repeat_delay:
                            repeat_count = (elapsed - self.key_repeat_delay) // self.key_repeat_interval + 1
                            for _ in range(repeat_count):
                                if key == pygame.K_LEFT:
                                    if not self.move_piece(-1, 0):
                                        break
                                elif key == pygame.K_RIGHT:
                                    if not self.move_piece(1, 0):
                                        break
                                elif key == pygame.K_DOWN:
                                    if not self.move_piece(0, 1):
                                        break
                            self.last_key_time[key] = current_time

            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
