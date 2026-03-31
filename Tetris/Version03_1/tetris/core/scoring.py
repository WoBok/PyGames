"""计分系统"""

from typing import Optional, Callable
from .tetromino import Tetromino


class ScoringSystem:
    """计分系统类"""

    def __init__(self):
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.fall_speed = 1.0
        self.lines_per_level = 10
        self.level_up_callback: Optional[Callable[[int], None]] = None

    def set_level_up_callback(self, callback: Callable[[int], None]) -> None:
        """设置升级回调函数"""
        self.level_up_callback = callback

    def calculate_score(self, lines_cleared: int) -> int:
        """计算得分，返回本次得分"""
        self.lines += lines_cleared

        # 基础得分：行数² × 倍率
        multiplier = 2 ** (self.level - 1)
        base_score = (lines_cleared ** 2) * multiplier
        self.score += base_score

        # 连击加分
        self.combo += 1
        combo_bonus = 0
        if self.combo > 1:
            combo_bonus = (2 ** (self.combo - 1)) * (self.level ** 2)
            self.score += combo_bonus

        # 检查升级
        new_level = self.lines // self.lines_per_level + 1
        if new_level > self.level:
            self.level = new_level
            self.update_fall_speed()
            if self.level_up_callback:
                self.level_up_callback(new_level)

        return base_score

    def get_combo_bonus(self) -> int:
        """获取当前连击奖励"""
        if self.combo > 1:
            return (2 ** (self.combo - 1)) * (self.level ** 2)
        return 0

    def update_fall_speed(self) -> None:
        """更新下落速度"""
        self.fall_speed = max(0.08, 1.0 - (self.level - 1) * 0.08)

    def get_fall_speed(self) -> float:
        """获取当前下落速度"""
        return self.fall_speed

    def reset_combo(self) -> None:
        """重置连击"""
        self.combo = 0

    def reset(self) -> None:
        """重置所有数据"""
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.fall_speed = 1.0

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            'score': self.score,
            'lines': self.lines,
            'level': self.level,
            'combo': self.combo,
            'fall_speed': self.fall_speed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScoringSystem':
        """从字典反序列化"""
        scoring = cls()
        scoring.score = data['score']
        scoring.lines = data['lines']
        scoring.level = data['level']
        scoring.combo = data['combo']
        scoring.fall_speed = data['fall_speed']
        return scoring