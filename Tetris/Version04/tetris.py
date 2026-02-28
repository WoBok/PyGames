"""
Neon Tetris — 霓虹俄罗斯方块
Python + Pygame 实现  |  Version 04
"""

import pygame
import random
import math
import os
import sys
import json
import time as _time

# ──────────────────────────── constants ────────────────────────────

CELL = 32
COLS, ROWS = 10, 20
BUFFER_ROWS = 2
TOTAL_ROWS = ROWS + BUFFER_ROWS

BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL

PANEL_W = 200
MARGIN = 16
LIGHT_BORDER = 10

WIN_W = LIGHT_BORDER + BOARD_W + LIGHT_BORDER + PANEL_W + MARGIN
WIN_H = LIGHT_BORDER + BOARD_H + LIGHT_BORDER

FPS = 60

# ──── colours (R, G, B) ────

BG_COLOR = (10, 10, 30)
GRID_DARK = (20, 20, 50)
GRID_LIGHT = (28, 28, 60)

NEON_COLORS = {
    "I": (0, 240, 240),    # cyan
    "O": (240, 240, 0),    # yellow
    "T": (180, 0, 255),    # purple
    "S": (0, 240, 0),      # green
    "Z": (255, 60, 80),    # pink-red
    "J": (50, 100, 255),   # blue
    "L": (255, 160, 0),    # orange
}

# ──── shapes (row, col offsets from pivot) ────

SHAPES = {
    "I": [[(0, 0), (0, 1), (0, 2), (0, 3)],
          [(0, 0), (1, 0), (2, 0), (3, 0)],
          [(0, 0), (0, 1), (0, 2), (0, 3)],
          [(0, 0), (1, 0), (2, 0), (3, 0)]],
    "O": [[(0, 0), (0, 1), (1, 0), (1, 1)]]*4,
    "T": [[(0, 1), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (1, 0), (1, 1), (2, 0)],
          [(0, 0), (0, 1), (0, 2), (1, 1)],
          [(0, 1), (1, 0), (1, 1), (2, 1)]],
    "S": [[(0, 1), (0, 2), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (1, 1), (2, 1)],
          [(0, 1), (0, 2), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (1, 1), (2, 1)]],
    "Z": [[(0, 0), (0, 1), (1, 1), (1, 2)],
          [(0, 1), (1, 0), (1, 1), (2, 0)],
          [(0, 0), (0, 1), (1, 1), (1, 2)],
          [(0, 1), (1, 0), (1, 1), (2, 0)]],
    "J": [[(0, 0), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (0, 1), (1, 0), (2, 0)],
          [(0, 0), (0, 1), (0, 2), (1, 2)],
          [(0, 1), (1, 1), (2, 0), (2, 1)]],
    "L": [[(0, 2), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (1, 0), (2, 0), (2, 1)],
          [(0, 0), (0, 1), (0, 2), (1, 0)],
          [(0, 0), (0, 1), (1, 1), (2, 1)]],
}

# SRS wall‑kick data (JLSTZ)
KICKS_JLSTZ = {
    (0,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
    (1,0): [(0,0),(1,0),(1,-1),(0,2),(1,2)],
    (1,2): [(0,0),(1,0),(1,-1),(0,2),(1,2)],
    (2,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
    (2,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)],
    (3,2): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
    (3,0): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
    (0,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)],
}

KICKS_I = {
    (0,1): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
    (1,0): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
    (1,2): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)],
    (2,1): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
    (2,3): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
    (3,2): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
    (3,0): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
    (0,3): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)],
}

# ──────────────────────────── helpers ──────────────────────────────

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lerp_color(c1, c2, t):
    t = clamp(t, 0, 1)
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def brighten(color, factor):
    return tuple(clamp(int(c * factor), 0, 255) for c in color)

def save_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "best_score.dat")

