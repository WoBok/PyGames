"""游戏引擎 - 核心逻辑"""

from typing import Optional, List, Tuple, Callable, Dict, Any
import random
import math

from ..config import GRID_WIDTH, GRID_HEIGHT, BOARD_X, BOARD_Y, GRID_SIZE, NEON_COLORS, GameConfig
from ..audio import SoundManager
from .board import Board
from .tetromino import Tetromino
from .scoring import ScoringSystem
from .game_state import GameState, StateMachine


class Event:
    """简单事件类"""

    def __init__(self):
        self._handlers: List[Callable] = []

    def subscribe(self, handler: Callable) -> None:
        """订阅事件"""
        self._handlers.append(handler)

    def unsubscribe(self, handler: Callable) -> None:
        """取消订阅"""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def emit(self, *args, **kwargs) -> None:
        """触发事件"""
        for handler in self._handlers:
            handler(*args, **kwargs)


class GameEngineEvents:
    """游戏引擎事件集合"""

    def __init__(self):
        self.piece_spawned = Event()  # 方块生成
        self.piece_moved = Event()    # 方块移动
        self.piece_rotated = Event()  # 方块旋转
        self.piece_locked = Event()   # 方块锁定
        self.lines_cleared = Event()  # 消行
        self.score_changed = Event()  # 分数变化
        self.level_up = Event()       # 升级
        self.combo_changed = Event()  # 连击变化
        self.game_over = Event()      # 游戏结束


