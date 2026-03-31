"""游戏板状态管理"""

from typing import List, Optional, Tuple
import random

from ..config import GRID_WIDTH, GRID_HEIGHT, NEON_COLORS, GameConfig, BASE_WIDTH
from .tetromino import Tetromino


class Board:
    """游戏板状态管理类 - 支持可配置尺寸"""

    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        self.width = self.config.grid_width
        self.height = self.config.grid_height
        self.left_offset = 0  # 左侧扩展的列数
        self.expand_side = 'right'  # 下一次扩展的方向：先右侧，再左侧
        # 游戏板网格（多2行用于上方缓冲）
        self.grid: List[List[Optional[str]]] = [
            [None for _ in range(self.width)]
            for _ in range(self.height + 2)
        ]

    def get_grid(self) -> List[List[Optional[str]]]:
        """获取网格数据"""
        return self.grid

    def get_cell(self, x: int, y: int) -> Optional[str]:
        """获取指定格子的内容"""
        if 0 <= y < len(self.grid) and 0 <= x < self.width:
            return self.grid[y][x]
        return None

    def set_cell(self, x: int, y: int, value: Optional[str]) -> None:
        """设置指定格子的内容"""
        if 0 <= y < len(self.grid) and 0 <= x < self.width:
            self.grid[y][x] = value

    def is_valid_position(self, piece: Tetromino, dx: int = 0, dy: int = 0) -> bool:
        """检查方块位置是否有效"""
        for x, y in piece.get_blocks():
            nx, ny = x + dx, y + dy
            # 检查边界
            if nx < 0 or nx >= self.width:
                return False
            if ny >= self.height + 2:
                return False
            # 检查碰撞
            if ny >= 0 and self.grid[ny][nx] is not None:
                return False
        return True

    def place_piece(self, piece: Tetromino) -> None:
        """放置方块到网格"""
        for x, y in piece.get_blocks():
            if 0 <= y < self.height + 2 and 0 <= x < self.width:
                self.grid[y][x] = piece.type

    def clear_lines(self) -> Tuple[int, List[int]]:
        """清除完整行，返回清除的行数和行号列表"""
        lines_to_clear = []
        for y in range(self.height + 2):
            if all(self.grid[y][x] is not None for x in range(self.width)):
                lines_to_clear.append(y)

        if lines_to_clear:
            for y in lines_to_clear:
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(self.width)])

        return len(lines_to_clear), lines_to_clear

    def is_game_over(self) -> bool:
        """检查是否游戏结束（检查缓冲区是否有方块）"""
        # 检查出生区域（前2行）是否有方块
        for y in range(2):
            for x in range(self.width):
                if self.grid[y][x] is not None:
                    return True
        return False

    def reset(self) -> None:
        """重置游戏板（恢复初始宽度）"""
        self.width = self.config.initial_width
        self.left_offset = 0
        self.expand_side = 'right'
        self.config.update_width(self.config.initial_width, left_offset=0)
        self.grid = [
            [None for _ in range(self.width)]
            for _ in range(self.height + 2)
        ]

    def expand_width(self, new_width: int) -> None:
        """扩展棋盘宽度（左右交替：先右侧，再左侧）"""
        if new_width <= self.width:
            return
        additional = new_width - self.width

        if self.expand_side == 'right':
            # 扩展右侧
            for row in self.grid:
                row.extend([None for _ in range(additional)])
            self.expand_side = 'left'
        else:
            # 扩展左侧：在每行开头插入空格，现有方块位置向右偏移
            for row in self.grid:
                row.insert(0, None)
            self.left_offset += 1
            self.expand_side = 'right'

        self.width = new_width
        self.config.update_width(new_width, left_offset=self.left_offset)

    def get_expand_side(self) -> str:
        """获取下一次扩展的方向"""
        return self.expand_side

    def get_row(self, y: int) -> List[Optional[str]]:
        """获取指定行"""
        if 0 <= y < len(self.grid):
            return self.grid[y]
        return []

    def copy(self) -> 'Board':
        """复制游戏板"""
        new_board = Board(self.config)
        new_board.grid = [row[:] for row in self.grid]
        return new_board

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            'width': self.width,
            'height': self.height,
            'grid': self.grid,
        }

    @classmethod
    def from_dict(cls, data: dict, config: Optional[GameConfig] = None) -> 'Board':
        """从字典反序列化"""
        board = cls(config)
        board.width = data['width']
        board.height = data['height']
        board.grid = data['grid']
        return board