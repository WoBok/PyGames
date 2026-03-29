import json
import os
import random
import sys

import pygame

def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发环境和 PyInstaller 打包环境 """
    try:
        # PyInstaller 创建一个临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


"""
新玩法贪吃蛇：赛博朋克版 + 技能系统

玩法说明：
1. 基本操作
   - 方向：↑ ↓ ← → 或 WASD
   - 空格：如果有能量，开启 / 关闭 幽灵模式（持续时间有限）
   - Tab：暂停并查看排行榜
   - ESC：退出游戏

2. 食物类型
   - 品红圆形：普通食物，每吃一个 +1 长度，+1 分，触发品红刷光特效
   - 黄色菱形：能量食物，增加一次"幽灵能量"（energy），触发黄色刷光特效

3. 幽灵模式（Ghost Mode）
   - 按空格消耗 1 点能量，进入幽灵模式 5 秒
   - 幽灵模式下可以穿过自己的身体、穿过荆棘障碍、穿墙传送
   - 是最强大的技能，可以无视一切障碍

4. 动态荆棘障碍
   - 每吃满 5 个普通食物，地图上随机生成一个新的荆棘障碍
   - 荆棘是永久的，非幽灵模式下碰到会死亡
   - 幽灵模式下可以穿过荆棘

5. 游戏结束
   - 非幽灵模式下：撞到边界、荆棘、或撞到自己，都会 Game Over
   - 幽灵模式下：无敌，可以穿过一切

6. 赛博朋克特效
   - 霓虹发光效果：蛇身、食物、障碍都有发光层
   - 粒子爆炸：吃到食物时触发粒子特效
   - 刷光效果：吃到食物时身体从头到尾闪过一道光

7. 依赖
   - pip install pygame
"""


# -------------------- 基本配置 --------------------
CELL_SIZE = 25
GRID_WIDTH = 25   # 网格宽度（5的倍数，确保每5格一组）
GRID_HEIGHT = 25  # 网格高度（5的倍数）
HUD_HEIGHT = 30   # 顶部 HUD 高度
BOTTOM_BAR_HEIGHT = 30 # 底部提示栏高度

SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT + HUD_HEIGHT + BOTTOM_BAR_HEIGHT # 屏幕高度 = HUD + 游戏区域 + 底部栏
GAME_AREA_Y = HUD_HEIGHT  # 游戏区域起始Y坐标

RENDER_FPS = 60             # 渲染帧率，保证输入跟手
STEP_INTERVAL_MS = 120       # 蛇移动间隔（毫秒），决定实际速度

# -------------------- 赛博朋克配色 --------------------
# 主色调：霓虹紫红、青蓝、亮黄
SNAKE_COLOR = (0, 255, 255)         # 青色霓虹
SNAKE_HEAD_COLOR = (255, 0, 255)    # 品红霓虹
SNAKE_GLOW = (0, 200, 255)          # 发光效果
FOOD_COLOR = (255, 0, 127)          # 品红食物
FOOD_GLOW = (255, 50, 150)          # 食物发光
ENERGY_FOOD_COLOR = (255, 255, 0)   # 黄色能量食物
ENERGY_GLOW = (255, 200, 0)         # 能量发光
BG_COLOR = (10, 5, 20)              # 深紫黑背景
GRID_COLOR = (50, 20, 80)           # 紫色网格
TEXT_COLOR = (0, 255, 255)          # 青色文字
TEXT_GLOW = (0, 200, 255)           # 文字发光
OBSTACLE_COLOR = (200, 0, 255)      # 紫红障碍
OBSTACLE_GLOW = (150, 0, 200)       # 障碍发光

GHOST_DURATION = 5_000  # 幽灵模式持续时间（毫秒）
FOOD_PER_OBSTACLE = 5   # 每吃多少普通食物生成一个障碍
LEADERBOARD_FILE = "snake_leaderboard.json"  # 排行榜文件
MAX_LEADERBOARD_ENTRIES = 10  # 排行榜最多保留多少条

# -------------------- 新系统配置 --------------------
# 道具颜色
MAGNET_COLOR = (255, 255, 0)      # 磁铁道具（黄色）
BOMB_COLOR = (0, 0, 0)             # 炸弹道具（黑色）
SCISSORS_COLOR = (0, 255, 0)       # 剪刀/减肥药（绿色）
ROTTEN_APPLE_COLOR = (128, 0, 128) # 腐烂苹果（紫色）

# 道具类型枚举
ITEM_MAGNET = "magnet"
ITEM_BOMB = "bomb"
ITEM_SCISSORS = "scissors"
ITEM_ROTTEN_APPLE = "rotten_apple"

# 传送门配置
PORTAL_PAIRS_MIN = 3
PORTAL_PAIRS_MAX = 5
PORTAL_REFRESH_MIN = 4_000  # 4秒
PORTAL_REFRESH_MAX = 10_000  # 10秒

# 地刺配置
SPIKE_COUNT_MIN = 3
SPIKE_COUNT_MAX = 5
SPIKE_TOGGLE_TIME = 500  # 0.5秒
SPIKE_REFRESH_MIN = 3_000  # 3秒
SPIKE_REFRESH_MAX = 5_000  # 5秒

# 迷雾模式配置
FOG_VISIBILITY_MIN = 3
FOG_VISIBILITY_MAX = 5

# 影子蛇配置
SHADOW_SNAKE_SPAWN_MIN = 10_000  # 10秒
SHADOW_SNAKE_SPAWN_MAX = 15_000  # 15秒

# 幽灵猎手配置
GHOST_HUNTER_COUNT_MAX = 3
GHOST_HUNTER_VISIBLE_MIN = 4_000  # 4秒
GHOST_HUNTER_VISIBLE_MAX = 7_000  # 7秒
GHOST_HUNTER_INVISIBLE_MIN = 4_000  # 4秒
GHOST_HUNTER_INVISIBLE_MAX = 8_000  # 8秒

# Boss战配置
BOSS_FOOD_THRESHOLD = 10  # 每10个食物出现Boss
BOSS_SHIELD_DURATION = 5_000  # 5秒护盾
BOSS_SIZE = 3  # Boss占据3x3格子
BOSS_BULLET_SPEED = 2  # Boss子弹速度

# 连击系统配置
COMBO_WINDOW = 2_000  # 2秒内连续吃到食物算连击


# -------------------- 粒子特效类 --------------------
class Particle:
    """单个粒子"""
    def __init__(self, x, y, color, vx, vy, life):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = random.randint(3, 8)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        # 添加重力和速度衰减
        self.vy += 0.2
        self.vx *= 0.98
    
    def is_alive(self):
        return self.life > 0
    
    def draw(self, surface):
        # 根据剩余生命调整透明度
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            # 绘制带发光效果的粒子
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color_with_alpha, (size, size), size)
            surface.blit(s, (int(self.x - size), int(self.y - size)))


class ParticleSystem:
    """粒子系统管理器"""
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, color, count=20):
        """在指定位置发射粒子"""
        for _ in range(count):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(2, 8)
            vx = speed * random.uniform(-1, 1)
            vy = speed * random.uniform(-3, 0)  # 向上喷射
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, vx, vy, life))
    
    def update(self):
        """更新所有粒子"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update()
    
    def draw(self, surface):
        """绘制所有粒子"""
        for p in self.particles:
            p.draw(surface)


# -------------------- 新系统类 --------------------
class Portal:
    """传送门"""
    def __init__(self, pos, color_id):
        self.pos = pos
        self.color_id = color_id  # 成对的传送门有相同的color_id
        self.color = self._get_color(color_id)
    
    def _get_color(self, color_id):
        """根据ID获取颜色"""
        colors = [
            (255, 0, 255),   # 品红
            (0, 255, 255),   # 青色
            (255, 255, 0),   # 黄色
            (0, 255, 0),     # 绿色
            (255, 128, 0),   # 橙色
        ]
        return colors[color_id % len(colors)]


class Spike:
    """地刺陷阱"""
    def __init__(self, pos):
        self.pos = pos
        self.visible = True
        self.last_toggle = pygame.time.get_ticks()
    
    def update(self):
        """更新地刺的显示状态"""
        now = pygame.time.get_ticks()
        if now - self.last_toggle >= SPIKE_TOGGLE_TIME:
            self.visible = not self.visible
            self.last_toggle = now


class ShadowSnake:
    """影子蛇AI"""
    def __init__(self, start_pos):
        self.snake = [start_pos]
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.last_move_time = pygame.time.get_ticks()
        self.move_interval = STEP_INTERVAL_MS
    
    def update(self, food_pos, obstacles, grid_width, grid_height):
        """更新影子蛇的位置（简单AI：朝食物移动）"""
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_interval:
            return
        
        self.last_move_time = now
        
        if not self.snake:
            return
        
        head_x, head_y = self.snake[0]
        
        # 简单AI：朝食物方向移动
        if food_pos:
            fx, fy = food_pos
            dx = 0
            dy = 0
            
            if fx > head_x:
                dx = 1
            elif fx < head_x:
                dx = -1
            elif fy > head_y:
                dy = 1
            elif fy < head_y:
                dy = -1
            
            # 如果无法朝食物方向移动，随机选择方向
            if dx == 0 and dy == 0:
                dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            
            # 避免反向移动
            if (dx, dy) == (-self.direction[0], -self.direction[1]):
                dx, dy = self.direction
            
            self.direction = (dx, dy)
        
        # 移动
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # 边界处理（穿墙）
        new_head = (new_head[0] % grid_width, new_head[1] % grid_height)
        
        # 检查是否吃到食物
        if food_pos and new_head == food_pos:
            self.snake.insert(0, new_head)
        else:
            self.snake.insert(0, new_head)
            if len(self.snake) > 1:
                self.snake.pop()


