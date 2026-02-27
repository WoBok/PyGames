import pygame
import random
import math
import time

pygame.init()

CELL = 32
COLS, ROWS = 10, 20
BOARD_W, BOARD_H = COLS * CELL, ROWS * CELL
PANEL_W = 240
W, H = BOARD_W + PANEL_W, BOARD_H
FPS = 60

BG = (3, 3, 15)

NEON_COLORS = [
    (255, 0, 128),
    (0, 255, 255),
    (255, 220, 0),
    (0, 255, 128),
    (255, 100, 0),
    (180, 0, 255),
    (0, 140, 255),
]

SHAPES = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[0,1,0],[1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
    [[1,1,0],[0,1,1]],
    [[0,1,1],[1,1,0]],
]

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("NEON TETRIS")
clock = pygame.time.Clock()

def _make_fonts():
    # Try CJK-capable fonts for Chinese text support
    for name in ("Microsoft YaHei", "SimHei", "NSimSun", "Arial Unicode MS", "Arial"):
        try:
            f = pygame.font.SysFont(name, 36, bold=True)
            if f.render("测", True, (255,255,255)).get_width() > 5:
                return (
                    pygame.font.SysFont(name, 36, bold=True),
                    pygame.font.SysFont(name, 28, bold=True),
                    pygame.font.SysFont(name, 20, bold=True),
                    pygame.font.SysFont(name, 13),
                )
        except:
            pass
    return (pygame.font.Font(None, 40), pygame.font.Font(None, 32),
            pygame.font.Font(None, 24), pygame.font.Font(None, 17))

font_xl, font_lg, font_md, font_sm = _make_fonts()


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


def neon_color(color, t=0):
    factor = 0.90 + 0.10 * math.sin(t * 3)
    return tuple(min(255, int(c * factor)) for c in color)