class GameEngine:
    """游戏核心逻辑引擎"""

    def __init__(
        self,
        config: Optional[GameConfig] = None,
        sound_manager: Optional[SoundManager] = None
    ):
        self.config = config or GameConfig()
        self.board = Board(self.config)
        self.scoring = ScoringSystem()
        self.sound_manager = sound_manager
        self.events = GameEngineEvents()

        # 方块相关
        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None

        # 时间相关
        self.fall_timer = 0
        self.level_up_pause = False

        # 特效状态（供外部特效系统使用）
        self.clear_flash_lines: List[int] = []
        self.clear_flash_timer = 0
        self.shake_offset = [0, 0]
        self.level_up_effect = 0

        # 拖影
        self.trail_positions: List[Tuple[float, float, Tuple[int, int, int], float]] = []

        # 初始化
        self.reset()

    def reset(self) -> None:
        """重置游戏"""
        self.board.reset()
        self.scoring.reset()
        self.current_piece = None
        self.next_piece = self._new_piece()
        self._spawn_piece()
        self.fall_timer = 0
        self.level_up_pause = False
        self.clear_flash_lines = []
        self.clear_flash_timer = 0
        self.shake_offset = [0, 0]
        self.level_up_effect = 0
        self.trail_positions = []

    def _new_piece(self) -> Tetromino:
        """生成新方块"""
        return Tetromino.random_piece(self.config)

    def _spawn_piece(self) -> bool:
        """放置方块"""
        self.current_piece = self.next_piece
        self.current_piece.x = self.config.grid_width // 2 - 1
        self.current_piece.y = 0
        self.next_piece = self._new_piece()

        # 检查是否可以放置
        for x, y in self.current_piece.get_blocks():
            if y >= 0 and self.board.get_cell(x, y + 2) is not None:
                return False

        self.events.piece_spawned.emit(self.current_piece)
        return True

    def move_piece(
        self,
        dx: int,
        dy: int,
        add_trail: bool = False,
        is_natural_fall: bool = False,
        is_player_move: bool = False
    ) -> bool:
        """移动方块"""
        if not self.current_piece:
            return False

        if self.board.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy

            # 添加拖影
            if dy > 0 and add_trail:
                columns = {}
                for x, y in self.current_piece.get_blocks():
                    if x not in columns or y > columns[x]:
                        columns[x] = y
                for x, y in columns.items():
                    self.trail_positions.append(
                        (
                            self.config.board_x + x * self.config.grid_size + self.config.grid_size // 2,
                            self.config.board_y + (y - 2) * self.config.grid_size + self.config.grid_size // 2,
                            self.current_piece.color,
                            1.0
                        )
                    )

            # 播放音效
            if self.sound_manager:
                if is_natural_fall and self.current_piece.y >= 2:
                    self.sound_manager.play_sound('drop')
                elif is_player_move:
                    self.sound_manager.play_sound('move')

            self.events.piece_moved.emit(dx, dy)
            return True
        return False

    def rotate_piece(self) -> bool:
        """旋转方块"""
        if not self.current_piece:
            return False

        self.current_piece.rotate()

        # 踢墙测试
        if not self.board.is_valid_position(self.current_piece):
            for dx in [-1, 1, -2, 2]:
                if self.board.is_valid_position(self.current_piece, dx, 0):
                    self.current_piece.x += dx
                    if self.sound_manager:
                        self.sound_manager.play_sound('rotation')
                    self.events.piece_rotated.emit(self.current_piece.rotation)
                    return True
            self.current_piece.rotate_back()
            return False

        if self.sound_manager:
            self.sound_manager.play_sound('rotation')
        self.events.piece_rotated.emit(self.current_piece.rotation)
        return True

    def hard_drop(self) -> int:
        """硬降，返回下落距离"""
        if not self.current_piece:
            return 0

        drop_distance = 0
        while self.move_piece(0, 1, add_trail=True):
            drop_distance += 1

        if self.sound_manager:
            self.sound_manager.play_sound('plummet')

        self._lock_piece()
        return drop_distance

    def get_ghost_position(self) -> List[Tuple[int, int]]:
        """获取幽灵方块位置"""
        if not self.current_piece:
            return []

        ghost_y = self.current_piece.y
        while self.board.is_valid_position(self.current_piece, 0, ghost_y - self.current_piece.y + 1):
            ghost_y += 1

        shape = self.current_piece.shapes[self.current_piece.rotation % len(self.current_piece.shapes)]
        return [(self.current_piece.x + dx, ghost_y + dy) for dx, dy in shape]

    def _lock_piece(self) -> None:
        """锁定方块"""
        if not self.current_piece:
            return

        self.board.place_piece(self.current_piece)

        if self.sound_manager:
            self.sound_manager.play_sound('land')

        self.events.piece_locked.emit(self.current_piece)

        # 消行检测
        cleared, lines = self.board.clear_lines()
        if cleared > 0:
            self.clear_flash_lines = lines
            self.clear_flash_timer = 20
            self._process_clear(cleared, lines)
        else:
            self.scoring.reset_combo()

        # 生成新方块
        if not self._spawn_piece():
            self.events.game_over.emit()

    def _process_clear(self, lines_cleared: int, line_indices: List[int]) -> None:
        """处理消行"""
        # 播放音效
        if self.sound_manager:
            self.sound_manager.play_sound('clear_line')

        # 记录升级前的level
        old_level = self.scoring.level

        # 计分（可能会升级）
        score = self.scoring.calculate_score(lines_cleared)
        self.events.score_changed.emit(self.scoring.score, self.scoring.lines)
        self.events.lines_cleared.emit(lines_cleared, line_indices)

        # 连击
        if self.scoring.combo > 1:
            self.events.combo_changed.emit(self.scoring.combo)
            if self.sound_manager:
                self.sound_manager.play_combo(self.scoring.combo)

        # 升级检测（level已在calculate_score中更新）
        if self.scoring.level > old_level:
            self.level_up_effect = 45
            self.level_up_pause = True
            self.shake_offset = [random.randint(-10, 10), random.randint(-10, 10)]
            self.events.level_up.emit(self.scoring.level)
            if self.sound_manager:
                self.sound_manager.play_sound('level_up')

        # TETRIS特效触发
        if lines_cleared == 4:
            self.shake_offset = [random.randint(-12, 12), random.randint(-12, 12)]
            if self.sound_manager:
                self.sound_manager.play_sound('tetris')

    def update(self, dt: float) -> bool:
        """
        更新游戏状态
        返回是否成功下落（用于特效判断）
        """
        # 升级暂停期间使用最慢速度
        if self.level_up_pause:
            self.fall_timer += dt
            if self.fall_timer >= 1.0:
                self.fall_timer = 0
                if not self.move_piece(0, 1, is_natural_fall=True):
                    self._lock_piece()
                    return False
        else:
            self.fall_timer += dt
            if self.fall_timer >= self.scoring.fall_speed:
                self.fall_timer = 0
                if not self.move_piece(0, 1, is_natural_fall=True):
                    self._lock_piece()
                    return False

        return True

    def update_effects(self) -> None:
        """更新特效状态"""
        if self.clear_flash_timer > 0:
            self.clear_flash_timer -= 1

        if self.level_up_effect > 0:
            self.level_up_effect -= 1

        if self.level_up_effect <= 0 and self.level_up_pause:
            self.level_up_pause = False

        # 更新拖影
        new_trails = []
        for x, y, color, life in self.trail_positions:
            if life > 0:
                new_trails.append((x, y, color, life - 0.05))
        self.trail_positions = new_trails

    def is_game_over(self) -> bool:
        """是否游戏结束"""
        # 检查当前方块是否能放置
        if self.current_piece:
            for x, y in self.current_piece.get_blocks():
                if y >= 0 and self.board.get_cell(x, y) is not None:
                    return True
        return False

    def get_state_data(self) -> Dict[str, Any]:
        """获取完整状态数据（用于网络同步）"""
        return {
            'board': self.board.to_dict(),
            'current_piece': self.current_piece.to_dict() if self.current_piece else None,
            'next_piece_type': self.next_piece.type if self.next_piece else None,
            'scoring': self.scoring.to_dict(),
            'fall_timer': self.fall_timer,
        }

    def restore_state(self, data: Dict[str, Any]) -> None:
        """恢复状态数据"""
        self.board = Board.from_dict(data['board'], self.config)
        if data['current_piece']:
            self.current_piece = Tetromino.from_dict(data['current_piece'], self.config)
        else:
            self.current_piece = None
        if data['next_piece_type']:
            self.next_piece = Tetromino(data['next_piece_type'], self.config)
        else:
            self.next_piece = self._new_piece()
        self.scoring = ScoringSystem.from_dict(data['scoring'])
        self.fall_timer = data['fall_timer']