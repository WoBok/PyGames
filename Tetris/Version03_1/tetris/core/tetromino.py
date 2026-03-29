"""方块类模块"""

from typing import List, Tuple, Optional
import random
import copy

from ..config import NEON_COLORS, SHAPES, GRID_WIDTH, GameConfig


class Tetromino:
    """方块类"""

    def __init__(self, shape_type: str, config: Optional[GameConfig] = None):
        self.type = shape_type
        self.rotation = 0
        self.config = config or GameConfig()
        self.x = self.config.grid_width // 2 - 1
        self.y = 0
        self.color = NEON_COLORS.get(shape_type, (255, 255, 255))
        self.shapes = SHAPES.get(shape_type, [])

    def get_blocks(self) -> List[Tuple[int, int]]:
        """获取当前旋转状态下的所有方块坐标"""
        if not self.shapes:
            return []
        shape = self.shapes[self.rotation % len(self.shapes)]
        return [(self.x + dx, self.y + dy) for dx, dy in shape]

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """获取方块边界（最小x, 最大x, 最小y, 最大y）"""
        if not self.shapes:
            return (0, 0, 0, 0)
        shape = self.shapes[0]
        min_x = min(dx for dx, dy in shape)
        max_x = max(dx for dx, dy in shape)
        min_y = min(dy for dx, dy in shape)
        max_y = max(dy for dx, dy in shape)
        return min_x, max_x, min_y, max_y

    def rotate(self) -> None:
        """顺时针旋转"""
        if self.shapes:
            self.rotation = (self.rotation + 1) % len(self.shapes)

    def rotate_back(self) -> None:
        """逆时针旋转"""
        if self.shapes:
            self.rotation = (self.rotation - 1) % len(self.shapes)

    def clone(self) -> 'Tetromino':
        """克隆方块（用于状态同步）"""
        new_piece = Tetromino(self.type, self.config)
        new_piece.rotation = self.rotation
        new_piece.x = self.x
        new_piece.y = self.y
        return new_piece

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            'type': self.type,
            'rotation': self.rotation,
            'x': self.x,
            'y': self.y,
        }

    @classmethod
    def from_dict(cls, data: dict, config: Optional[GameConfig] = None) -> 'Tetromino':
        """从字典反序列化"""
        piece = cls(data['type'], config)
        piece.rotation = data['rotation']
        piece.x = data['x']
        piece.y = data['y']
        return piece

    @classmethod
    def random_piece(cls, config: Optional[GameConfig] = None) -> 'Tetromino':
        """生成随机方块"""
        shape_type = random.choice(list(SHAPES.keys()))
        return cls(shape_type, config)