def draw_neon_cell(surface, x, y, color, alpha=255, glow=True, size=CELL):
    # Outer glow layers
    if glow and alpha > 60:
        for radius, a in [(size + 16, 18), (size + 10, 35), (size + 4, 55)]:
            gs = pygame.Surface((radius, radius), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*color, int(a * alpha / 255)), (0, 0, radius, radius), border_radius=6)
            surface.blit(gs, (x - (radius - size) // 2, y - (radius - size) // 2))

    cs = size - 2
    cell = pygame.Surface((cs, cs), pygame.SRCALPHA)

    # Glass base: semi-transparent fill
    base_alpha = int(alpha * 0.6)
    cell.fill((*color, base_alpha))

    # Darker bottom-right shadow for depth
    shadow = pygame.Surface((cs, cs), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, int(alpha * 0.4)),
                        [(cs, 0), (cs, cs), (0, cs)])
    cell.blit(shadow, (0, 0))

    # Top highlight strip (glass reflection)
    hl = pygame.Surface((cs - 4, cs // 3), pygame.SRCALPHA)
    hl.fill((255, 255, 255, int(alpha * 0.55)))
    cell.blit(hl, (2, 2))

    # Diagonal shine spot (top-left corner)
    shine_s = pygame.Surface((cs // 3, cs // 3), pygame.SRCALPHA)
    shine_s.fill((255, 255, 255, int(alpha * 0.35)))
    cell.blit(shine_s, (2, 2))

    # Left edge highlight
    le = pygame.Surface((3, cs - 4), pygame.SRCALPHA)
    le.fill((255, 255, 255, int(alpha * 0.35)))
    cell.blit(le, (2, 2))

    # Bottom-right dark edge for 3D bevel
    br = pygame.Surface((cs, 3), pygame.SRCALPHA)
    br.fill((0, 0, 0, int(alpha * 0.5)))
    cell.blit(br, (0, cs - 3))
    br2 = pygame.Surface((3, cs), pygame.SRCALPHA)
    br2.fill((0, 0, 0, int(alpha * 0.5)))
    cell.blit(br2, (cs - 3, 0))

    # Bright neon border (outer)
    border_color = tuple(min(255, c + 120) for c in color)
    pygame.draw.rect(cell, (*border_color, min(255, alpha)), (0, 0, cs, cs), 2)
    # Inner border subtle
    pygame.draw.rect(cell, (*color, min(255, int(alpha * 0.5))), (2, 2, cs - 4, cs - 4), 1)

    surface.blit(cell, (x + 1, y + 1))


def neon_text(surface, text, font, color, x, y, glow_radius=2, glow_layers=2, t=0):
    # Medium edge glow (no breathing/flicker)
    for radius, base_a in [(4, 25), (2, 50)]:
        gs = font.render(text, True, color)
        gs.set_alpha(base_a)
        for dx in range(-radius, radius + 1, max(1, radius // 2)):
            for dy in range(-radius, radius + 1, max(1, radius // 2)):
                if dx != 0 or dy != 0:
                    surface.blit(gs, (x + dx, y + dy))
    # Edge highlight (bright outline)
    ec = tuple(min(255, c + 100) for c in color)
    es = font.render(text, True, ec)
    es.set_alpha(180)
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        surface.blit(es, (x + dx, y + dy))
    # Core
    s = font.render(text, True, color)
    surface.blit(s, (x, y))


class Particle:
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-8, 8)
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(2, 7) * speed_mult
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd - random.uniform(1, 4)
        self.color = color
        self.life = 1.0
        self.decay = random.uniform(0.018, 0.035)
        self.size = random.randint(2, 7)
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.vx *= 0.98
        self.life -= self.decay
        return self.life > 0

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            ta = int(self.life * 255 * (i + 1) / len(self.trail) * 0.4)
            ts = max(1, self.size - (len(self.trail) - i))
            s = pygame.Surface((ts * 2, ts * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, ta), (ts, ts), ts)
            surface.blit(s, (int(tx) - ts, int(ty) - ts))
        alpha = int(self.life * 255)
        sz = self.size
        s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (sz, sz), sz)
        # Bright center
        if sz > 2:
            pygame.draw.circle(s, (255, 255, 255, min(255, alpha)), (sz, sz), sz // 2)
        surface.blit(s, (int(self.x) - sz, int(self.y) - sz))


# Precompute background star field
STARS = [(random.randint(0, W), random.randint(0, H), random.uniform(0.3, 1.0), random.uniform(0, math.pi * 2)) for _ in range(80)]

# Bulb border: positions around the board edge, each with a random flicker phase
_bulb_r = 6
_bulb_gap = 20
_bulb_positions = []
for _bx in range(_bulb_gap // 2, BOARD_W, _bulb_gap):
    _bulb_positions.append((_bx, _bulb_r, random.uniform(0, math.pi * 2)))           # top
    _bulb_positions.append((_bx, BOARD_H - _bulb_r, random.uniform(0, math.pi * 2))) # bottom
for _by in range(_bulb_gap * 2, BOARD_H - _bulb_gap, _bulb_gap):
    _bulb_positions.append((_bulb_r, _by, random.uniform(0, math.pi * 2)))            # left
    _bulb_positions.append((BOARD_W - _bulb_r, _by, random.uniform(0, math.pi * 2))) # right

# Separator bulbs across panel width
_sep_bulbs = [(BOARD_W + 10 + i * _bulb_gap, random.uniform(0, math.pi * 2))
              for i in range((PANEL_W - 10) // _bulb_gap + 1)]


class Game:
    def __init__(self):
        self.high_score = 0
        self.show_intro = True
        self.show_help = False
        self.reset()

    def reset(self):
        self.board_surf = pygame.Surface((BOARD_W, BOARD_H), pygame.SRCALPHA)
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.combo = 0
        self.particles = []
        self.flash_effects = []
        self.rainbow_timer = 0
        self.shake_timer = 0
        self.shake_offset = (0, 0)
        self.t = 0
        self.game_over = False
        self.drop_timer = 0
        self.drop_interval = 1.0
        self.trail = []
        self.combo_text = []
        self.scan_lines = []
        self.next_idx = random.randint(0, len(SHAPES) - 1)
        self.next_color = random.randint(0, len(NEON_COLORS) - 1)
        self.spawn_piece()

    def spawn_piece(self):
        self.shape_idx = self.next_idx
        self.color_idx = self.next_color
        self.next_idx = random.randint(0, len(SHAPES) - 1)
        self.next_color = random.randint(0, len(NEON_COLORS) - 1)
        self.piece = [row[:] for row in SHAPES[self.shape_idx]]
        self.px = COLS // 2 - len(self.piece[0]) // 2
        self.py = 0
        self.trail = []
        if not self.valid(self.piece, self.px, self.py):
            self.game_over = True

    def valid(self, piece, px, py):
        for r, row in enumerate(piece):
            for c, v in enumerate(row):
                if v:
                    nx, ny = px + c, py + r
                    if nx < 0 or nx >= COLS or ny >= ROWS:
                        return False
                    if ny >= 0 and self.board[ny][nx]:
                        return False
        return True

    def lock(self):
        color = NEON_COLORS[self.color_idx]
        for r, row in enumerate(self.piece):
            for c, v in enumerate(row):
                if v:
                    self.board[self.py + r][self.px + c] = color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        full = [r for r in range(ROWS) if all(self.board[r])]
        if not full:
            self.combo = 0
            return
        n = len(full)
        self.combo += 1

        # Combo score: 2^(combo-1)*level (first clear=1x, second=2x, third=4x...)
        combo_score = (2 ** (self.combo - 1)) * self.level
        line_score = n * n * (2 ** (self.level - 1))
        gained = line_score + combo_score
        self.score += gained
        self.high_score = max(self.score, self.high_score)
        self.lines_cleared += n

        # Combo text popup
        cx = BOARD_W // 2
        cy = full[0] * CELL
        if self.combo > 1:
            self.combo_text.append([f"COMBO x{self.combo}! +{combo_score}", cx, cy - 20,
                                     NEON_COLORS[self.combo % len(NEON_COLORS)], 1.5])
        if n >= 4:
            self.combo_text.append([f"TETRIS! +{gained}", cx, cy, (255, 255, 0), 2.0])
        elif n >= 2:
            self.combo_text.append([f"+{gained}", cx, cy, NEON_COLORS[n % len(NEON_COLORS)], 1.2])

        # Particles - more for more lines
        speed = 1.0 + n * 0.5
        for row in full:
            for c in range(COLS):
                color = self.board[row][c] or (255, 255, 255)
                count = 4 + n * 3
                for _ in range(count):
                    self.particles.append(Particle(c * CELL + CELL // 2, row * CELL + CELL // 2, color, speed))
            self.flash_effects.append([row, random.choice(NEON_COLORS), 255, n])
            # Scan line sweep
            self.scan_lines.append([row * CELL, NEON_COLORS[n % len(NEON_COLORS)], 255])

        for r in full:
            self.board.pop(r)
            self.board.insert(0, [None] * COLS)

        new_level = self.lines_cleared // 10 + 1
        if new_level > self.level:
            self.level = new_level
            self.drop_interval = max(0.08, 1.0 - (self.level - 1) * 0.08)
            self.rainbow_timer = 2.0
            self.shake_timer = 1.0

    def move(self, dx):
        if self.valid(self.piece, self.px + dx, self.py):
            self.px += dx

    def rotate_piece(self):
        r = rotate(self.piece)
        if self.valid(r, self.px, self.py):
            self.piece = r

    def drop(self):
        if self.valid(self.piece, self.px, self.py + 1):
            color = NEON_COLORS[self.color_idx]
            for r, row in enumerate(self.piece):
                for c, v in enumerate(row):
                    if v:
                        self.trail.append([self.px + c, self.py + r, color, 180])
            self.py += 1
        else:
            self.lock()

    def hard_drop(self):
        while self.valid(self.piece, self.px, self.py + 1):
            self.py += 1
        self.lock()

    def update(self, dt):
        if self.show_intro or self.show_help:
            self.t += dt
            return
        if self.game_over:
            self.t += dt
            return
        self.t += dt
        self.drop_timer += dt
        if self.drop_timer >= self.drop_interval:
            self.drop_timer = 0
            self.drop()

        self.particles = [p for p in self.particles if p.update()]

        for fe in self.flash_effects:
            fe[2] -= 10
        self.flash_effects = [fe for fe in self.flash_effects if fe[2] > 0]

        for sl in self.scan_lines:
            sl[2] -= 8
        self.scan_lines = [sl for sl in self.scan_lines if sl[2] > 0]

        for tr in self.trail:
            tr[3] -= 18
        self.trail = [tr for tr in self.trail if tr[3] > 0]

        for ct in self.combo_text:
            ct[4] -= dt
            ct[2] -= 0.5
        self.combo_text = [ct for ct in self.combo_text if ct[4] > 0]

        if self.rainbow_timer > 0:
            self.rainbow_timer -= dt
        if self.shake_timer > 0:
            self.shake_timer -= dt
            amp = int(self.shake_timer * 10)
            self.shake_offset = (random.randint(-amp, amp), random.randint(-amp, amp))
        else:
            self.shake_offset = (0, 0)

    def ghost_pos(self):
        gy = self.py
        while self.valid(self.piece, self.px, gy + 1):
            gy += 1
        return gy

    def draw(self):
        screen.fill(BG)
        self._draw_background()

        # Rainbow overlay
        if self.rainbow_timer > 0:
            phase = self.t * 3
            rc = (
                int(127 + 127 * math.sin(phase)),
                int(127 + 127 * math.sin(phase + 2.094)),
                int(127 + 127 * math.sin(phase + 4.189)),
            )
            intensity = min(1.0, self.rainbow_timer / 2.0) * 0.3
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((*rc, int(intensity * 255)))
            screen.blit(ov, (0, 0))

        ox, oy = self.shake_offset
        board_surf = self.board_surf
        board_surf.fill((0, 0, 0, 0))

        # Grid background
        for r in range(ROWS):
            for c in range(COLS):
                col = 15 + (r + c) % 2 * 5
                pygame.draw.rect(board_surf, (col, col, col + 15, 255), (c * CELL + 1, r * CELL + 1, CELL - 2, CELL - 2))
                # subtle grid lines
                pygame.draw.rect(board_surf, (30, 30, 60, 80), (c * CELL, r * CELL, CELL, CELL), 1)

        # Trail
        for tr in self.trail:
            draw_neon_cell(board_surf, tr[0] * CELL, tr[1] * CELL, tr[2], tr[3], glow=False)

        # Board cells
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c]:
                    color = neon_color(self.board[r][c], self.t)
                    draw_neon_cell(board_surf, c * CELL, r * CELL, color)

        # Flash effects
        for fe in self.flash_effects:
            row, color, alpha, n = fe
            # Wide horizontal flash
            fs = pygame.Surface((BOARD_W, CELL), pygame.SRCALPHA)
            fs.fill((*color, min(200, alpha)))
            board_surf.blit(fs, (0, row * CELL))
            # Expanding glow rings for multi-line
            if n >= 2:
                expand = int((255 - alpha) / 255 * CELL * n)
                gs = pygame.Surface((BOARD_W, CELL * n + expand * 2), pygame.SRCALPHA)
                gs.fill((*color, min(80, alpha // 2)))
                board_surf.blit(gs, (0, row * CELL - expand))

        # Scan lines
        for sl in self.scan_lines:
            y_pos, color, alpha = sl
            ss = pygame.Surface((BOARD_W, 3), pygame.SRCALPHA)
            ss.fill((*color, min(255, alpha * 2)))
            board_surf.blit(ss, (0, y_pos))

        # Ghost piece
        gy = self.ghost_pos()
        ghost_color = NEON_COLORS[self.color_idx]
        for r, row in enumerate(self.piece):
            for c, v in enumerate(row):
                if v and gy != self.py:
                    gs = pygame.Surface((CELL - 2, CELL - 2), pygame.SRCALPHA)
                    gs.fill((*ghost_color, 25))
                    pygame.draw.rect(gs, (*ghost_color, 80), (0, 0, CELL - 2, CELL - 2), 1)
                    pygame.draw.rect(gs, (*ghost_color, 40), (1, 1, CELL - 4, CELL - 4), 1)
                    board_surf.blit(gs, ((self.px + c) * CELL + 1, (gy + r) * CELL + 1))

        # Current piece
        color = neon_color(NEON_COLORS[self.color_idx], self.t)
        for r, row in enumerate(self.piece):
            for c, v in enumerate(row):
                if v:
                    draw_neon_cell(board_surf, (self.px + c) * CELL, (self.py + r) * CELL, color)

        # Particles
        for p in self.particles:
            p.draw(board_surf)

        # Combo text popups
        for ct in self.combo_text:
            text, cx, cy, color, _ = ct
            neon_text(board_surf, text, font_md, color, cx - font_md.size(text)[0] // 2, int(cy))

        screen.blit(board_surf, (ox, oy))

        self.draw_panel()

        if self.show_intro:
            self._draw_intro()
        elif self.show_help:
            self._draw_help()

        pygame.display.flip()

    def _draw_bulb_border(self, surface, x, y, w, h, color, t, gap=18):
        """Draw a border made of small bulbs around a rectangle."""
        r = 3
        phase_seed = (x + y) * 0.1
        positions = []
        # top & bottom
        for bx in range(x + gap // 2, x + w, gap):
            positions.append((bx, y, phase_seed + bx * 0.05))
            positions.append((bx, y + h, phase_seed + bx * 0.05 + 1))
        # left & right (skip corners)
        for by in range(y + gap, y + h, gap):
            positions.append((x, by, phase_seed + by * 0.05 + 2))
            positions.append((x + w, by, phase_seed + by * 0.05 + 3))
        for bx, by, phase in positions:
            brightness = 0.5 + 0.5 * math.sin(t * (2.0 + phase % 2) + phase)
            ci = int(phase * 7 / (math.pi * 2)) % len(NEON_COLORS)
            bc = color if color is not None else NEON_COLORS[ci]
            alpha = int(80 + 175 * brightness)
            cx2, cy2 = int(bx), int(by)
            gs = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*bc, int(alpha * 0.3)), (r * 2, r * 2), r * 2)
            surface.blit(gs, (cx2 - r * 2, cy2 - r * 2))
            bs = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(bs, (*bc, alpha), (r, r), r)
            pygame.draw.circle(bs, (255, 255, 255, int(alpha * 0.5)), (r - 1, r - 1), r // 3)
            surface.blit(bs, (cx2 - r, cy2 - r))

    def _draw_bulbs(self, surface, positions, t, ox=0, oy=0):
        for bx, by, phase in positions:
            brightness = 0.5 + 0.5 * math.sin(t * (2.0 + phase % 2) + phase)
            ci = int(phase * 7 / (math.pi * 2)) % len(NEON_COLORS)
            color = NEON_COLORS[ci]
            alpha = int(80 + 175 * brightness)
            cx, cy = int(bx + ox), int(by + oy)
            # Glow
            gs = pygame.Surface((_bulb_r * 4, _bulb_r * 4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*color, int(alpha * 0.3)), (_bulb_r * 2, _bulb_r * 2), _bulb_r * 2)
            surface.blit(gs, (cx - _bulb_r * 2, cy - _bulb_r * 2))
            # Bulb body
            bs = pygame.Surface((_bulb_r * 2, _bulb_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(bs, (*color, alpha), (_bulb_r, _bulb_r), _bulb_r)
            # Highlight
            pygame.draw.circle(bs, (255, 255, 255, int(alpha * 0.5)), (_bulb_r - 2, _bulb_r - 2), _bulb_r // 3)
            surface.blit(bs, (cx - _bulb_r, cy - _bulb_r))

    def _draw_intro(self):
        t = self.t
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 10, 210))
        screen.blit(ov, (0, 0))

        def rc(off=0):
            return (int(127 + 127 * math.sin(t * 0.8 + off)),
                    int(127 + 127 * math.sin(t * 0.8 + off + 2.094)),
                    int(127 + 127 * math.sin(t * 0.8 + off + 4.189)))

        def cn(text, font, color, y):
            cx = W // 2 - font.size(text)[0] // 2
            neon_text(screen, text, font, color, cx, y, t=t)

        cn("NEON TETRIS", font_xl, rc(), 60)

        lines = [
            ("操作说明", font_md, (180, 180, 255), 120),
            ("← →   左右移动", font_sm, (160, 160, 220), 155),
            ("↑      旋转方块", font_sm, (160, 160, 220), 175),
            ("↓      加速下落（长按）", font_sm, (160, 160, 220), 195),
            ("SPACE  硬降到底", font_sm, (160, 160, 220), 215),
            ("R      重新开始", font_sm, (160, 160, 220), 235),
            ("H      帮助/规则", font_sm, (160, 160, 220), 255),
            ("得分规则", font_md, (180, 255, 180), 290),
            ("消行得分 = 行数² × 2^(关卡-1)", font_sm, (160, 220, 160), 325),
            ("连击加分 = 2^(连击数-1) × 关卡", font_sm, (160, 220, 160), 345),
            ("每消10行升一关，速度加快", font_sm, (160, 220, 160), 365),
            ("连击从第2次消行开始计算", font_sm, (160, 220, 160), 385),
        ]
        for text, font, color, y in lines:
            cn(text, font, color, y)

        pulse = 0.6 + 0.4 * math.sin(t * 4)
        hint_color = (int(255 * pulse), int(255 * pulse), 100)
        cn("按 SPACE 开始游戏", font_md, hint_color, H - 70)

    def _draw_help(self):
        t = self.t
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 10, 220))
        screen.blit(ov, (0, 0))

        def rc(off=0):
            return (int(127 + 127 * math.sin(t * 0.8 + off)),
                    int(127 + 127 * math.sin(t * 0.8 + off + 2.094)),
                    int(127 + 127 * math.sin(t * 0.8 + off + 4.189)))

        def cn(text, font, color, y):
            cx = W // 2 - font.size(text)[0] // 2
            neon_text(screen, text, font, color, cx, y, t=t)

        cn("帮助 / 规则", font_xl, rc(), 30)

        lines = [
            ("按键操作", font_md, (180, 180, 255), 80),
            ("← →      左右移动（长按加速）", font_sm, (200, 200, 255), 108),
            ("↑         旋转方块", font_sm, (200, 200, 255), 126),
            ("↓         加速下落（长按）", font_sm, (200, 200, 255), 144),
            ("SPACE     硬降到底", font_sm, (200, 200, 255), 162),
            ("R         重新开始", font_sm, (200, 200, 255), 180),
            ("H         关闭帮助", font_sm, (200, 200, 255), 198),
            ("得分规则", font_md, (180, 255, 180), 228),
            ("消行得分 = 行数² × 2^(关卡-1)", font_sm, (180, 240, 180), 256),
            ("  1行: 1×倍率  2行: 4×倍率", font_sm, (160, 220, 160), 274),
            ("  3行: 9×倍率  4行(Tetris): 16×倍率", font_sm, (160, 220, 160), 292),
            ("连击加分 = 2^(连击数-1) × 关卡", font_sm, (180, 240, 180), 316),
            ("  第1次消行: 无连击加分", font_sm, (160, 220, 160), 334),
            ("  第2次: +2×关卡  第3次: +4×关卡", font_sm, (160, 220, 160), 352),
            ("  第4次: +8×关卡  以此类推...", font_sm, (160, 220, 160), 370),
            ("关卡", font_md, (255, 220, 120), 400),
            ("每消除10行升一关，速度逐渐加快", font_sm, (240, 210, 140), 428),
            ("最高速度在第12关达到上限", font_sm, (240, 210, 140), 446),
        ]
        for text, font, color, y in lines:
            cn(text, font, color, y)

        cn("按 H 关闭帮助", font_md, (150, 150, 200), H - 50)

    def _draw_background(self):
        t = self.t
        # Animated stars
        for i, (sx, sy, brightness, phase) in enumerate(STARS):
            a = int((0.5 + 0.5 * math.sin(t * 1.5 + phase)) * brightness * 180)
            r = 1 if brightness < 0.6 else 2
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 200, 255, a), (r, r), r)
            screen.blit(s, (sx - r, sy - r))

        # Subtle vertical scan lines on panel area
        for x in range(BOARD_W, W, 4):
            a = int(8 + 4 * math.sin(t * 2 + x * 0.1))
            pygame.draw.line(screen, (20, 20, 50), (x, 0), (x, H), 1)

        # Panel background gradient
        panel_surf = pygame.Surface((PANEL_W, H), pygame.SRCALPHA)
        for y in range(H):
            a = int(120 + 30 * math.sin(y * 0.02 + t))
            panel_surf.fill((8, 8, 25, a), (0, y, PANEL_W, 1))
        screen.blit(panel_surf, (BOARD_W, 0))

        # Panel left border glow
        bc = neon_color(NEON_COLORS[int(t * 0.5) % len(NEON_COLORS)], t)
        for i, (w, a) in enumerate([(6, 20), (3, 50), (1, 150)]):
            bs = pygame.Surface((w, H), pygame.SRCALPHA)
            bs.fill((*bc, a))
            screen.blit(bs, (BOARD_W - w // 2, 0))

    def draw_panel(self):
        px = BOARD_W + 10
        t = self.t
        pw = PANEL_W - 16

        def rainbow(offset=0):
            return (
                int(127 + 127 * math.sin(t * 0.8 + offset)),
                int(127 + 127 * math.sin(t * 0.8 + offset + 2.094)),
                int(127 + 127 * math.sin(t * 0.8 + offset + 4.189)),
            )

        def stat_box(y, label, value, val_font, val_color, label_color=(120, 120, 180), h=58):
            bx = pygame.Surface((pw, h), pygame.SRCALPHA)
            bx.fill((10, 10, 35, 140))
            screen.blit(bx, (px, y))
            neon_text(screen, label, font_sm, label_color, px + 6, y + 5, t=t)
            neon_text(screen, str(value), val_font, val_color, px + 6, y + 22, t=t)

        # Title
        neon_text(screen, "TETRIS", font_xl, rainbow(), px, 8, t=t)

        # Separator: bulb row (top of panel)
        self._draw_bulbs(screen, [(x, 52, ph) for x, ph in _sep_bulbs], t)

        # Next piece box
        neon_text(screen, "NEXT", font_md, (0, 220, 255), px, 100, t=t)
        next_shape = SHAPES[self.next_idx]
        nc = NEON_COLORS[self.next_color]
        mini = 22
        box_h = 64
        box_top = 135
        box_w = len(next_shape[0]) * mini
        box_sh = len(next_shape) * mini
        nx_off = px + (pw - box_w) // 2
        ny_off = box_top + (box_h - box_sh) // 2

        nb = pygame.Surface((pw, box_h), pygame.SRCALPHA)
        nb.fill((10, 10, 30, 160))
        screen.blit(nb, (px, box_top))

        for r, row in enumerate(next_shape):
            for c, v in enumerate(row):
                if v:
                    draw_neon_cell(screen, nx_off + c * mini, ny_off + r * mini,
                                   neon_color(nc, t), size=mini)

        y = 230
        stat_box(y, "BEST", self.high_score, font_xl, neon_color((255, 180, 50), t), h=68)
        y += 88
        score_color = rainbow(1.0) if self.rainbow_timer > 0 else neon_color((100, 255, 255), t)
        stat_box(y, "SCORE", self.score, font_md, score_color)
        y += 78
        stat_box(y, "LINES", self.lines_cleared, font_md, neon_color((200, 200, 255), t))
        y += 78

        # LEVEL with shake
        lx, ly = px, y
        if self.shake_timer > 0:
            amp = int(self.shake_timer * 8)
            lx += random.randint(-amp, amp)
            ly += random.randint(-amp, amp)
        level_color = rainbow(3.0) if self.shake_timer > 0 else neon_color((0, 255, 150), t)
        lb = pygame.Surface((pw, 70), pygame.SRCALPHA)
        lb.fill((10, 10, 35, 140))
        screen.blit(lb, (lx, ly))
        neon_text(screen, "LEVEL", font_sm, (120, 120, 180), lx + 6, ly + 4, t=t)
        neon_text(screen, str(self.level), font_md, level_color, lx + 6, ly + 22, t=t)

        # H hint at bottom
        neon_text(screen, "H  帮助", font_sm, (80, 80, 120), px, H - 20, t=t)

        if self.game_over:
            ov = pygame.Surface((BOARD_W, BOARD_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 200))
            screen.blit(ov, (0, 0))
            neon_text(screen, "GAME OVER", font_xl, (255, 80, 80), 20, BOARD_H // 2 - 35, t=self.t)
            neon_text(screen, f"Score: {self.score}", font_md, (200, 200, 255),
                      40, BOARD_H // 2 + 12, t=self.t)
            neon_text(screen, "Press R to restart", font_md, (150, 150, 200),
                      25, BOARD_H // 2 + 40, t=self.t)


game = Game()
last_time = time.time()

# Hold-key repeat state: {key: [delay_remaining, repeat_timer]}
KEY_DELAY = 0.18   # initial delay before repeat
KEY_REPEAT = 0.05  # interval between repeats
hold_keys = {pygame.K_LEFT: [KEY_DELAY, 0.0],
             pygame.K_RIGHT: [KEY_DELAY, 0.0],
             pygame.K_DOWN: [KEY_DELAY, 0.0]}

running = True
while running:
    now = time.time()
    dt = min(now - last_time, 0.05)
    last_time = now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game.show_intro:
                if event.key == pygame.K_SPACE:
                    game.show_intro = False
            elif game.show_help:
                if event.key == pygame.K_h:
                    game.show_help = False
            elif event.key == pygame.K_h:
                game.show_help = True
            elif event.key == pygame.K_r:
                game.reset()
            elif not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.move(-1)
                    hold_keys[pygame.K_LEFT] = [KEY_DELAY, 0.0]
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                    hold_keys[pygame.K_RIGHT] = [KEY_DELAY, 0.0]
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_DOWN:
                    game.drop()
                    hold_keys[pygame.K_DOWN] = [KEY_DELAY, 0.0]
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()
        elif event.type == pygame.KEYUP:
            if event.key in hold_keys:
                hold_keys[event.key] = [KEY_DELAY, 0.0]

    if not game.game_over and not game.show_intro and not game.show_help:
        pressed = pygame.key.get_pressed()
        for key, action in [(pygame.K_LEFT, lambda: game.move(-1)),
                            (pygame.K_RIGHT, lambda: game.move(1)),
                            (pygame.K_DOWN, lambda: game.drop())]:
            if pressed[key]:
                state = hold_keys[key]
                if state[0] > 0:
                    state[0] -= dt
                else:
                    state[1] += dt
                    while state[1] >= KEY_REPEAT:
                        action()
                        state[1] -= KEY_REPEAT

    game.update(dt)
    game.draw()
    clock.tick(FPS)

pygame.quit()