def load_best():
    try:
        with open(save_path(), "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_best(score):
    try:
        with open(save_path(), "w") as f:
            f.write(str(score))
    except Exception:
        pass

# ──────────────────────────── Tetromino ────────────────────────────

class Tetromino:
    def __init__(self, shape_key=None):
        if shape_key is None:
            shape_key = random.choice(list(SHAPES.keys()))
        self.key = shape_key
        self.color = NEON_COLORS[shape_key]
        self.rotation = 0
        self.row = 0
        self.col = COLS // 2 - 1
        if shape_key == "I":
            self.row = -1
        elif shape_key == "O":
            self.col = COLS // 2 - 1

    def cells(self, rotation=None, row=None, col=None):
        r = rotation if rotation is not None else self.rotation
        ro = row if row is not None else self.row
        co = col if col is not None else self.col
        return [(ro + dr, co + dc) for dr, dc in SHAPES[self.key][r % 4]]

    def rotate_cw(self):
        return (self.rotation + 1) % 4

    def rotate_ccw(self):
        return (self.rotation + 3) % 4

# ──────────────────────────── Board ───────────────────────────────

class Board:
    def __init__(self):
        self.grid = [[None]*COLS for _ in range(TOTAL_ROWS)]

    def valid(self, cells):
        for r, c in cells:
            if c < 0 or c >= COLS or r >= TOTAL_ROWS:
                return False
            if r >= 0 and self.grid[r][c] is not None:
                return False
        return True

    def lock(self, piece):
        for r, c in piece.cells():
            if 0 <= r < TOTAL_ROWS and 0 <= c < COLS:
                self.grid[r][c] = piece.color

    def clear_lines(self):
        cleared = []
        new_grid = []
        for r in range(TOTAL_ROWS):
            if all(self.grid[r][c] is not None for c in range(COLS)):
                cleared.append(r)
            else:
                new_grid.append(self.grid[r])
        for _ in range(len(cleared)):
            new_grid.insert(0, [None]*COLS)
        self.grid = new_grid
        return cleared

    def ghost_row(self, piece):
        r = piece.row
        while True:
            cells = piece.cells(row=r+1)
            if not self.valid(cells):
                return r
            r += 1

# ──────────────────────────── Particle ────────────────────────────

class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 320)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(60, 180)
        self.color = color
        self.life = 1.0
        self.decay = random.uniform(0.6, 1.4)
        self.size = random.uniform(2, 5)
        self.trail = []

    def update(self, dt):
        self.trail.append((self.x, self.y, self.life))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.vy += 400 * dt   # gravity
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= self.decay * dt
        return self.life > 0

    def draw(self, surf, ox, oy):
        for tx, ty, tl in self.trail:
            a = int(tl * 80)
            if a > 0:
                pygame.draw.circle(surf, (*self.color, ), (int(tx+ox), int(ty+oy)), max(1, int(self.size*tl*0.5)))
        a = clamp(int(self.life * 255), 0, 255)
        if a > 0:
            pygame.draw.circle(surf, self.color, (int(self.x+ox), int(self.y+oy)), max(1, int(self.size*self.life)))

# ──────────────────────────── FloatingText ────────────────────────

