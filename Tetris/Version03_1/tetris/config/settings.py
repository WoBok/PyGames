"""配置模块 - 全局常量和设置"""

from typing import Dict, List, Tuple

# 方块尺寸（可配置）
GRID_SIZE = 32
BASE_WIDTH = 10  # 基准宽度（Level 1）
GRID_WIDTH = 10
GRID_HEIGHT = 20


def get_width_for_level(level: int) -> int:
    """根据关卡计算棋盘宽度"""
    return BASE_WIDTH + (level - 1)

# 游戏板尺寸
BOARD_WIDTH = GRID_WIDTH * GRID_SIZE
BOARD_HEIGHT = GRID_HEIGHT * GRID_SIZE
BOARD_X = 0
BOARD_Y = 0

# 面板尺寸
PANEL_WIDTH = 180
PANEL_X = BOARD_X + BOARD_WIDTH

# 屏幕尺寸
SCREEN_WIDTH = BOARD_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT

# 霓虹颜色映射
NEON_COLORS: Dict[str, Tuple[int, int, int]] = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (255, 0, 255),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 128, 255),
    'L': (255, 128, 0),
}

# 火花颜色列表
SPARK_COLORS: List[Tuple[int, int, int]] = [
    (255, 100, 50),
    (255, 150, 50),
    (255, 200, 100),
    (255, 255, 150),
    (255, 200, 200),
    (255, 100, 100),
    (100, 255, 255),
    (255, 100, 255),
]

# 方块形状定义（各旋转状态）
SHAPES: Dict[str, List[List[Tuple[int, int]]]] = {
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


class GameConfig:
    """游戏配置类 - 支持可配置参数"""

    def __init__(
        self,
        grid_size: int = GRID_SIZE,
        grid_width: int = GRID_WIDTH,
        grid_height: int = GRID_HEIGHT,
        board_x: int = BOARD_X,
        board_y: int = BOARD_Y,
        panel_width: int = PANEL_WIDTH,
    ):
        self.grid_size = grid_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.board_x = board_x
        self.board_y = board_y
        self.panel_width = panel_width
        self.initial_width = BASE_WIDTH  # 初始宽度（用于重置）

        # 计算派生尺寸
        self.board_width = grid_width * grid_size
        self.board_height = grid_height * grid_size
        self.panel_x = board_x + self.board_width
        self.screen_width = self.board_width + panel_width
        self.screen_height = self.board_height

    def update_width(self, new_width: int, left_offset: int = 0) -> None:
        """动态更新棋盘宽度"""
        self.grid_width = new_width
        self.board_width = new_width * self.grid_size
        # board_x 保持为 0，窗口宽度增加
        self.board_x = 0
        self.panel_x = self.board_width
        self.screen_width = self.board_width + self.panel_width

    def get_neon_color(self, piece_type: str) -> Tuple[int, int, int]:
        """获取方块颜色"""
        return NEON_COLORS.get(piece_type, (255, 255, 255))

    def get_shape(self, piece_type: str) -> List[List[Tuple[int, int]]]:
        """获取方块形状"""
        return SHAPES.get(piece_type, [])