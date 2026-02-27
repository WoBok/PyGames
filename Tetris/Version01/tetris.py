import pygame
import random
import math
import time

pygame.init()

CELL = 32
COLS, ROWS = 10, 20
BOARD_W, BOARD_H = COLS * CELL, ROWS * CELL
PANEL_W = 220
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

try:
    font_xl = pygame.font.SysFont("Arial", 36, bold=True)
    font_lg = pygame.font.SysFont("Arial", 28, bold=True)
    font_md = pygame.font.SysFont("Arial", 20, bold=True)
    font_sm = pygame.font.SysFont("Arial", 13)
except:
    font_xl = pygame.font.Font(None, 40)
    font_lg = pygame.font.Font(None, 32)
    font_md = pygame.font.Font(None, 24)
    font_sm = pygame.font.Font(None, 17)


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


def neon_color(color, t=0):
    factor = 0.75 + 0.25 * math.sin(t * 3)
    return tuple(min(255, int(c * factor)) for c in color)


def draw_neon_cell(surface, x, y, color, alpha=255, glow=True, size=CELL):
    # Outer glow layers
    if glow and alpha > 60:
        for radius, a in [(size + 12, 25), (size + 6, 45)]:
            gs = pygame.Surface((radius, radius), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*color, int(a * alpha / 255)), (0, 0, radius, radius), border_radius=5)
            surface.blit(gs, (x - (radius - size) // 2, y - (radius - size) // 2))

    cs = size - 2
    cell = pygame.Surface((cs, cs), pygame.SRCALPHA)

    # Glass base: semi-transparent fill
    base_alpha = int(alpha * 0.55)
    cell.fill((*color, base_alpha))

    # Darker bottom-right shadow for depth
    shadow = pygame.Surface((cs, cs), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, int(alpha * 0.35)),
                        [(cs, 0), (cs, cs), (0, cs)])
    cell.blit(shadow, (0, 0))

    # Top highlight strip (glass reflection)
    hl = pygame.Surface((cs - 4, cs // 3), pygame.SRCALPHA)
    hl.fill((255, 255, 255, int(alpha * 0.45)))
    cell.blit(hl, (2, 2))

    # Left edge highlight
    le = pygame.Surface((3, cs - 4), pygame.SRCALPHA)
    le.fill((255, 255, 255, int(alpha * 0.3)))
    cell.blit(le, (2, 2))

    # Bright neon border
    border_color = tuple(min(255, c + 100) for c in color)
    pygame.draw.rect(cell, (*border_color, min(255, alpha)), (0, 0, cs, cs), 1)
    # Inner border subtle
    pygame.draw.rect(cell, (*color, min(255, int(alpha * 0.6))), (1, 1, cs - 2, cs - 2), 1)

    surface.blit(cell, (x + 1, y + 1))


def neon_text(surface, text, font, color, x, y, glow_radius=3, glow_layers=3):
    # Multi-layer glow
    for i in range(glow_layers, 0, -1):
        a = int(80 / i)
        gc = tuple(min(255, c) for c in color)
        gs = font.render(text, True, gc)
        gs.set_alpha(a)
        for dx in range(-i * glow_radius // glow_layers, i * glow_radius // glow_layers + 1):
            for dy in range(-i * glow_radius // glow_layers, i * glow_radius // glow_layers + 1):
                if dx != 0 or dy != 0:
                    surface.blit(gs, (x + dx, y + dy))
    # Sharp core
    s = font.render(text, True, color)
    surface.blit(s, (x, y))
    # White inner shine
    shine = font.render(text, True, (255, 255, 255))
    shine.set_alpha(40)
    surface.blit(shine, (x, y))


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


class Game:
    def __init__(self):
        self.high_score = 0
        self.reset()

    def reset(self):
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
        self.combo_text = []  # [(text, x, y, color, life)]
        self.scan_lines = []  # horizontal scan line effects
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

        base = n * n
        level_mult = 2 ** (self.level - 1)
        combo_mult = self.combo ** 2
        gained = base * level_mult * combo_mult
        self.score += gained
        self.high_score = max(self.score, self.high_score)
        self.lines_cleared += n

        # Combo text popup
        cx = BOARD_W // 2
        cy = full[0] * CELL
        if self.combo > 1:
            self.combo_text.append([f"COMBO x{self.combo}!", cx, cy - 20,
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
            phase = self.t * 10
            rc = (
                int(127 + 127 * math.sin(phase)),
                int(127 + 127 * math.sin(phase + 2.094)),
                int(127 + 127 * math.sin(phase + 4.189)),
            )
            intensity = min(1.0, self.rainbow_timer / 2.0) * 0.5
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((*rc, int(intensity * 255)))
            screen.blit(ov, (0, 0))

        ox, oy = self.shake_offset
        board_surf = pygame.Surface((BOARD_W, BOARD_H), pygame.SRCALPHA)

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

        # Combo text
        for ct in self.combo_text:
            text, cx, cy, color, life = ct
            a = min(255, int(life * 180))
            s = font_md.render(text, True, color)
            s.set_alpha(a)
            board_surf.blit(s, (cx - s.get_width() // 2, int(cy)))

        screen.blit(board_surf, (ox, oy))

        # Board border - animated neon
        t = self.t
        bc = neon_color(NEON_COLORS[int(t * 0.7) % len(NEON_COLORS)], t)
        for i, width in enumerate([4, 2, 1]):
            a = [60, 120, 255][i]
            bs = pygame.Surface((BOARD_W + 8, BOARD_H + 8), pygame.SRCALPHA)
            pygame.draw.rect(bs, (*bc, a), (0, 0, BOARD_W + 8, BOARD_H + 8), width, border_radius=2)
            screen.blit(bs, (ox - 4, oy - 4))

        self.draw_panel()
        pygame.display.flip()

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
        px = BOARD_W + 12
        t = self.t

        def rainbow(offset=0):
            return (
                int(127 + 127 * math.sin(t * 2 + offset)),
                int(127 + 127 * math.sin(t * 2 + offset + 2.094)),
                int(127 + 127 * math.sin(t * 2 + offset + 4.189)),
            )

        # Title
        neon_text(screen, "TETRIS", font_xl, rainbow(), px, 8, glow_radius=4, glow_layers=4)

        # Separator line
        lc = neon_color(NEON_COLORS[int(t) % len(NEON_COLORS)], t)
        for w, a in [(4, 30), (2, 80), (1, 200)]:
            ls = pygame.Surface((PANEL_W - 20, w), pygame.SRCALPHA)
            ls.fill((*lc, a))
            screen.blit(ls, (px, 50))

        # Next piece box
        neon_text(screen, "NEXT", font_md, (0, 220, 255), px, 60)
        next_shape = SHAPES[self.next_idx]
        nc = NEON_COLORS[self.next_color]
        mini = 22
        box_w = len(next_shape[0]) * mini
        box_h = len(next_shape) * mini
        nx_off = px + (PANEL_W - 20 - box_w) // 2
        ny_off = 85

        # Next piece background box
        nb = pygame.Surface((PANEL_W - 20, 60), pygame.SRCALPHA)
        nb.fill((10, 10, 30, 150))
        pygame.draw.rect(nb, (*nc, 60), (0, 0, PANEL_W - 20, 60), 1, border_radius=3)
        screen.blit(nb, (px, ny_off - 5))

        for r, row in enumerate(next_shape):
            for c, v in enumerate(row):
                if v:
                    draw_neon_cell(screen, nx_off + c * mini, ny_off + r * mini,
                                   neon_color(nc, t), size=mini)

        y = 160
        # BEST first (larger)
        neon_text(screen, "BEST", font_sm, (120, 120, 180), px, y)
        neon_text(screen, str(self.high_score), font_lg,
                  neon_color((255, 180, 50), t), px, y + 16)
        y += 52

        # SCORE
        neon_text(screen, "SCORE", font_sm, (120, 120, 180), px, y)
        score_color = rainbow(1.0) if self.rainbow_timer > 0 else neon_color((100, 255, 255), t)
        neon_text(screen, str(self.score), font_lg, score_color, px, y + 16)
        y += 52

        # LINES
        neon_text(screen, "LINES", font_sm, (120, 120, 180), px, y)
        neon_text(screen, str(self.lines_cleared), font_md, neon_color((200, 200, 255), t), px, y + 16)
        y += 48

        # COMBO
        if self.combo > 1:
            cc = rainbow(2.0)
            neon_text(screen, f"COMBO x{self.combo}", font_md, cc, px, y)
            y += 30

        # LEVEL with shake
        lx, ly = px, y + 5
        if self.shake_timer > 0:
            amp = int(self.shake_timer * 8)
            lx += random.randint(-amp, amp)
            ly += random.randint(-amp, amp)
        level_color = rainbow(3.0) if self.shake_timer > 0 else neon_color((0, 255, 150), t)
        neon_text(screen, "LEVEL", font_sm, (120, 120, 180), lx, ly)
        neon_text(screen, str(self.level), font_xl, level_color, lx, ly + 16,
                  glow_radius=5, glow_layers=4)

        # Controls
        y2 = H - 108
        neon_text(screen, "CONTROLS", font_sm, (60, 60, 100), px, y2)
        y2 += 16
        for line in ["← → Move", "↑  Rotate", "↓  Soft drop", "SPC Hard drop", "R  Restart"]:
            s = font_sm.render(line, True, (70, 70, 110))
            screen.blit(s, (px, y2))
            y2 += 17

        if self.game_over:
            ov = pygame.Surface((BOARD_W, BOARD_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 170))
            screen.blit(ov, (0, 0))
            go_color = rainbow()
            neon_text(screen, "GAME OVER", font_xl, go_color, 15, BOARD_H // 2 - 30,
                      glow_radius=6, glow_layers=5)
            neon_text(screen, f"Score: {self.score}", font_md, (200, 200, 255),
                      30, BOARD_H // 2 + 15)
            neon_text(screen, "Press R to restart", font_md, (150, 150, 200),
                      15, BOARD_H // 2 + 45)


game = Game()
last_time = time.time()

running = True
while running:
    now = time.time()
    dt = min(now - last_time, 0.05)
    last_time = now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game.reset()
            elif not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_DOWN:
                    game.drop()
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()

    game.update(dt)
    game.draw()
    clock.tick(FPS)

pygame.quit()