class FloatingText:
    def __init__(self, text, x, y, color, size=26):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0
        self.size = size
        self.vy = -80

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= 0.7 * dt
        return self.life > 0

    def draw(self, surf, font_cache):
        a = clamp(int(self.life * 255), 0, 255)
        if a <= 0:
            return
        sz = max(12, int(self.size * (0.8 + 0.2 * self.life)))
        if sz not in font_cache:
            font_cache[sz] = pygame.font.SysFont("consolas", sz, bold=True)
        f = font_cache[sz]
        ts = f.render(self.text, True, self.color)
        ts.set_alpha(a)
        surf.blit(ts, (self.x - ts.get_width()//2, int(self.y)))

# ──────────────────────────── Effects ─────────────────────────────

class EffectsManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self.line_flash_rows = []
        self.line_flash_timer = 0
        self.scan_y = -1
        self.scan_timer = 0
        self.glow_rings = []
        self.rainbow_timer = 0
        self.shake_timer = 0
        self.shake_amp = 0
        self.level_jitter_timer = 0

    def spawn_line_clear(self, rows, board_offset_x, board_offset_y, colors_grid):
        self.line_flash_rows = rows
        self.line_flash_timer = 0.35
        if len(rows) >= 2:
            mid_y = sum(r * CELL + CELL//2 for r in rows) / len(rows)
            self.glow_rings.append([board_offset_x + BOARD_W//2, board_offset_y + mid_y, 0, 0.6])
        self.scan_y = min(rows) * CELL
        self.scan_timer = 0.4
        # particles
        for r in rows:
            for c in range(COLS):
                color = colors_grid[r][c] if colors_grid[r][c] else (200, 200, 255)
                cx = board_offset_x + c * CELL + CELL // 2
                cy = board_offset_y + (r - BUFFER_ROWS) * CELL + CELL // 2
                count = 4 + len(rows) * 3
                for _ in range(count):
                    self.particles.append(Particle(cx, cy, color))

    def spawn_floating_text(self, text, x, y, color):
        self.floating_texts.append(FloatingText(text, x, y, color))

    def trigger_level_up(self):
        self.rainbow_timer = 2.0
        self.shake_timer = 1.0
        self.shake_amp = 8
        self.level_jitter_timer = 1.5

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [t for t in self.floating_texts if t.update(dt)]
        if self.line_flash_timer > 0:
            self.line_flash_timer -= dt
        if self.scan_timer > 0:
            self.scan_timer -= dt
        new_rings = []
        for ring in self.glow_rings:
            ring[2] += 300 * dt  # expand radius
            ring[3] -= dt        # fade
            if ring[3] > 0:
                new_rings.append(ring)
        self.glow_rings = new_rings
        if self.rainbow_timer > 0:
            self.rainbow_timer -= dt
        if self.shake_timer > 0:
            self.shake_timer -= dt
        if self.level_jitter_timer > 0:
            self.level_jitter_timer -= dt

    def get_shake_offset(self):
        if self.shake_timer > 0:
            amp = self.shake_amp * (self.shake_timer / 1.0)
            return random.uniform(-amp, amp), random.uniform(-amp, amp)
        return 0, 0

    def draw_line_flash(self, surf, ox, oy):
        if self.line_flash_timer > 0 and self.line_flash_rows:
            progress = 1 - self.line_flash_timer / 0.35
            flash_x = int(progress * BOARD_W)
            for r in self.line_flash_rows:
                y = oy + (r - BUFFER_ROWS) * CELL
                flash_surf = pygame.Surface((flash_x, CELL), pygame.SRCALPHA)
                alpha = int(200 * (1 - progress))
                flash_surf.fill((255, 255, 255, alpha))
                surf.blit(flash_surf, (ox, y))

    def draw_scan_line(self, surf, ox, oy):
        if self.scan_timer > 0:
            progress = 1 - self.scan_timer / 0.4
            y = oy + (self.scan_y - BUFFER_ROWS * CELL) - int(progress * BOARD_H * 0.3)
            scan_surf = pygame.Surface((BOARD_W, 3), pygame.SRCALPHA)
            a = int(150 * (1 - progress))
            scan_surf.fill((0, 255, 255, a))
            surf.blit(scan_surf, (ox, y))

    def draw_glow_rings(self, surf):
        for ring in self.glow_rings:
            x, y, radius, life = ring
            a = int(life * 120)
            if a > 0 and radius > 0:
                pygame.draw.circle(surf, (255, 255, 255), (int(x), int(y)), int(radius), 2)

    def draw_rainbow(self, surf):
        if self.rainbow_timer > 0:
            hue = (pygame.time.get_ticks() * 0.3) % 360
            color = pygame.Color(0)
            color.hsla = (hue, 80, 60, 0)
            a = int(60 * min(1, self.rainbow_timer / 0.5))
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            overlay.fill((*color[:3], a))
            surf.blit(overlay, (0, 0))

    def draw_particles(self, surf, ox, oy):
        for p in self.particles:
            p.draw(surf, ox, oy)

    def draw_floating(self, surf, font_cache):
        for t in self.floating_texts:
            t.draw(surf, font_cache)

# ──────────────────────────── Renderer ────────────────────────────

class NeonRenderer:
    """Draws neon-glass style blocks and other visual elements."""

    @staticmethod
    def draw_block(surf, x, y, color, t_ms, alpha_override=None):
        """Draw a single neon block at pixel position (x, y)."""
        # breathing brightness
        breath = 1.0 + 0.10 * math.sin(t_ms * 0.003)
        c = brighten(color, breath)

        s = CELL
        # outer glow
        glow_s = pygame.Surface((s+8, s+8), pygame.SRCALPHA)
        ga = alpha_override if alpha_override else 40
        pygame.draw.rect(glow_s, (*c, ga), (0, 0, s+8, s+8), border_radius=4)
        surf.blit(glow_s, (x-4, y-4))

        # glass fill
        fill_a = alpha_override if alpha_override else 110
        fill_s = pygame.Surface((s, s), pygame.SRCALPHA)
        fill_s.fill((*c, fill_a))
        surf.blit(fill_s, (x, y))

        # top highlight
        hl = pygame.Surface((s-4, 3), pygame.SRCALPHA)
        hl.fill((255, 255, 255, alpha_override or 90))
        surf.blit(hl, (x+2, y+2))

        # left highlight
        lh = pygame.Surface((3, s-4), pygame.SRCALPHA)
        lh.fill((255, 255, 255, alpha_override or 50))
        surf.blit(lh, (x+2, y+2))

        # shadow bottom‑right
        sh = pygame.Surface((s-2, 3), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 60))
        surf.blit(sh, (x+1, y+s-4))
        sv = pygame.Surface((3, s-2), pygame.SRCALPHA)
        sv.fill((0, 0, 0, 60))
        surf.blit(sv, (x+s-4, y+1))

        # neon border
        ba = alpha_override if alpha_override else 220
        border_c = brighten(c, 1.3)
        pygame.draw.rect(surf, (*border_c[:3],), (x, y, s, s), 2, border_radius=2)

    @staticmethod
    def draw_ghost_block(surf, x, y, color):
        s = CELL
        gs = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*color, 40), (0, 0, s, s))
        pygame.draw.rect(gs, (*color, 90), (0, 0, s, s), 2, border_radius=2)
        surf.blit(gs, (x, y))

# ──────────────────────────── Stars BG ────────────────────────────

class StarField:
    def __init__(self, count=80):
        self.stars = []
        for _ in range(count):
            self.stars.append({
                "x": random.randint(0, WIN_W),
                "y": random.randint(0, WIN_H),
                "size": random.uniform(0.5, 2.5),
                "phase": random.uniform(0, math.pi*2),
                "speed": random.uniform(0.5, 2.0),
            })

    def draw(self, surf, t_ms):
        for s in self.stars:
            brightness = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t_ms * 0.001 * s["speed"] + s["phase"]))
            c = int(brightness * 255)
            pygame.draw.circle(surf, (c, c, clamp(c + 30, 0, 255)),
                               (s["x"], s["y"]), max(1, int(s["size"] * brightness)))