class GhostHunter:
    """幽灵猎手"""
    def __init__(self, pos):
        self.pos = pos
        self.visible = True
        self.last_toggle = pygame.time.get_ticks()
        self.visible_duration = random.randint(GHOST_HUNTER_VISIBLE_MIN, GHOST_HUNTER_VISIBLE_MAX)
        self.invisible_duration = random.randint(GHOST_HUNTER_INVISIBLE_MIN, GHOST_HUNTER_INVISIBLE_MAX)
    
    def update(self):
        """更新幽灵猎手的可见性"""
        now = pygame.time.get_ticks()
        elapsed = now - self.last_toggle
        
        if self.visible:
            if elapsed >= self.visible_duration:
                self.visible = False
                self.last_toggle = now
                self.invisible_duration = random.randint(GHOST_HUNTER_INVISIBLE_MIN, GHOST_HUNTER_INVISIBLE_MAX)
        else:
            if elapsed >= self.invisible_duration:
                self.visible = True
                self.last_toggle = now
                self.visible_duration = random.randint(GHOST_HUNTER_VISIBLE_MIN, GHOST_HUNTER_VISIBLE_MAX)
    
    def move_towards(self, target_pos, grid_width, grid_height):
        """向目标位置移动"""
        tx, ty = target_pos
        x, y = self.pos
        
        dx = 0
        dy = 0
        
        if tx > x:
            dx = 1
        elif tx < x:
            dx = -1
        
        if ty > y:
            dy = 1
        elif ty < y:
            dy = -1
        
        # 随机选择x或y方向移动（避免斜向移动）
        if dx != 0 and dy != 0:
            if random.random() < 0.5:
                dy = 0
            else:
                dx = 0
        
        new_pos = (x + dx, y + dy)
        # 允许穿墙
        new_pos = (new_pos[0] % grid_width, new_pos[1] % grid_height)
        self.pos = new_pos