# ──────────────────────────── Light Bulbs ─────────────────────────

class LightBulbs:
    def __init__(self, rect):
        self.bulbs = []
        spacing = 18
        x0, y0, w, h = rect
        # top
        for i in range(0, w, spacing):
            self.bulbs.append((x0+i, y0, random.uniform(0, math.pi*2), self._rand_color()))
        # bottom
        for i in range(0, w, spacing):
            self.bulbs.append((x0+i, y0+h, random.uniform(0, math.pi*2), self._rand_color()))
        # left
        for i in range(spacing, h, spacing):
            self.bulbs.append((x0, y0+i, random.uniform(0, math.pi*2), self._rand_color()))
        # right
        for i in range(spacing, h, spacing):
            self.bulbs.append((x0+w, y0+i, random.uniform(0, math.pi*2), self._rand_color()))

    @staticmethod
    def _rand_color():
        return random.choice([(255,80,80),(80,255,80),(80,80,255),(255,255,80),(255,80,255),(80,255,255),(255,160,80)])

    def draw(self, surf, t_ms):
        for bx, by, phase, color in self.bulbs:
            brightness = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t_ms * 0.004 + phase))
            c = brighten(color, brightness)
            r = int(3 + 2 * brightness)
            # glow
            gs = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*c, int(50*brightness)), (r*2, r*2), r*2)
            surf.blit(gs, (bx-r*2, by-r*2))
            pygame.draw.circle(surf, c, (bx, by), r)

class SeparatorBulbs:
    def __init__(self, x, y, w):
        self.bulbs = []
        spacing = 14
        for i in range(0, w, spacing):
            self.bulbs.append((x+i, y, random.uniform(0, math.pi*2), LightBulbs._rand_color()))

    def draw(self, surf, t_ms):
        for bx, by, phase, color in self.bulbs:
            brightness = 0.5 + 0.5 * (0.5 + 0.5 * math.sin(t_ms * 0.005 + phase))
            c = brighten(color, brightness)
            pygame.draw.circle(surf, c, (bx, by), 3)

# ──────────────────────────── Trail ───────────────────────────────

class TrailManager:
    def __init__(self):
        self.trails = []  # list of (cells, color, life)

    def add(self, cells, color):
        self.trails.append((list(cells), color, 1.0))

    def update(self, dt):
        new = []
        for cells, color, life in self.trails:
            life -= dt * 4
            if life > 0:
                new.append((cells, color, life))
        self.trails = new

    def draw(self, surf, ox, oy, t_ms):
        for cells, color, life in self.trails:
            a = int(life * 50)
            if a <= 0:
                continue
            for r, c in cells:
                y = oy + (r - BUFFER_ROWS) * CELL
                x = ox + c * CELL
                if y < oy - CELL or y > oy + BOARD_H:
                    continue
                NeonRenderer.draw_block(surf, x, y, color, t_ms, alpha_override=a)

# ──────────────────────────── Game ────────────────────────────────

class Game:
    STATE_START = 0
    STATE_PLAYING = 1
    STATE_GAMEOVER = 2

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Neon Tetris ✦")
        self.clock = pygame.time.Clock()

        # fonts
        self.font_cache = {}
        self.font_title = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_label = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_value = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_big = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 14)
        self.font_help = pygame.font.SysFont("consolas", 15)
        self.font_huge = pygame.font.SysFont("consolas", 48, bold=True)

        # board origin (inside light border)
        self.board_ox = LIGHT_BORDER
        self.board_oy = LIGHT_BORDER

        # decoration
        self.stars = StarField(80)
        self.bulbs = LightBulbs((self.board_ox - 5, self.board_oy - 5, BOARD_W + 10, BOARD_H + 10))
        panel_x = self.board_ox + BOARD_W + LIGHT_BORDER
        self.sep_bulbs = SeparatorBulbs(panel_x + 10, self.board_oy + 65, PANEL_W - 20)

        # game state
        self.state = Game.STATE_START
        self.show_help = False
        self.best_score = load_best()
        self.reset_game()

    def reset_game(self):
        self.board = Board()
        self.effects = EffectsManager()
        self.trail = TrailManager()
        self.bag = []
        self.current = self._next_piece()
        self.next_piece = self._next_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.drop_interval = 1.0
        self.drop_timer = 0
        self.lock_delay = 0
        self.lock_delay_max = 0.5
        # DAS (delayed auto shift)
        self.das_dir = 0   # -1 left, 1 right, 2 down
        self.das_timer = 0
        self.das_delay = 0.17
        self.das_repeat = 0.05
        self.das_charged = False
        self.prev_cells = None

    def _next_piece(self):
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
        return Tetromino(self.bag.pop())

    def _try_move(self, piece, dr, dc):
        cells = piece.cells(row=piece.row+dr, col=piece.col+dc)
        if self.board.valid(cells):
            # record trail before move
            if dr != 0 or dc != 0:
                self.trail.add(piece.cells(), piece.color)
            piece.row += dr
            piece.col += dc
            return True
        return False

    def _try_rotate(self, piece):
        new_rot = piece.rotate_cw()
        kicks = KICKS_I if piece.key == "I" else KICKS_JLSTZ
        key = (piece.rotation, new_rot)
        if key not in kicks:
            return False
        for dc, dr in kicks[key]:
            cells = piece.cells(rotation=new_rot, row=piece.row - dr, col=piece.col + dc)
            if self.board.valid(cells):
                self.trail.add(piece.cells(), piece.color)
                piece.rotation = new_rot
                piece.row -= dr
                piece.col += dc
                return True
        return False

    def _hard_drop(self):
        ghost_r = self.board.ghost_row(self.current)
        if ghost_r != self.current.row:
            self.trail.add(self.current.cells(), self.current.color)
        self.current.row = ghost_r
        self._lock_piece()

    def _lock_piece(self):
        self.board.lock(self.current)
        # save colors before clearing
        colors_snap = [row[:] for row in self.board.grid]
        cleared = self.board.clear_lines()
        if cleared:
            self.combo += 1
            # scoring
            n = len(cleared)
            multiplier = 2 ** (self.level - 1)
            line_score = n * n * multiplier
            combo_bonus = 0
            if self.combo > 1:
                combo_bonus = (2 ** (self.combo - 1)) * (self.level ** 2)
            total = line_score + combo_bonus
            self.score += total
            self.lines += n

            # effects
            ox = self.board_ox
            oy = self.board_oy
            self.effects.spawn_line_clear(cleared, ox, oy, colors_snap)
            mid_r = sum(cleared) / len(cleared)
            fx = ox + BOARD_W // 2
            fy = oy + (mid_r - BUFFER_ROWS) * CELL
            self.effects.spawn_floating_text(f"+{line_score}", fx, fy, (255, 255, 100))
            if self.combo > 1:
                self.effects.spawn_floating_text(
                    f"COMBO x{self.combo}! +{combo_bonus}", fx, fy - 30, (0, 255, 255))
            if n == 4:
                self.effects.spawn_floating_text("TETRIS!", fx, fy - 60, (255, 50, 255), size=32)

            # level up
            new_level = self.lines // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.drop_interval = max(0.08, 1.0 - (self.level - 1) * 0.08)
                self.effects.trigger_level_up()
        else:
            self.combo = 0

        # best score
        if self.score > self.best_score:
            self.best_score = self.score
            save_best(self.best_score)

        # spawn next
        self.current = self.next_piece
        self.next_piece = self._next_piece()
        self.drop_timer = 0
        self.lock_delay = 0
        # check game over
        if not self.board.valid(self.current.cells()):
            self.state = Game.STATE_GAMEOVER

    def _update_playing(self, dt):
        self.drop_timer += dt
        # DAS handling
        if self.das_dir != 0:
            self.das_timer += dt
            if not self.das_charged:
                if self.das_timer >= self.das_delay:
                    self.das_charged = True
                    self.das_timer = 0
                    if self.das_dir == 2:
                        self._try_move(self.current, 1, 0)
                    else:
                        self._try_move(self.current, 0, self.das_dir)
            else:
                while self.das_timer >= self.das_repeat:
                    self.das_timer -= self.das_repeat
                    if self.das_dir == 2:
                        self._try_move(self.current, 1, 0)
                    else:
                        self._try_move(self.current, 0, self.das_dir)

        # auto drop
        interval = self.drop_interval
        if self.das_dir == 2:
            interval = min(interval, 0.05)
        if self.drop_timer >= interval:
            self.drop_timer -= interval
            if not self._try_move(self.current, 1, 0):
                self.lock_delay += interval
                if self.lock_delay >= self.lock_delay_max:
                    self._lock_piece()
            else:
                self.lock_delay = 0

        # check if on ground for lock delay
        ground_cells = self.current.cells(row=self.current.row + 1)
        if not self.board.valid(ground_cells):
            self.lock_delay += dt
            if self.lock_delay >= self.lock_delay_max:
                self._lock_piece()

    def _handle_event_playing(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._try_move(self.current, 0, -1)
                self.das_dir = -1
                self.das_timer = 0
                self.das_charged = False
            elif event.key == pygame.K_RIGHT:
                self._try_move(self.current, 0, 1)
                self.das_dir = 1
                self.das_timer = 0
                self.das_charged = False
            elif event.key == pygame.K_DOWN:
                self._try_move(self.current, 1, 0)
                self.das_dir = 2
                self.das_timer = 0
                self.das_charged = False
            elif event.key == pygame.K_UP:
                self._try_rotate(self.current)
                self.lock_delay = 0  # reset lock delay on rotate
            elif event.key == pygame.K_SPACE:
                self._hard_drop()
            elif event.key == pygame.K_r:
                self.reset_game()
                self.state = Game.STATE_PLAYING
            elif event.key == pygame.K_h:
                self.show_help = not self.show_help
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and self.das_dir == -1:
                self.das_dir = 0
            elif event.key == pygame.K_RIGHT and self.das_dir == 1:
                self.das_dir = 0
            elif event.key == pygame.K_DOWN and self.das_dir == 2:
                self.das_dir = 0

    # ──── draw methods ────

    def _draw_board_bg(self, surf, ox, oy):
        """Checkerboard background on game area."""
        for r in range(ROWS):
            for c in range(COLS):
                x = ox + c * CELL
                y = oy + r * CELL
                color = GRID_DARK if (r + c) % 2 == 0 else GRID_LIGHT
                pygame.draw.rect(surf, color, (x, y, CELL, CELL))

    def _draw_board(self, surf, ox, oy, t_ms):
        """Draw locked blocks on the board."""
        for r in range(BUFFER_ROWS, TOTAL_ROWS):
            for c in range(COLS):
                color = self.board.grid[r][c]
                if color:
                    x = ox + c * CELL
                    y = oy + (r - BUFFER_ROWS) * CELL
                    NeonRenderer.draw_block(surf, x, y, color, t_ms)

    def _draw_piece(self, surf, piece, ox, oy, t_ms):
        for r, c in piece.cells():
            y = oy + (r - BUFFER_ROWS) * CELL
            x = ox + c * CELL
            if y >= oy - CELL:
                NeonRenderer.draw_block(surf, x, y, piece.color, t_ms)

    def _draw_ghost(self, surf, piece, ox, oy):
        ghost_r = self.board.ghost_row(piece)
        cells = piece.cells(row=ghost_r)
        for r, c in cells:
            y = oy + (r - BUFFER_ROWS) * CELL
            x = ox + c * CELL
            if y >= oy:
                NeonRenderer.draw_ghost_block(surf, x, y, piece.color)

    def _draw_panel(self, surf, t_ms):
        px = self.board_ox + BOARD_W + LIGHT_BORDER
        py = self.board_oy

        # gradient background
        for i in range(BOARD_H):
            t = i / BOARD_H
            c = lerp_color((15, 15, 45), (25, 20, 55), t)
            pygame.draw.line(surf, c, (px, py + i), (px + PANEL_W, py + i))

        # dynamic scan line on panel
        scan_pos = int((t_ms * 0.05) % BOARD_H)
        scan_s = pygame.Surface((PANEL_W, 2), pygame.SRCALPHA)
        scan_s.fill((0, 255, 255, 30))
        surf.blit(scan_s, (px, py + scan_pos))

        # flowing neon glow on left border
        for i in range(BOARD_H):
            hue_shift = (i * 2 + t_ms * 0.1) % 360
            pc = pygame.Color(0)
            pc.hsla = (hue_shift, 80, 50, 0)
            brightness = 0.5 + 0.5 * math.sin((i * 0.05 + t_ms * 0.003))
            a = int(brightness * 100)
            gs = pygame.Surface((6, 1), pygame.SRCALPHA)
            gs.fill((*pc[:3], a))
            surf.blit(gs, (px - 3, py + i))

        # TETRIS title
        title_surf = self.font_title.render("TETRIS", True, (255, 0, 255))
        tx = px + (PANEL_W - title_surf.get_width()) // 2
        # glow behind title
        glow = self.font_title.render("TETRIS", True, (255, 100, 255))
        glow.set_alpha(50 + int(30 * math.sin(t_ms * 0.002)))
        surf.blit(glow, (tx - 2, py + 18))
        surf.blit(title_surf, (tx, py + 20))

        # separator bulbs
        self.sep_bulbs.draw(surf, t_ms)

        # next piece
        label_y = py + 80
        lbl = self.font_label.render("NEXT", True, (150, 150, 200))
        surf.blit(lbl, (px + 15, label_y))
        # draw next piece preview
        if self.next_piece:
            cells = self.next_piece.cells(rotation=0, row=0, col=0)
            min_c = min(c for _, c in cells)
            max_c = max(c for _, c in cells)
            min_r = min(r for r, _ in cells)
            max_r = max(r for r, _ in cells)
            pw = (max_c - min_c + 1) * CELL
            ph = (max_r - min_r + 1) * CELL
            start_x = px + (PANEL_W - pw) // 2
            start_y = label_y + 25
            for r, c in cells:
                bx = start_x + (c - min_c) * CELL
                by = start_y + (r - min_r) * CELL
                NeonRenderer.draw_block(surf, bx, by, self.next_piece.color, t_ms)

        # stats
        stats_y = label_y + 110
        stats = [
            ("BEST", str(self.best_score), (255, 215, 0)),
            ("SCORE", str(self.score), (0, 255, 200)),
            ("LINES", str(self.lines), (0, 200, 255)),
            ("LEVEL", str(self.level), (255, 100, 255)),
        ]
        for i, (label, value, color) in enumerate(stats):
            ly = stats_y + i * 70
            lbl = self.font_label.render(label, True, (150, 150, 200))
            surf.blit(lbl, (px + 15, ly))
            # best score larger
            if label == "BEST":
                vs = self.font_big.render(value, True, color)
            else:
                vs = self.font_value.render(value, True, color)
            # level jitter
            jx, jy = 0, 0
            if label == "LEVEL" and self.effects.level_jitter_timer > 0:
                jx = random.uniform(-3, 3)
                jy = random.uniform(-3, 3)
            surf.blit(vs, (px + 15 + jx, ly + 20 + jy))

        # help hint at bottom
        help_y = py + BOARD_H - 30
        hint = self.font_small.render("Press H for help", True, (100, 100, 150))
        surf.blit(hint, (px + 15, help_y))

    def _draw_start_screen(self, surf, t_ms):
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        cx = WIN_W // 2
        # title
        title = self.font_huge.render("NEON TETRIS", True, (255, 0, 255))
        # glow
        glow = self.font_huge.render("NEON TETRIS", True, (255, 100, 255))
        glow.set_alpha(40 + int(30 * math.sin(t_ms * 0.002)))
        surf.blit(glow, (cx - title.get_width()//2 - 2, 68))
        surf.blit(title, (cx - title.get_width()//2, 70))

        # controls
        lines = [
            "─── Controls ───",
            "← →    Move left / right",
            "↑      Rotate",
            "↓      Soft drop",
            "SPACE  Hard drop",
            "R      Restart",
            "H      Help",
            "",
            "─── Scoring ───",
            "Lines² × 2^(Level-1)",
            "Combo: 2^(Combo-1) × Level²",
            "Every 10 lines = next level",
            "",
            "",
            "Press SPACE to start",
        ]
        for i, line in enumerate(lines):
            if line.startswith("───"):
                c = (0, 255, 255)
                f = self.font_big
            elif line.startswith("Press"):
                pulse = 0.5 + 0.5 * math.sin(t_ms * 0.004)
                c = lerp_color((100, 100, 100), (255, 255, 0), pulse)
                f = self.font_big
            else:
                c = (200, 200, 220)
                f = self.font_help
            ts = f.render(line, True, c)
            surf.blit(ts, (cx - ts.get_width()//2, 140 + i * 28))

    def _draw_gameover(self, surf, t_ms):
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        cx = WIN_W // 2
        go = self.font_huge.render("GAME OVER", True, (255, 50, 50))
        surf.blit(go, (cx - go.get_width()//2, 180))

        score_text = self.font_big.render(f"Score: {self.score}", True, (0, 255, 200))
        surf.blit(score_text, (cx - score_text.get_width()//2, 260))

        best_text = self.font_big.render(f"Best: {self.best_score}", True, (255, 215, 0))
        surf.blit(best_text, (cx - best_text.get_width()//2, 300))

        lines_text = self.font_value.render(f"Lines: {self.lines}  Level: {self.level}", True, (200, 200, 220))
        surf.blit(lines_text, (cx - lines_text.get_width()//2, 350))

        pulse = 0.5 + 0.5 * math.sin(t_ms * 0.004)
        c = lerp_color((100, 100, 100), (255, 255, 0), pulse)
        restart = self.font_big.render("Press R to restart", True, c)
        surf.blit(restart, (cx - restart.get_width()//2, 420))

    def _draw_help(self, surf, t_ms):
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))

        cx = WIN_W // 2
        title = self.font_big.render("─── HELP ───", True, (0, 255, 255))
        surf.blit(title, (cx - title.get_width()//2, 60))

        lines = [
            "Controls:",
            "  ← →     Move left / right (hold to auto-repeat)",
            "  ↑       Rotate clockwise",
            "  ↓       Soft drop (hold to speed up)",
            "  SPACE   Hard drop to bottom",
            "  R       Restart game",
            "  H       Close this help",
            "",
            "Scoring:",
            f"  Line Score = Lines² × 2^(Level-1)",
            f"  1 line = 1pt, 2 = 4pt, 3 = 9pt, 4 = 16pt (×multiplier)",
            "",
            "  Combo bonus = 2^(Combo-1) × Level²",
            "  Consecutive clears earn increasing combo bonuses",
            "",
            "Levels:",
            "  Every 10 lines cleared = Level Up",
            "  Speed increases each level",
            "  Max speed at ~Level 12",
            "",
            "Game Over:",
            "  When new piece can't spawn at the top",
            "  Best score is saved automatically",
            "",
            "Press H to close",
        ]
        for i, line in enumerate(lines):
            if line.endswith(":") and not line.startswith(" "):
                c = (255, 200, 100)
                f = self.font_value
            elif line == "Press H to close":
                pulse = 0.5 + 0.5 * math.sin(t_ms * 0.004)
                c = lerp_color((100, 100, 100), (255, 255, 0), pulse)
                f = self.font_value
            else:
                c = (200, 200, 220)
                f = self.font_help
            ts = f.render(line, True, c)
            surf.blit(ts, (cx - ts.get_width()//2, 100 + i * 22))

    # ──── main loop ────

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # cap delta
            t_ms = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.state == Game.STATE_START:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.state = Game.STATE_PLAYING
                        elif event.key == pygame.K_h:
                            self.show_help = not self.show_help
                elif self.state == Game.STATE_PLAYING:
                    if not self.show_help:
                        self._handle_event_playing(event)
                    else:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                            self.show_help = False
                elif self.state == Game.STATE_GAMEOVER:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.state = Game.STATE_PLAYING

            # update
            if self.state == Game.STATE_PLAYING and not self.show_help:
                self._update_playing(dt)
            self.effects.update(dt)
            self.trail.update(dt)

            # draw
            sx, sy = self.effects.get_shake_offset()
            ox = self.board_ox + int(sx)
            oy = self.board_oy + int(sy)

            self.screen.fill(BG_COLOR)
            self.stars.draw(self.screen, t_ms)

            # board background
            self._draw_board_bg(self.screen, ox, oy)

            # ghost piece
            if self.state == Game.STATE_PLAYING:
                self._draw_ghost(self.screen, self.current, ox, oy)

            # trails
            self.trail.draw(self.screen, ox, oy, t_ms)

            # locked blocks
            self._draw_board(self.screen, ox, oy, t_ms)

            # current piece
            if self.state == Game.STATE_PLAYING:
                self._draw_piece(self.screen, self.current, ox, oy, t_ms)

            # effects
            self.effects.draw_line_flash(self.screen, ox, oy)
            self.effects.draw_scan_line(self.screen, ox, oy)
            self.effects.draw_glow_rings(self.screen)
            self.effects.draw_particles(self.screen, 0, 0)
            self.effects.draw_floating(self.screen, self.font_cache)
            self.effects.draw_rainbow(self.screen)

            # light bulbs border
            self.bulbs.draw(self.screen, t_ms)

            # right panel
            self._draw_panel(self.screen, t_ms)

            # overlays
            if self.state == Game.STATE_START:
                self._draw_start_screen(self.screen, t_ms)
            elif self.state == Game.STATE_GAMEOVER:
                self._draw_gameover(self.screen, t_ms)
            if self.show_help:
                self._draw_help(self.screen, t_ms)

            pygame.display.flip()

        pygame.quit()

# ──────────────────────────── entry point ─────────────────────────

if __name__ == "__main__":
    Game().run()