class Boss:
    """Boss"""
    def __init__(self, pos):
        self.pos = pos  # 中心位置
        self.shield_active = True
        self.shield_start_time = pygame.time.get_ticks()
        self.bullets = []  # 子弹列表
        self.last_bullet_time = pygame.time.get_ticks()
        self.bullet_interval = 1_000  # 每秒发射一颗子弹
    
    def update(self, grid_width, grid_height):
        """更新Boss状态"""
        now = pygame.time.get_ticks()
        
        # 检查护盾是否消失
        if self.shield_active:
            if now - self.shield_start_time >= BOSS_SHIELD_DURATION:
                self.shield_active = False
        
        # 发射子弹
        if now - self.last_bullet_time >= self.bullet_interval:
            self.shoot_bullet(grid_width, grid_height)
            self.last_bullet_time = now
        
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx'] * BOSS_BULLET_SPEED
            bullet['y'] += bullet['dy'] * BOSS_BULLET_SPEED
            
            # 移除超出边界的子弹
            if not (0 <= bullet['x'] < grid_width and 0 <= bullet['y'] < grid_height):
                self.bullets.remove(bullet)
    
    def shoot_bullet(self, grid_width, grid_height):
        """发射子弹（8个方向）"""
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (-1, -1), (1, -1), (-1, 1)
        ]
        for dx, dy in directions:
            self.bullets.append({
                'x': self.pos[0],
                'y': self.pos[1],
                'dx': dx,
                'dy': dy
            })
    
    def get_cells(self):
        """获取Boss占据的所有格子"""
        cells = []
        for dx in range(-BOSS_SIZE//2, BOSS_SIZE//2 + 1):
            for dy in range(-BOSS_SIZE//2, BOSS_SIZE//2 + 1):
                cells.append((self.pos[0] + dx, self.pos[1] + dy))
        return cells


class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("技能贪吃蛇 - 幽灵模式 + 动态障碍")

        # 设置窗口图标
        try:
            icon_path = resource_path("snake_icon.png")
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"加载图标失败: {e}")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        # 使用支持中文的字体列表，前面优先中文，后面兜底英文
        font_candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "consolas"]
        self.font_small = pygame.font.SysFont(font_candidates, 18)
        self.font_medium = pygame.font.SysFont(font_candidates, 24, bold=True)  # 中等字体，用于最高分
        self.font_big = pygame.font.SysFont(font_candidates, 36, bold=True)
        self.font_xlarge = pygame.font.SysFont(font_candidates, 48, bold=True)  # 特大字体，用于标题

        # 渲染帧率（固定）
        self.fps = RENDER_FPS

        # 排行榜相关
        self.leaderboard = self.load_leaderboard()
        self.show_leaderboard = False  # 是否显示排行榜界面
        self.entering_name = False     # 是否正在输入名字
        self.player_name_input = ""    # 输入的名字
        self.paused = False            # 游戏是否暂停

        # 粒子系统
        self.particle_system = ParticleSystem()

        self.reset(start_with_intro=True)

    # -------------------- 游戏状态初始化 --------------------
    def reset(self, start_with_intro: bool = False):
        # start_with_intro=True 表示回到启动界面，仅首次进入使用；
        # 复盘（按 R）时使用 start_with_intro=False，直接开新局。
        self.started = not start_with_intro
        self.last_move_time = pygame.time.get_ticks()
        self.step_interval_ms = STEP_INTERVAL_MS
        center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = [
            center,
            (center[0] - 1, center[1]),
            (center[0] - 2, center[1]),
        ]
        self.direction = (1, 0)  # 初始向右
        self.next_direction = self.direction

        self.score = 0
        self.normal_food_eaten = 0

        self.obstacles = set()

        self.food_pos = None
        self.energy_food_pos = None

        self.energy = 1  # 初始给一点能量试试新玩法
        self.ghost_mode = False
        self.ghost_end_time = 0

        # 刷光效果
        self.glow_effect_active = False
        self.glow_effect_start = 0
        self.glow_effect_color = None
        self.glow_effect_duration = 500  # 刷光持续时间（毫秒）

        self.spawn_food()

        self.game_over = False
        self.game_over_reason = ""
        self.paused = False
        self.show_leaderboard = False

        # -------------------- 新系统初始化 --------------------
        # 初始化传送门和地刺
        self.init_portals()
        self.init_spikes()
        # 道具系统
        self.item_pos = None  # 当前道具位置
        self.item_type = None  # 当前道具类型
        self.magnet_active = False  # 磁铁激活状态
        self.magnet_food_targets = []  # 磁铁吸引的食物目标
        
        # 腐烂苹果反向控制
        self.reverse_controls = False
        self.reverse_controls_end_time = 0
        self.rainbow_glow_active = False  # 彩虹流光效果
        
        # 剪刀效果
        self.scissors_active = False
        self.scissors_remove_count = 0
        
        # 传送门系统
        self.portals = []  # 传送门列表，[(pos, color_id), ...]
        self.last_portal_refresh = pygame.time.get_ticks()
        
        # 地刺系统
        self.spikes = []  # Spike对象列表
        self.last_spike_refresh = pygame.time.get_ticks()
        
        # 迷雾模式（默认启用）
        self.fog_enabled = True
        self.fog_visibility = random.randint(FOG_VISIBILITY_MIN, FOG_VISIBILITY_MAX)
        
        # 影子蛇系统
        self.shadow_snakes = []  # ShadowSnake对象列表
        self.last_shadow_snake_spawn = pygame.time.get_ticks()
        
        # 幽灵猎手系统
        self.ghost_hunters = []  # GhostHunter对象列表
        self.last_ghost_hunter_spawn = pygame.time.get_ticks()
        
        # Boss系统
        self.boss = None  # Boss对象
        self.boss_food_count = 0  # Boss触发计数器
        
        # 连击系统
        self.combo_count = 0
        self.combo_multiplier = 1
        self.last_food_time = 0

    # -------------------- 排行榜相关 --------------------
    def load_leaderboard(self):
        """从文件加载排行榜，格式：[{"name": "玩家名", "score": 分数}, ...]"""
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_leaderboard(self):
        """保存排行榜到文件"""
        try:
            with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
                json.dump(self.leaderboard, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存排行榜失败: {e}")

    def is_high_score(self, score):
        """判断分数是否能进入排行榜"""
        if len(self.leaderboard) < MAX_LEADERBOARD_ENTRIES:
            return True
        return score > self.leaderboard[-1]["score"]

    def add_to_leaderboard(self, name, score):
        """添加记录到排行榜并排序"""
        self.leaderboard.append({"name": name, "score": score})
        self.leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self.leaderboard = self.leaderboard[:MAX_LEADERBOARD_ENTRIES]
        self.save_leaderboard()

    # -------------------- 工具函数 --------------------
    def random_empty_cell(self):
        """从空白位置里随机挑一个网格坐标"""
        occupied = set(self.snake) | self.obstacles
        if self.food_pos:
            occupied.add(self.food_pos)
        if self.energy_food_pos:
            occupied.add(self.energy_food_pos)
        if self.item_pos:
            occupied.add(self.item_pos)
        # 考虑传送门
        for portal_pos, _ in self.portals:
            occupied.add(portal_pos)
        # 考虑地刺
        for spike in self.spikes:
            occupied.add(spike.pos)
        # 考虑影子蛇
        for shadow_snake in self.shadow_snakes:
            occupied.update(shadow_snake.snake)
        # 考虑幽灵猎手
        for hunter in self.ghost_hunters:
            occupied.add(hunter.pos)
        # 考虑Boss
        if self.boss:
            occupied.update(self.boss.get_cells())
            for bullet in self.boss.bullets:
                occupied.add((int(bullet['x']), int(bullet['y'])))

        all_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if not all_cells:
            return None
        return random.choice(all_cells)

    def spawn_food(self):
        """生成普通食物和（有概率）能量食物"""
        self.food_pos = self.random_empty_cell()
        # 30% 概率生成能量食物（如果当前没有）
        if self.energy_food_pos is None and random.random() < 0.3:
            self.energy_food_pos = self.random_empty_cell()
    
    def spawn_item(self):
        """生成道具（15%概率）"""
        if self.item_pos is None and random.random() < 0.15:
            self.item_pos = self.random_empty_cell()
            if self.item_pos:
                # 随机选择道具类型
                item_types = [ITEM_MAGNET, ITEM_BOMB, ITEM_SCISSORS, ITEM_ROTTEN_APPLE]
                self.item_type = random.choice(item_types)
    
    def init_portals(self):
        """初始化传送门"""
        pair_count = random.randint(PORTAL_PAIRS_MIN, PORTAL_PAIRS_MAX)
        self.portals = []
        for color_id in range(pair_count):
            # 每对传送门生成两个
            for _ in range(2):
                pos = self.random_empty_cell()
                if pos:
                    self.portals.append((pos, color_id))
    
    def refresh_portals(self):
        """刷新传送门位置"""
        if not self.portals:
            self.init_portals()
            return
        
        # 随机选择一对传送门刷新
        if len(self.portals) >= 2:
            color_ids = list(set(p[1] for p in self.portals))
            if color_ids:
                refresh_color_id = random.choice(color_ids)
                # 移除该颜色的传送门
                self.portals = [p for p in self.portals if p[1] != refresh_color_id]
                # 重新生成一对
                for _ in range(2):
                    pos = self.random_empty_cell()
                    if pos:
                        self.portals.append((pos, refresh_color_id))
    
    def init_spikes(self):
        """初始化地刺"""
        spike_count = random.randint(SPIKE_COUNT_MIN, SPIKE_COUNT_MAX)
        self.spikes = []
        for _ in range(spike_count):
            pos = self.random_empty_cell()
            if pos:
                self.spikes.append(Spike(pos))
    
    def refresh_spike(self):
        """刷新一个地刺的位置"""
        if self.spikes:
            # 随机移除一个
            self.spikes.pop(random.randint(0, len(self.spikes) - 1))
        # 添加一个新的
        pos = self.random_empty_cell()
        if pos:
            self.spikes.append(Spike(pos))

    def spawn_obstacle(self):
        cell = self.random_empty_cell()
        if cell is not None:
            self.obstacles.add(cell)

    # -------------------- 输入处理 --------------------
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # 如果正在输入名字
                if self.entering_name:
                    if event.key == pygame.K_RETURN:
                        # 回车确认，添加到排行榜
                        if self.player_name_input.strip():
                            self.add_to_leaderboard(self.player_name_input.strip(), self.score)
                        self.entering_name = False
                        self.player_name_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        # 退格删除
                        self.player_name_input = self.player_name_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        # ESC 取消输入
                        self.entering_name = False
                        self.player_name_input = ""
                    else:
                        # 输入字符（限制长度）
                        if len(self.player_name_input) < 15:
                            self.player_name_input += event.unicode
                    return

                # 查看排行榜（Tab 键切换，同时暂停/恢复游戏）
                if event.key == pygame.K_TAB:
                    self.show_leaderboard = not self.show_leaderboard
                    # 显示排行榜时暂停，关闭时恢复
                    if self.show_leaderboard:
                        self.paused = True
                    else:
                        self.paused = False
                    return

                # Game Over 界面输入
                if self.game_over and not self.entering_name:
                    if event.key == pygame.K_ESCAPE:
                        self.reset(start_with_intro=True) # 返回主界面
                    elif event.key == pygame.K_r:
                        self.reset(start_with_intro=False) # 重新开始
                    return

                # 启动画面：按空格键开始（ESC 直接退出）
                if not self.started:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        self.started = True
                    return

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # 方向键 / WASD
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if self.direction != (0, 1):
                        self.next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.direction != (0, -1):
                        self.next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.direction != (-1, 0):
                        self.next_direction = (1, 0)
                # 幽灵模式开关（游戏结束时不能开启）
                elif event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.toggle_ghost_mode()


    def toggle_ghost_mode(self):
        now = pygame.time.get_ticks()
        # 已在幽灵模式：直接关闭
        if self.ghost_mode:
            self.ghost_mode = False
            self.ghost_end_time = now
            return

        # 还没开启，且有能量：开启
        if self.energy > 0 and not self.ghost_mode:
            self.energy -= 1
            self.ghost_mode = True
            self.ghost_end_time = now + GHOST_DURATION

    def trigger_game_over(self, reason):
        """触发游戏结束，判断是否进入排行榜"""
        self.game_over = True
        self.game_over_reason = reason
        # 判断是否进入排行榜
        if self.score > 0 and self.is_high_score(self.score):
            self.entering_name = True
            self.player_name_input = ""
    
    def trigger_glow_effect(self, color):
        """触发身体刷光效果"""
        self.glow_effect_active = True
        self.glow_effect_start = pygame.time.get_ticks()
        self.glow_effect_color = color
    
    def handle_item_effect(self, item_type, head_pos):
        """处理道具效果"""
        head_x, head_y = head_pos
        screen_x = head_x * CELL_SIZE + CELL_SIZE // 2
        screen_y = GAME_AREA_Y + head_y * CELL_SIZE + CELL_SIZE // 2
        
        if item_type == ITEM_MAGNET:
            # 磁铁：吸引5x5范围内的食物
            self.magnet_active = True
            self.magnet_food_targets = []
            # 查找5x5范围内的食物
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    check_pos = (head_x + dx, head_y + dy)
                    if self.food_pos == check_pos:
                        self.magnet_food_targets.append(self.food_pos)
                    if self.energy_food_pos == check_pos:
                        self.magnet_food_targets.append(self.energy_food_pos)
            # 特效
            self.particle_system.emit(screen_x, screen_y, MAGNET_COLOR, count=40)
        
        elif item_type == ITEM_BOMB:
            # 炸弹：清除5x5范围内的障碍物
            removed_obstacles = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    check_pos = (head_x + dx, head_y + dy)
                    if check_pos in self.obstacles:
                        removed_obstacles.append(check_pos)
                        self.obstacles.remove(check_pos)
            # 爆炸特效
            for pos in removed_obstacles:
                obs_x = pos[0] * CELL_SIZE + CELL_SIZE // 2
                obs_y = GAME_AREA_Y + pos[1] * CELL_SIZE + CELL_SIZE // 2
                self.particle_system.emit(obs_x, obs_y, BOMB_COLOR, count=30)
            self.particle_system.emit(screen_x, screen_y, BOMB_COLOR, count=50)
        
        elif item_type == ITEM_SCISSORS:
            # 剪刀：减少身体长度3-5格
            remove_count = random.randint(3, 5)
            self.scissors_active = True
            self.scissors_remove_count = min(remove_count, len(self.snake) - 1)  # 至少保留头部
            # 特效
            self.particle_system.emit(screen_x, screen_y, SCISSORS_COLOR, count=35)
        
        elif item_type == ITEM_ROTTEN_APPLE:
            # 腐烂苹果：操作反向5秒，彩虹流光特效
            self.reverse_controls = True
            self.reverse_controls_end_time = pygame.time.get_ticks() + 5_000
            self.rainbow_glow_active = True
            # 特效
            self.particle_system.emit(screen_x, screen_y, ROTTEN_APPLE_COLOR, count=40)

    # -------------------- 游戏更新逻辑 --------------------
    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        # 幽灵模式计时即使在未移动时也需要更新
        if self.ghost_mode and now >= self.ghost_end_time:
            self.ghost_mode = False
        
        # 反向控制计时
        if self.reverse_controls and now >= self.reverse_controls_end_time:
            self.reverse_controls = False
            self.rainbow_glow_active = False
        
        # 磁铁效果：更新食物位置（飞向蛇头）
        if self.magnet_active and self.magnet_food_targets:
            head_pos = self.snake[0] if self.snake else None
            if head_pos:
                new_targets = []
                for food_pos in self.magnet_food_targets:
                    fx, fy = food_pos
                    hx, hy = head_pos
                    # 向蛇头移动
                    if fx < hx:
                        fx += 1
                    elif fx > hx:
                        fx -= 1
                    if fy < hy:
                        fy += 1
                    elif fy > hy:
                        fy -= 1
                    new_pos = (fx, fy)
                    if new_pos == head_pos:
                        # 到达蛇头，触发吃食物效果
                        if food_pos == self.food_pos:
                            self.food_pos = None
                            self.score += 1
                            self.normal_food_eaten += 1
                        elif food_pos == self.energy_food_pos:
                            self.energy_food_pos = None
                            self.energy += 1
                    else:
                        new_targets.append(new_pos)
                        # 更新食物位置
                        if food_pos == self.food_pos:
                            self.food_pos = new_pos
                        elif food_pos == self.energy_food_pos:
                            self.energy_food_pos = new_pos
                self.magnet_food_targets = new_targets
                if not self.magnet_food_targets:
                    self.magnet_active = False
        else:
            self.magnet_active = False
        
        # 剪刀效果：从尾部移除
        if self.scissors_active and self.scissors_remove_count > 0 and len(self.snake) > 1:
            tail_pos = self.snake[-1]
            tail_screen_x = tail_pos[0] * CELL_SIZE + CELL_SIZE // 2
            tail_screen_y = GAME_AREA_Y + tail_pos[1] * CELL_SIZE + CELL_SIZE // 2
            self.particle_system.emit(tail_screen_x, tail_screen_y, SCISSORS_COLOR, count=20)
            self.snake.pop()
            self.scissors_remove_count -= 1
            if self.scissors_remove_count == 0:
                self.scissors_active = False

        # 移动节奏控制：未到间隔则不移动
        if now - self.last_move_time < self.step_interval_ms:
            return
        self.last_move_time = now

        # 更新方向（考虑反向控制）
        if self.reverse_controls:
            # 反向控制：方向相反
            dx, dy = self.next_direction
            reversed_direction = (-dx, -dy)
            self.direction = reversed_direction
        else:
            self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 传送门检测：进入传送门后传送到同颜色的另一个传送门
        for portal_pos, color_id in self.portals:
            if new_head == portal_pos:
                # 找到同颜色的其他传送门
                other_portals = [p for p in self.portals if p[1] == color_id and p[0] != portal_pos]
                if other_portals:
                    new_head = other_portals[0][0]
                    # 传送特效
                    screen_x = portal_pos[0] * CELL_SIZE + CELL_SIZE // 2
                    screen_y = GAME_AREA_Y + portal_pos[1] * CELL_SIZE + CELL_SIZE // 2
                    self.particle_system.emit(screen_x, screen_y, (255, 0, 255), count=30)
                    break
        
        # 地刺检测：非幽灵模式下撞到可见的地刺会死亡
        for spike in self.spikes:
            if spike.visible and new_head == spike.pos:
                if not self.ghost_mode:
                    self.trigger_game_over("撞到地刺了！")
                    return
        
        # 边界检测：幽灵模式允许穿墙（从另一侧出来）；正常模式死亡
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            if self.ghost_mode:
                new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
            else:
                self.trigger_game_over("撞到边界了！")
                return

        # 障碍检测：幽灵模式可以穿过障碍
        if new_head in self.obstacles:
            if not self.ghost_mode:
                self.trigger_game_over("撞到荆棘了！")
                return

        # 自身碰撞（根据幽灵模式判断是否死亡）
        if new_head in self.snake:
            if not self.ghost_mode:
                self.trigger_game_over("撞到自己了！")
                return
            # 幽灵模式下可以穿过身体：尾部仍然会移动

        # 移动：在前面加新头
        self.snake.insert(0, new_head)

        ate_food = False
        # 吃普通食物
        if self.food_pos and new_head == self.food_pos:
            ate_food = True
            # 连击系统计算
            if self.last_food_time > 0 and now - self.last_food_time < COMBO_WINDOW:
                self.combo_count += 1
                self.combo_multiplier = min(8, 2 ** min(self.combo_count // 2, 3))
            else:
                self.combo_count = 0
                self.combo_multiplier = 1
            self.score += 1 * self.combo_multiplier
            self.normal_food_eaten += 1
            self.last_food_time = now
            # 触发粒子特效
            food_screen_x = self.food_pos[0] * CELL_SIZE + CELL_SIZE // 2
            food_screen_y = GAME_AREA_Y + self.food_pos[1] * CELL_SIZE + CELL_SIZE // 2
            self.particle_system.emit(food_screen_x, food_screen_y, FOOD_COLOR, count=25)
            # 触发身体刷光效果
            self.trigger_glow_effect(FOOD_COLOR)
            self.food_pos = None

            # 吃够一定数量普通食物后，生成障碍
            if self.normal_food_eaten % FOOD_PER_OBSTACLE == 0:
                self.spawn_obstacle()
            
            # 检查是否触发Boss（在吃完食物后检查）
            if self.normal_food_eaten > 0 and self.normal_food_eaten % BOSS_FOOD_THRESHOLD == 0 and self.boss is None:
                boss_pos = self.random_empty_cell()
                if boss_pos:
                    self.boss = Boss(boss_pos)

        # 吃能量食物
        if self.energy_food_pos and new_head == self.energy_food_pos:
            # 触发能量食物粒子特效（黄色）
            energy_screen_x = self.energy_food_pos[0] * CELL_SIZE + CELL_SIZE // 2
            energy_screen_y = GAME_AREA_Y + self.energy_food_pos[1] * CELL_SIZE + CELL_SIZE // 2
            self.particle_system.emit(energy_screen_x, energy_screen_y, ENERGY_FOOD_COLOR, count=30)
            # 触发身体刷光效果
            self.trigger_glow_effect(ENERGY_FOOD_COLOR)
            self.energy_food_pos = None
            self.energy += 1
        
        # 吃道具
        if self.item_pos and new_head == self.item_pos:
            self.handle_item_effect(self.item_type, new_head)
            self.item_pos = None
            self.item_type = None

        # 如果没有吃普通食物，尾巴要前进（去掉最后一个块）
        if not ate_food:
            self.snake.pop()

        # 如果食物被吃掉了，就重新生成
        if self.food_pos is None:
            self.spawn_food()
        
        # 道具生成
        self.spawn_item()
        
        # 更新传送门刷新
        if now - self.last_portal_refresh >= random.randint(PORTAL_REFRESH_MIN, PORTAL_REFRESH_MAX):
            self.refresh_portals()
            self.last_portal_refresh = now
        
        # 更新地刺
        for spike in self.spikes:
            spike.update()
        
        # 更新地刺刷新
        if now - self.last_spike_refresh >= random.randint(SPIKE_REFRESH_MIN, SPIKE_REFRESH_MAX):
            self.refresh_spike()
            self.last_spike_refresh = now
        
        # 更新影子蛇
        for shadow_snake in self.shadow_snakes[:]:
            shadow_snake.update(self.food_pos, self.obstacles, GRID_WIDTH, GRID_HEIGHT)
            # 检查影子蛇是否撞到自己（头部碰撞）
            if shadow_snake.snake and self.snake:
                shadow_head = shadow_snake.snake[0]
                if shadow_head in self.snake:
                    # 影子蛇撞到玩家身体，死亡并变成食物
                    shadow_length = len(shadow_snake.snake)
                    for i, pos in enumerate(shadow_snake.snake):
                        if pos not in self.snake and pos not in self.obstacles:
                            if self.food_pos is None:
                                self.food_pos = pos
                            elif self.energy_food_pos is None:
                                self.energy_food_pos = pos
                            elif i % 2 == 0:  # 部分变成食物
                                pass  # 可以扩展为生成临时食物
                    self.shadow_snakes.remove(shadow_snake)
                # 检查玩家是否撞到影子蛇身体
                if self.snake[0] in shadow_snake.snake[1:]:
                    if not self.ghost_mode:
                        self.trigger_game_over("撞到影子蛇了！")
                        return
        
        # 更新幽灵猎手
        if self.snake:
            player_head = self.snake[0]
            for hunter in self.ghost_hunters:
                hunter.update()
                if hunter.visible:
                    hunter.move_towards(player_head, GRID_WIDTH, GRID_HEIGHT)
                    # 检查碰撞
                    if hunter.pos == player_head:
                        if not self.ghost_mode:
                            self.trigger_game_over("被幽灵猎手捕获了！")
                            return
        
        # 生成新的影子蛇
        if now - self.last_shadow_snake_spawn >= random.randint(SHADOW_SNAKE_SPAWN_MIN, SHADOW_SNAKE_SPAWN_MAX):
            spawn_pos = self.random_empty_cell()
            if spawn_pos:
                self.shadow_snakes.append(ShadowSnake(spawn_pos))
                self.last_shadow_snake_spawn = now
        
        # 生成新的幽灵猎手
        if len(self.ghost_hunters) < GHOST_HUNTER_COUNT_MAX:
            if now - self.last_ghost_hunter_spawn >= random.randint(3_000, 6_000):
                spawn_pos = self.random_empty_cell()
                if spawn_pos:
                    self.ghost_hunters.append(GhostHunter(spawn_pos))
                    self.last_ghost_hunter_spawn = now
        
        # 移除消失的幽灵猎手（应该在GhostHunter类中处理，这里先简单实现）
        self.ghost_hunters = [h for h in self.ghost_hunters if h.visible or (now - h.last_toggle < h.invisible_duration + 1000)]
        
        # 更新Boss
        if self.boss:
            self.boss.update(GRID_WIDTH, GRID_HEIGHT)
            # 检查Boss子弹碰撞
            for bullet in self.boss.bullets[:]:
                bullet_pos = (int(bullet['x']), int(bullet['y']))
                if bullet_pos == new_head:
                    if not self.ghost_mode:
                        self.trigger_game_over("被Boss子弹击中了！")
                        return
            # 检查Boss碰撞（无护盾时可击杀）
            if not self.boss.shield_active and new_head in self.boss.get_cells():
                if self.ghost_mode:
                    # 击杀Boss
                    boss_screen_x = self.boss.pos[0] * CELL_SIZE + CELL_SIZE // 2
                    boss_screen_y = GAME_AREA_Y + self.boss.pos[1] * CELL_SIZE + CELL_SIZE // 2
                    self.particle_system.emit(boss_screen_x, boss_screen_y, (255, 215, 0), count=100)
                    self.score += 20  # Boss击杀奖励
                    self.boss = None
                else:
                    self.trigger_game_over("撞到Boss了！")
                    return
        

    # -------------------- 绘制相关 --------------------
    def draw_text_with_glow(self, text, font, color, pos, center=False):
        """绘制带发光效果的文字"""
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        if center:
            text_rect.center = pos
        else:
            text_rect.topleft = pos
        
        # 绘制发光层
        glow_color = tuple(max(0, c - 50) for c in color)
        for offset in [(2,2), (-2,2), (2,-2), (-2,-2), (0,2), (0,-2), (2,0), (-2,0)]:
            glow_surf = font.render(text, True, glow_color)
            glow_pos = (text_rect.x + offset[0], text_rect.y + offset[1])
            self.screen.blit(glow_surf, glow_pos)
        
        # 绘制主文字
        self.screen.blit(text_surf, text_rect)
        return text_rect
    
    def draw_grid(self):
        """绘制赛博朋克风格的网格（在游戏区域内，不包括底部栏）"""
        game_area_end_y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT
        
        # 绘制游戏区域的边框（上左下右）
        border_color = (100, 50, 150)
        pygame.draw.line(self.screen, border_color, (0, GAME_AREA_Y), (SCREEN_WIDTH, GAME_AREA_Y), 2)  # 上边
        pygame.draw.line(self.screen, border_color, (0, GAME_AREA_Y), (0, game_area_end_y), 2)  # 左边
        pygame.draw.line(self.screen, border_color, (0, game_area_end_y - 1), (SCREEN_WIDTH, game_area_end_y - 1), 2)  # 下边
        pygame.draw.line(self.screen, border_color, (SCREEN_WIDTH - 1, GAME_AREA_Y), (SCREEN_WIDTH - 1, game_area_end_y), 2)  # 右边
        
        # 主网格线（在游戏区域内）
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, GAME_AREA_Y), (x, game_area_end_y), 1)
        for y in range(GAME_AREA_Y, game_area_end_y, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y), 1)
        
        # 每隔5格绘制高亮线
        bright_grid = (80, 40, 120)
        for x in range(0, SCREEN_WIDTH, CELL_SIZE * 5):
            pygame.draw.line(self.screen, bright_grid, (x, GAME_AREA_Y), (x, game_area_end_y), 2)
        for y in range(GAME_AREA_Y, game_area_end_y, CELL_SIZE * 5):
            pygame.draw.line(self.screen, bright_grid, (0, y), (SCREEN_WIDTH, y), 2)
    
    def draw_fog(self):
        """绘制迷雾模式：蛇头周围3-5格可见，其他区域黑色"""
        if not self.fog_enabled or not self.snake:
            return
        
        head_x, head_y = self.snake[0]
        visibility = self.fog_visibility
        
        # 创建迷雾表面
        fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT - BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 220))  # 半透明黑色迷雾
        
        # 在蛇头周围创建可见区域（渐变）
        for dx in range(-visibility, visibility + 1):
            for dy in range(-visibility, visibility + 1):
                distance = (dx**2 + dy**2)**0.5
                if distance <= visibility:
                    x = head_x + dx
                    y = head_y + dy
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        screen_x = x * CELL_SIZE
                        screen_y = y * CELL_SIZE
                        # 清除该区域的迷雾（使用alpha通道）
                        fog_rect = pygame.Rect(screen_x, screen_y, CELL_SIZE, CELL_SIZE)
                        clear_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        clear_surf.fill((0, 0, 0, 0))
                        fog_surface.blit(clear_surf, fog_rect)
        
        self.screen.blit(fog_surface, (0, GAME_AREA_Y))

    def draw_snake(self):
        """绘制蛇（圆球状，带渐变色、光泽效果和刷光效果）"""
        # 计算刷光效果进度
        glow_progress = -1  # -1表示无效，0-1表示从头到尾的进度
        if self.glow_effect_active:
            elapsed = pygame.time.get_ticks() - self.glow_effect_start
            if elapsed < self.glow_effect_duration:
                glow_progress = elapsed / self.glow_effect_duration
            else:
                self.glow_effect_active = False
        
        snake_length = len(self.snake)
        
        # 幽灵模式闪烁效果：由慢变快，提示即将结束
        ghost_blink = False
        ghost_blink_interval = 200  # 默认200ms
        if self.ghost_mode:
            time_left = max(0, self.ghost_end_time - pygame.time.get_ticks())
            # 剩余时间越少，闪烁越快
            if time_left < 2000:  # 最后2秒
                ghost_blink_interval = 50  # 很快
            elif time_left < 3000:  # 最后3秒
                ghost_blink_interval = 100  # 较快
            elif time_left < 4000:  # 最后4秒
                ghost_blink_interval = 150  # 中等
            ghost_blink = (pygame.time.get_ticks() // ghost_blink_interval) % 2 == 0
        
        for i, (x, y) in enumerate(self.snake):
            center_x = x * CELL_SIZE + CELL_SIZE // 2
            center_y = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
            
            # 头部和身体大小不同
            if i == 0:
                # 头部：稍大
                radius = CELL_SIZE // 2 - 1
                base_color = SNAKE_HEAD_COLOR
                glow_color = SNAKE_HEAD_COLOR
            else:
                # 身体：比头部小（稍微大一点）
                radius = int(CELL_SIZE * 0.42)  # 身体半径约为头部的84%
                base_color = SNAKE_COLOR
                glow_color = SNAKE_GLOW

            # 刷光效果：检查当前节点是否应该被刷光点亮
            is_glowing = False
            rainbow_color = None
            if self.rainbow_glow_active:
                # 彩虹流光效果：根据时间和位置计算彩虹色
                hue = (i * 30 + pygame.time.get_ticks() // 20) % 360
                # HSV转RGB的简化版本
                h = hue / 60.0
                c = 1.0
                x = c * (1 - abs(h % 2 - 1))
                if h < 1:
                    rainbow_color = (255, int(255 * x), 0)
                elif h < 2:
                    rainbow_color = (int(255 * x), 255, 0)
                elif h < 3:
                    rainbow_color = (0, 255, int(255 * x))
                elif h < 4:
                    rainbow_color = (0, int(255 * x), 255)
                elif h < 5:
                    rainbow_color = (int(255 * x), 0, 255)
                else:
                    rainbow_color = (255, 0, int(255 * x))
                base_color = rainbow_color
                glow_color = rainbow_color
            
            if glow_progress >= 0 and snake_length > 0 and not self.rainbow_glow_active:
                # 计算刷光应该到达的节点索引（带点宽度，让刷光更明显）
                glow_position = glow_progress * snake_length
                glow_width = 3  # 刷光的宽度（几个节点同时亮）
                if abs(i - glow_position) < glow_width:
                    is_glowing = True
                    # 根据距离计算亮度
                    distance_factor = 1.0 - abs(i - glow_position) / glow_width
                    # 替换颜色为刷光颜色，并增加亮度
                    blend_factor = distance_factor * 0.9
                    # 混合刷光颜色，并增加整体亮度
                    base_color = tuple(
                        min(255, int((base_color[j] * (1 - blend_factor) + self.glow_effect_color[j] * blend_factor) * 1.3))
                        for j in range(3)
                    )
                    glow_color = tuple(min(255, int(c * 1.2)) for c in self.glow_effect_color)

            # 幽灵模式：半透明闪烁
            alpha = 255
            if self.ghost_mode:
                if ghost_blink:
                    alpha = 120  # 半透明
                else:
                    alpha = 200  # 稍微透明
            
            # 渐变色：从头部到尾部颜色渐变
            if snake_length > 1:
                gradient_factor = i / max(1, snake_length - 1)
                # 从头部颜色渐变到尾部颜色（稍微变暗）
                color = tuple(
                    int(base_color[j] * (1 - gradient_factor * 0.3))
                    for j in range(3)
                )
            else:
                color = base_color
            
            # 绘制发光层（多层圆形，越外越淡）
            if self.rainbow_glow_active:
                glow_intensity = 8  # 彩虹流光加强发光
            else:
                glow_intensity = 6 if is_glowing else 4  # 刷光时加强发光
            for r in range(radius + glow_intensity, radius, -1):
                alpha_glow = int((50 if self.rainbow_glow_active else (30 if is_glowing else 20)) * (1 - (r - radius) / glow_intensity))
                if self.ghost_mode:
                    alpha_glow = int(alpha_glow * (alpha / 255))
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*glow_color, alpha_glow), (r, r), r)
                self.screen.blit(s, (center_x - r, center_y - r))
            
            # 绘制主体圆球（带渐变和光泽）
            # 创建渐变表面
            ball_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            
            # 绘制基础圆球
            pygame.draw.circle(ball_surf, (*color, alpha), (radius, radius), radius)
            
            # 添加光泽效果（高光）
            highlight_radius = int(radius * 0.6)
            highlight_offset_x = int(radius * 0.3)
            highlight_offset_y = int(radius * 0.3)
            highlight_color = tuple(min(c + 80, 255) for c in color)
            if alpha < 255:
                highlight_alpha = int(alpha * 0.8)
            else:
                highlight_alpha = 200
            pygame.draw.circle(
                ball_surf, (*highlight_color, highlight_alpha),
                (radius - highlight_offset_x, radius - highlight_offset_y),
                highlight_radius
            )
            
            # 添加顶部小高光点
            small_highlight_radius = int(radius * 0.3)
            small_highlight_pos_x = int(radius * 0.4)
            small_highlight_pos_y = int(radius * 0.4)
            pygame.draw.circle(
                ball_surf, (255, 255, 255, min(alpha, 180)),
                (radius - small_highlight_pos_x, radius - small_highlight_pos_y),
                small_highlight_radius
            )
            
            # 绘制到屏幕
            self.screen.blit(ball_surf, (center_x - radius, center_y - radius))
            
            # 头部添加眼睛
            if i == 0:
                # 根据方向确定眼睛位置（眼睛在移动方向的前方，左右对称）
                dx, dy = self.direction
                eye_size = max(2, radius // 4)  # 眼睛大小
                eye_forward = radius // 2  # 眼睛在移动方向前方的偏移
                eye_side = radius // 3  # 眼睛左右对称的偏移
                
                # 计算眼睛位置（在移动方向前方，左右对称）
                if dx == 1:  # 向右移动
                    eye1_x = center_x + eye_forward
                    eye1_y = center_y - eye_side
                    eye2_x = center_x + eye_forward
                    eye2_y = center_y + eye_side
                elif dx == -1:  # 向左移动
                    eye1_x = center_x - eye_forward
                    eye1_y = center_y - eye_side
                    eye2_x = center_x - eye_forward
                    eye2_y = center_y + eye_side
                elif dy == -1:  # 向上移动
                    eye1_x = center_x - eye_side
                    eye1_y = center_y - eye_forward
                    eye2_x = center_x + eye_side
                    eye2_y = center_y - eye_forward
                else:  # 向下移动 (dy == 1)
                    eye1_x = center_x - eye_side
                    eye1_y = center_y + eye_forward
                    eye2_x = center_x + eye_side
                    eye2_y = center_y + eye_forward
                
                # 绘制眼睛（白色高光，带发光效果）
                eye_alpha = min(alpha, 255)
                # 眼睛发光层
                for r in range(eye_size + 2, eye_size, -1):
                    eye_glow_alpha = int(60 * (1 - (r - eye_size) / 2))
                    s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 255, 255, eye_glow_alpha), (r, r), r)
                    self.screen.blit(s, (eye1_x - r, eye1_y - r))
                    self.screen.blit(s, (eye2_x - r, eye2_y - r))
                
                # 绘制眼睛（白色）
                pygame.draw.circle(self.screen, (255, 255, 255), (eye1_x, eye1_y), eye_size)
                pygame.draw.circle(self.screen, (255, 255, 255), (eye2_x, eye2_y), eye_size)
                
                # 眼睛内部小黑点（瞳孔）
                pupil_size = max(1, eye_size // 2)
                pygame.draw.circle(self.screen, (0, 0, 0), (eye1_x, eye1_y), pupil_size)
                pygame.draw.circle(self.screen, (0, 0, 0), (eye2_x, eye2_y), pupil_size)

    def draw_foods(self):
        """绘制食物（带霓虹发光和脉冲效果）"""
        pulse = abs((pygame.time.get_ticks() % 1000) / 500 - 1)  # 0-1-0 脉冲
        
        if self.food_pos:
            x, y = self.food_pos
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
            
            # 发光层（脉冲效果）
            glow_radius = int(CELL_SIZE * 0.8 + pulse * 8)
            for r in range(glow_radius, CELL_SIZE // 2, -2):
                alpha = int(60 * (1 - (glow_radius - r) / glow_radius))
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*FOOD_GLOW, alpha), (r, r), r)
                self.screen.blit(s, (cx - r, cy - r))
            
            # 实体
            pygame.draw.circle(self.screen, FOOD_COLOR, (cx, cy), CELL_SIZE // 2 - 2)
            # 高光
            pygame.draw.circle(self.screen, (255, 150, 200), (cx - 3, cy - 3), CELL_SIZE // 4)

        if self.energy_food_pos:
            x, y = self.energy_food_pos
            rect = pygame.Rect(x * CELL_SIZE, GAME_AREA_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # 发光层（脉冲效果）
            glow_size = int(pulse * 6)
            for offset in range(6, 0, -1):
                glow_rect = pygame.Rect(
                    x * CELL_SIZE - offset - glow_size,
                    GAME_AREA_Y + y * CELL_SIZE - offset - glow_size,
                    CELL_SIZE + (offset + glow_size) * 2,
                    CELL_SIZE + (offset + glow_size) * 2
                )
                alpha_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                alpha = 40 // offset
                pygame.draw.rect(alpha_surf, (*ENERGY_GLOW, alpha), alpha_surf.get_rect(), border_radius=10)
                self.screen.blit(alpha_surf, glow_rect)
            
            # 实体（菱形）
            center_x = x * CELL_SIZE + CELL_SIZE // 2
            center_y = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
            points = [
                (center_x, center_y - CELL_SIZE // 2 + 2),
                (center_x + CELL_SIZE // 2 - 2, center_y),
                (center_x, center_y + CELL_SIZE // 2 - 2),
                (center_x - CELL_SIZE // 2 + 2, center_y)
            ]
            pygame.draw.polygon(self.screen, ENERGY_FOOD_COLOR, points)
            # 内部高光
            inner_points = [
                (center_x, center_y - CELL_SIZE // 4),
                (center_x + CELL_SIZE // 4, center_y),
                (center_x, center_y + CELL_SIZE // 4),
                (center_x - CELL_SIZE // 4, center_y)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 150), inner_points)
    
    def draw_items(self):
        """绘制道具"""
        if self.item_pos and self.item_type:
            x, y = self.item_pos
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
            
            pulse = abs((pygame.time.get_ticks() % 1000) / 500 - 1)
            
            if self.item_type == ITEM_MAGNET:
                # 磁铁：黄色方形
                size = int(CELL_SIZE * 0.6 + pulse * 4)
                rect = pygame.Rect(cx - size//2, cy - size//2, size, size)
                pygame.draw.rect(self.screen, MAGNET_COLOR, rect)
                pygame.draw.rect(self.screen, (255, 255, 150), rect, 2)
            
            elif self.item_type == ITEM_BOMB:
                # 炸弹：黑色圆形
                radius = int(CELL_SIZE * 0.3 + pulse * 3)
                pygame.draw.circle(self.screen, BOMB_COLOR, (cx, cy), radius)
                pygame.draw.circle(self.screen, (50, 50, 50), (cx, cy), radius, 2)
                # 引线
                pygame.draw.line(self.screen, (100, 100, 100), (cx, cy - radius), (cx - 3, cy - radius - 5), 2)
            
            elif self.item_type == ITEM_SCISSORS:
                # 剪刀：绿色X形
                size = CELL_SIZE // 2
                pygame.draw.line(self.screen, SCISSORS_COLOR, (cx - size, cy - size), (cx + size, cy + size), 3)
                pygame.draw.line(self.screen, SCISSORS_COLOR, (cx + size, cy - size), (cx - size, cy + size), 3)
            
            elif self.item_type == ITEM_ROTTEN_APPLE:
                # 腐烂苹果：紫色圆形，带骷髅
                radius = int(CELL_SIZE * 0.4)
                pygame.draw.circle(self.screen, ROTTEN_APPLE_COLOR, (cx, cy), radius)
                # 简单的骷髅标志（X）
                pygame.draw.line(self.screen, (255, 255, 255), (cx - 5, cy - 5), (cx + 5, cy + 5), 2)
                pygame.draw.line(self.screen, (255, 255, 255), (cx + 5, cy - 5), (cx - 5, cy + 5), 2)
    
    def draw_portals(self):
        """绘制传送门"""
        for portal_pos, color_id in self.portals:
            x, y = portal_pos
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
            
            portal = Portal(portal_pos, color_id)
            color = portal.color
            
            # 旋转效果
            angle = (pygame.time.get_ticks() % 2000) / 2000 * 360
            pulse = abs((pygame.time.get_ticks() % 1000) / 500 - 1)
            
            # 外圈
            radius = int(CELL_SIZE * 0.4 + pulse * 3)
            for r in range(radius, radius - 5, -1):
                alpha = int(100 * (1 - (radius - r) / 5))
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*color, alpha), (r, r), r)
                self.screen.blit(s, (cx - r, cy - r))
            
            # 内圈
            pygame.draw.circle(self.screen, color, (cx, cy), radius - 5)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), radius - 8)
    
    def draw_spikes(self):
        """绘制地刺"""
        for spike in self.spikes:
            if spike.visible:
                x, y = spike.pos
                cx = x * CELL_SIZE + CELL_SIZE // 2
                cy = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
                
                # 红色三角形地刺
                points = [
                    (cx, cy - CELL_SIZE // 2),
                    (cx - CELL_SIZE // 3, cy + CELL_SIZE // 3),
                    (cx + CELL_SIZE // 3, cy + CELL_SIZE // 3)
                ]
                pygame.draw.polygon(self.screen, (255, 0, 0), points)
                pygame.draw.polygon(self.screen, (255, 100, 100), points, 2)
    
    def draw_shadow_snakes(self):
        """绘制影子蛇"""
        for shadow_snake in self.shadow_snakes:
            for i, (x, y) in enumerate(shadow_snake.snake):
                center_x = x * CELL_SIZE + CELL_SIZE // 2
                center_y = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
                
                # 半透明的暗色蛇
                radius = int(CELL_SIZE * 0.35)
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                color = (100, 100, 100, 180) if i == 0 else (80, 80, 80, 150)
                pygame.draw.circle(s, color, (radius, radius), radius)
                self.screen.blit(s, (center_x - radius, center_y - radius))
    
    def draw_ghost_hunters(self):
        """绘制幽灵猎手"""
        for hunter in self.ghost_hunters:
            if hunter.visible:
                x, y = hunter.pos
                cx = x * CELL_SIZE + CELL_SIZE // 2
                cy = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
                
                # 红色半透明幽灵
                radius = int(CELL_SIZE * 0.4)
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                # 闪烁效果
                alpha = int(150 + 50 * abs((pygame.time.get_ticks() % 1000) / 500 - 1))
                pygame.draw.circle(s, (255, 0, 0, alpha), (radius, radius), radius)
                self.screen.blit(s, (cx - radius, cy - radius))
                
                # 眼睛
                pygame.draw.circle(self.screen, (255, 255, 255), (cx - 3, cy - 2), 2)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx + 3, cy - 2), 2)
    
    def draw_boss(self):
        """绘制Boss"""
        if self.boss:
            x, y = self.boss.pos
            cx = x * CELL_SIZE + CELL_SIZE // 2
            cy = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
            
            # 绘制护盾效果
            if self.boss.shield_active:
                shield_progress = (pygame.time.get_ticks() - self.boss.shield_start_time) / BOSS_SHIELD_DURATION
                shield_alpha = int(100 * (1 - shield_progress))
                radius = CELL_SIZE * (BOSS_SIZE // 2 + 1)
                for r in range(int(radius), int(radius - 5), -1):
                    s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (0, 255, 255, shield_alpha), (r, r), r)
                    self.screen.blit(s, (cx - r, cy - r))
            
            # 绘制Boss主体（3x3方块）
            size = CELL_SIZE * BOSS_SIZE
            rect = pygame.Rect(cx - size//2, cy - size//2, size, size)
            pygame.draw.rect(self.screen, (200, 0, 0), rect)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 3)
            
            # 绘制子弹
            for bullet in self.boss.bullets:
                bx = int(bullet['x'] * CELL_SIZE + CELL_SIZE // 2)
                by = int(GAME_AREA_Y + bullet['y'] * CELL_SIZE + CELL_SIZE // 2)
                pygame.draw.circle(self.screen, (255, 255, 0), (bx, by), 4)

    def draw_obstacles(self):
        """绘制荆棘障碍（赛博朋克风格）"""
        for x, y in self.obstacles:
            center_x = x * CELL_SIZE + CELL_SIZE // 2
            center_y = GAME_AREA_Y + y * CELL_SIZE + CELL_SIZE // 2
            
            # 发光层（圆形扩散）
            for r in range(18, 8, -2):
                alpha = int(60 * (18 - r) / 18)
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*OBSTACLE_GLOW, alpha), (r, r), r)
                self.screen.blit(s, (center_x - r, center_y - r))
            
            # 中心危险标志（X形）
            danger_color = OBSTACLE_COLOR
            line_width = 3
            offset = CELL_SIZE // 3
            
            # X 的两条线
            pygame.draw.line(
                self.screen, danger_color,
                (center_x - offset, center_y - offset),
                (center_x + offset, center_y + offset),
                line_width
            )
            pygame.draw.line(
                self.screen, danger_color,
                (center_x + offset, center_y - offset),
                (center_x - offset, center_y + offset),
                line_width
            )
            
            # 四个方向的尖刺
            spike_length = CELL_SIZE // 2 - 2
            spike_width = 6
            
            # 上尖刺
            spike_top = [
                (center_x, center_y - spike_length),
                (center_x - spike_width, center_y),
                (center_x + spike_width, center_y)
            ]
            pygame.draw.polygon(self.screen, danger_color, spike_top)
            pygame.draw.polygon(self.screen, (255, 100, 255), spike_top, 2)
            
            # 下尖刺
            spike_bottom = [
                (center_x, center_y + spike_length),
                (center_x - spike_width, center_y),
                (center_x + spike_width, center_y)
            ]
            pygame.draw.polygon(self.screen, danger_color, spike_bottom)
            pygame.draw.polygon(self.screen, (255, 100, 255), spike_bottom, 2)
            
            # 左尖刺
            spike_left = [
                (center_x - spike_length, center_y),
                (center_x, center_y - spike_width),
                (center_x, center_y + spike_width)
            ]
            pygame.draw.polygon(self.screen, danger_color, spike_left)
            pygame.draw.polygon(self.screen, (255, 100, 255), spike_left, 2)
            
            # 右尖刺
            spike_right = [
                (center_x + spike_length, center_y),
                (center_x, center_y - spike_width),
                (center_x, center_y + spike_width)
            ]
            pygame.draw.polygon(self.screen, danger_color, spike_right)
            pygame.draw.polygon(self.screen, (255, 100, 255), spike_right, 2)
            
            # 中心圆点
            pygame.draw.circle(self.screen, (255, 0, 200), (center_x, center_y), 4)
            pygame.draw.circle(self.screen, (255, 150, 255), (center_x, center_y), 2)

    def draw_hud(self):
        """绘制HUD（赛博朋克风格，显示在屏幕上方）"""
        # 绘制半透明背景条
        hud_height = 30
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill((10, 5, 20, 200))  # 半透明深色背景
        self.screen.blit(hud_surface, (0, 0))
        
        # 左上角：分数 / 能量 / 幽灵剩余时间
        time_left = 0
        if self.ghost_mode:
            time_left = max(0, (self.ghost_end_time - pygame.time.get_ticks()) // 1000)

        combo_text = ""
        if self.combo_multiplier > 1:
            combo_text = f"  连击x{self.combo_multiplier}"
        
        text = f"分数: {self.score}   能量: {self.energy}   "
        if self.ghost_mode:
            text += f"幽灵模式: {time_left}秒"
        else:
            text += "幽灵模式: 关闭"
        text += combo_text

        # 计算垂直居中位置
        text_surf = self.font_small.render(text, True, TEXT_COLOR)
        text_height = text_surf.get_height()
        hud_center_y = (HUD_HEIGHT - text_height) // 2

        self.draw_text_with_glow(text, self.font_small, TEXT_COLOR, (8, hud_center_y))

        # 右上角显示最高分
        if self.leaderboard:
            high_score_text = f"最高分: {self.leaderboard[0]['score']}"
            high_score_surf = self.font_small.render(high_score_text, True, (255, 215, 0))
            high_score_height = high_score_surf.get_height()
            high_score_y = (HUD_HEIGHT - high_score_height) // 2
            self.draw_text_with_glow(high_score_text, self.font_small, (255, 215, 0), (SCREEN_WIDTH - 120, high_score_y))

    def draw_game_over(self):
        """绘制Game Over界面（赛博朋克风格）"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((10, 5, 20))
        self.screen.blit(overlay, (0, 0))

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # 标题带闪烁效果
        blink = (pygame.time.get_ticks() // 500) % 2
        title_color = (255, 0, 127) if blink else (255, 50, 150)
        self.draw_text_with_glow("游戏结束", self.font_big, title_color, (center_x, center_y - 60), center=True)
        
        self.draw_text_with_glow(self.game_over_reason, self.font_small, TEXT_COLOR, (center_x, center_y - 10), center=True)
        self.draw_text_with_glow(f"最终得分: {self.score}", self.font_small, (255, 255, 0), (center_x, center_y + 60), center=True)
        
        # 显示最高分（在中间区域，字体更大，和开始界面一样，位置再往下一点）
        if self.leaderboard:
            high_score_text = f"最高分: {self.leaderboard[0]['score']} ({self.leaderboard[0]['name']})"
            self.draw_text_with_glow(high_score_text, self.font_medium, (255, 215, 0), (center_x, center_y + 90), center=True)
        else:
            self.draw_text_with_glow("暂无最高分", self.font_medium, (150, 150, 150), (center_x, center_y + 90), center=True)
        
        # 提示移到屏幕下方
        self.draw_text_with_glow("按 R 重新开始，Tab 查看排行榜，ESC 返回开始界面", self.font_small, (200, 200, 220), (center_x, SCREEN_HEIGHT - 40), center=True)

    def draw_start_screen(self):
        """绘制开始界面（赛博朋克风格）"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(210)
        overlay.fill((10, 5, 20))
        self.screen.blit(overlay, (0, 0))

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # 标题带脉冲效果
        pulse = abs((pygame.time.get_ticks() % 2000) / 1000 - 1)
        title_color = (
            int(255),
            int(100 + pulse * 100),
            int(200 + pulse * 55)
        )
        self.draw_text_with_glow("技能贪吃蛇", self.font_xlarge, title_color, (center_x, center_y - 60), center=True)
        self.draw_text_with_glow("幽灵模式 + 动态障碍", self.font_small, TEXT_COLOR, (center_x, center_y - 10), center=True)
        
        # 显示最高分（在中间区域，字体更大，位置再往下一点）
        if self.leaderboard:
            high_score_text = f"最高分: {self.leaderboard[0]['score']} ({self.leaderboard[0]['name']})"
            self.draw_text_with_glow(high_score_text, self.font_medium, (255, 215, 0), (center_x, center_y + 80), center=True)
        else:
            self.draw_text_with_glow("暂无记录", self.font_medium, (150, 150, 150), (center_x, center_y + 40), center=True)
        
        # 提示文字移到屏幕下方（带闪烁）
        blink = (pygame.time.get_ticks() // 800) % 2
        tip_alpha = 220 if blink else 150
        tip_color = (tip_alpha, tip_alpha, 255)
        # 按空格开始提示
        self.draw_text_with_glow("按空格键开始 (ESC 退出)", self.font_small, tip_color, (center_x, SCREEN_HEIGHT - 60), center=True)
        # 操作提示
        self.draw_text_with_glow("方向键/WASD 移动；空格开启幽灵模式；Tab 暂停并查看排行榜", self.font_small, (190, 190, 210), (center_x, SCREEN_HEIGHT - 35), center=True)

    def draw_leaderboard(self):
        """绘制排行榜界面（赛博朋克风格）"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((10, 5, 20))
        self.screen.blit(overlay, (0, 0))

        center_x = SCREEN_WIDTH // 2
        self.draw_text_with_glow("排行榜 TOP 10", self.font_big, (255, 215, 0), (center_x, 40), center=True)
        
        # 只在游戏进行中时显示暂停提示
        if self.started and not self.game_over:
            self.draw_text_with_glow("(游戏已暂停)", self.font_small, (180, 180, 210), (center_x, 75), center=True)
            y_start = 110
        else:
            y_start = 90

        if not self.leaderboard:
            self.draw_text_with_glow("暂无记录", self.font_small, TEXT_COLOR, (center_x, y_start + 40), center=True)
        else:
            y_offset = y_start
            current_time = pygame.time.get_ticks()
            for i, entry in enumerate(self.leaderboard[:MAX_LEADERBOARD_ENTRIES]):
                rank_text = f"{i+1}. {entry['name']}"
                score_text = f"{entry['score']}"
                
                # 前三名用不同颜色和特效
                if i == 0:
                    # 第一名：金色，闪烁效果（与第二名交换）
                    blink = (current_time // 300) % 2
                    if blink:
                        color = (255, 215, 0)  # 亮金色
                    else:
                        color = (200, 180, 0)  # 暗金色
                    # 添加发光边框
                    for glow_offset in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                        glow_surf = self.font_small.render(rank_text, True, (255, 200, 50))
                        self.screen.blit(glow_surf, (center_x - 150 + glow_offset[0], y_offset + glow_offset[1]))
                        glow_surf2 = self.font_small.render(score_text, True, (255, 200, 50))
                        self.screen.blit(glow_surf2, (center_x + 100 + glow_offset[0], y_offset + glow_offset[1]))
                elif i == 1:
                    # 第二名：紫色，脉冲效果（与第一名交换，颜色改为紫色）
                    pulse = abs((current_time % 1500) / 750 - 1)
                    color = (
                        int(200 + pulse * 55),
                        int(100 + pulse * 100),
                        int(255)
                    )
                    # 添加额外的发光效果
                    for glow_offset in range(3, 0, -1):
                        glow_alpha = int(40 * pulse / glow_offset)
                        glow_color = tuple(min(255, c + 50) for c in color)
                        glow_surf = self.font_small.render(rank_text, True, glow_color)
                        glow_surf.set_alpha(glow_alpha)
                        self.screen.blit(glow_surf, (center_x - 150 - glow_offset, y_offset - glow_offset))
                        glow_surf2 = self.font_small.render(score_text, True, glow_color)
                        glow_surf2.set_alpha(glow_alpha)
                        self.screen.blit(glow_surf2, (center_x + 100 - glow_offset, y_offset - glow_offset))
                elif i == 2:
                    # 第三名：品红，无特效
                    color = (255, 0, 255)  # 品红色
                else:
                    color = TEXT_COLOR

                self.draw_text_with_glow(rank_text, self.font_small, color, (center_x - 150, y_offset))
                self.draw_text_with_glow(score_text, self.font_small, color, (center_x + 100, y_offset))
                y_offset += 30

        self.draw_text_with_glow("按 Tab 返回", self.font_small, (200, 200, 220), (center_x, SCREEN_HEIGHT - 40), center=True)

    def draw_bottom_bar(self):
        """绘制底部技能提示栏"""
        if self.energy > 0 and not self.game_over:
            # 只有在有能量且游戏进行中时显示
            bar_y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT
            
            # 绘制半透明背景
            bar_surface = pygame.Surface((SCREEN_WIDTH, BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
            bar_surface.fill((10, 5, 20, 180))
            self.screen.blit(bar_surface, (0, bar_y))

            # 提示文字闪烁
            blink = (pygame.time.get_ticks() // 400) % 2
            if blink:
                prompt_text = "按空格使用幽灵模式技能"
                prompt_color = (255, 255, 0) # Yellow
                center_x = SCREEN_WIDTH // 2
                center_y = bar_y + BOTTOM_BAR_HEIGHT // 2
                self.draw_text_with_glow(prompt_text, self.font_small, prompt_color, (center_x, center_y), center=True)

    def draw_name_input(self):
        """绘制输入名字界面（赛博朋克风格）"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((10, 5, 20))
        self.screen.blit(overlay, (0, 0))

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # 恭喜文字带闪烁
        blink = (pygame.time.get_ticks() // 300) % 2
        congrats_color = (255, 215, 0) if blink else (255, 255, 0)
        self.draw_text_with_glow("新纪录！", self.font_big, congrats_color, (center_x, center_y - 80), center=True)
        self.draw_text_with_glow("请输入你的名字：", self.font_small, TEXT_COLOR, (center_x, center_y - 30), center=True)
        
        # 输入框（霓虹边框）
        input_box_width = 300
        input_box_height = 40
        input_box = pygame.Rect(center_x - input_box_width//2, center_y, input_box_width, input_box_height)
        
        # 绘制发光边框
        for offset in range(3, 0, -1):
            glow_rect = input_box.inflate(offset * 2, offset * 2)
            pygame.draw.rect(self.screen, (0, 100, 200, 80 // offset), glow_rect, 2, border_radius=5)
        
        pygame.draw.rect(self.screen, (30, 20, 50), input_box, border_radius=3)
        pygame.draw.rect(self.screen, (0, 255, 255), input_box, 2, border_radius=3)
        
        # 显示输入的文字
        cursor_blink = "_" if (pygame.time.get_ticks() // 500) % 2 else " "
        self.draw_text_with_glow(self.player_name_input + cursor_blink, self.font_small, (255, 255, 255), (input_box.x + 10, input_box.y + 10))

        self.draw_text_with_glow("回车确认，ESC 跳过", self.font_small, (200, 200, 220), (center_x, center_y + 60), center=True)

    # -------------------- 主循环 --------------------
    def run(self):
        while True:
            self.handle_input()

            # 启动画面：未开始时仅渲染，不更新逻辑
            if not self.started:
                self.screen.fill(BG_COLOR)
                self.draw_grid()
                self.draw_obstacles()
                self.draw_spikes()
                self.draw_portals()
                self.draw_foods()
                self.draw_items()
                self.draw_snake()
                self.draw_shadow_snakes()
                self.draw_ghost_hunters()
                self.draw_boss()
                self.draw_hud()
                self.draw_start_screen()
                
                # 启动画面也可以查看排行榜
                if self.show_leaderboard:
                    self.draw_leaderboard()
                
                pygame.display.flip()
                self.clock.tick(self.fps)
                continue

            # Game Over input is now handled in handle_input()
            if self.game_over and not self.entering_name:
                pass # All input is handled in handle_input() now

            # 只在游戏进行中且未暂停时更新逻辑
            if not self.game_over and not self.paused:
                self.update()
            
            # 粒子系统始终更新（即使游戏暂停）
            self.particle_system.update()

            self.screen.fill(BG_COLOR)
            self.draw_grid()
            self.draw_obstacles()
            self.draw_spikes()
            self.draw_portals()
            self.draw_foods()
            self.draw_items()
            self.draw_snake()
            self.draw_shadow_snakes()
            self.draw_ghost_hunters()
            self.draw_boss()
            
            # 绘制粒子特效（在蛇上面）
            self.particle_system.draw(self.screen)
            
            # 绘制迷雾（在最上层）
            self.draw_fog()
            
            self.draw_hud()
            self.draw_bottom_bar() # Draw the new bottom bar

            if self.game_over:
                self.draw_game_over()

            # 显示排行榜（覆盖在游戏画面上）
            if self.show_leaderboard:
                self.draw_leaderboard()

            # 显示名字输入界面（覆盖在 game over 上）
            if self.entering_name:
                self.draw_name_input()

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    # 防止多次导入时自动运行
    game = SnakeGame()
    game.run()


