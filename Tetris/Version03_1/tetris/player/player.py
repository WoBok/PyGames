"""玩家类"""

from typing import Optional, Tuple, Dict, Any
import random

import pygame

from ..config import GameConfig
from ..core import GameEngine, GameState
from ..audio import SoundManager
from ..effects import EffectManager
from ..input import InputHandler, KeyBindings
from ..rendering import Renderer


class Player:
    """单个玩家实例"""

    def __init__(
        self,
        player_id: str,
        config: Optional[GameConfig] = None,
        board_position: Tuple[int, int] = (0, 0),
        key_bindings: Optional[KeyBindings] = None,
        sound_manager: Optional[SoundManager] = None
    ):
        self.player_id = player_id
        self.config = config or GameConfig()

        # 覆盖配置中的位置
        self.board_position = board_position

        # 组件
        self.engine = GameEngine(self.config, sound_manager)
        self.effects = EffectManager(self.config)
        self.input_handler = InputHandler(key_bindings or KeyBindings.player1())
        self.sound_manager = sound_manager

        # 分数记录
        self.high_score = 0

        # 设置输入回调
        self._setup_input_callbacks()

        # 保存最后消除行的位置（用于Level Up和Combo显示）
        self._last_clear_y = None

    def _setup_input_callbacks(self) -> None:
        """设置输入回调"""
        ih = self.input_handler

        ih.on_move_left = lambda: self.engine.move_piece(-1, 0, is_player_move=True)
        ih.on_move_right = lambda: self.engine.move_piece(1, 0, is_player_move=True)
        ih.on_move_down = lambda: self.engine.move_piece(0, 1, add_trail=True, is_player_move=True)
        ih.on_rotate = self.engine.rotate_piece
        ih.on_hard_drop = self.engine.hard_drop
        ih.on_restart = self._restart_game

        # 订阅引擎事件以触发特效
        self.engine.events.lines_cleared.subscribe(self._on_lines_cleared)
        self.engine.events.level_up.subscribe(self._on_level_up)
        self.engine.events.combo_changed.subscribe(self._on_combo)

    def _on_lines_cleared(self, lines_count: int, line_indices: list) -> None:
        """消行事件处理"""
        # 使用消除行的位置计算Y坐标，并保存供Level Up和Combo使用
        if line_indices:
            avg_row = sum(line_indices) / len(line_indices)
            center_y = self.config.board_y + (avg_row - 2) * self.config.grid_size
            # 保存最后消除行的位置
            self._last_clear_y = center_y
        else:
            center_y = self.config.board_y + self.config.board_height // 2
            self._last_clear_y = center_y

        center_x = self.config.board_x + self.config.board_width // 2

        # 触发消行特效
        self.effects.trigger_line_clear(
            line_indices,
            self.config.board_x,
            self.config.board_y,
            self.engine.board.grid
        )

        # 计分浮动文字
        score = (lines_count ** 2) * (2 ** (self.engine.scoring.level - 1))
        if lines_count == 4:
            self.effects.add_floating_text(center_x, center_y, f"TETRIS! +{score}", (255, 255, 255), 20, True, 0)
            self.effects.trigger_tetris(center_y)
        else:
            self.effects.add_floating_text(center_x, center_y, f"+{score}", (255, 255, 255), 16, False, 0)

    def _on_level_up(self, level: int) -> None:
        """升级事件处理"""
        center_x = self.config.board_x + self.config.board_width // 2
        # 使用最后消除行的位置
        center_y = self._last_clear_y if self._last_clear_y else self.config.board_y + self.config.board_height // 2
        self.effects.trigger_level_up(center_x, center_y)

    def _on_combo(self, combo: int) -> None:
        """连击事件处理"""
        center_x = self.config.board_x + self.config.board_width // 2
        # 使用最后消除行的位置
        center_y = self._last_clear_y if self._last_clear_y else self.config.board_y + self.config.board_height // 2

        combo_bonus = (2 ** (combo - 1)) * (self.engine.scoring.level ** 2)
        self.effects.add_floating_text(
            center_x, center_y + 40,
            f"COMBO x{combo}! +{combo_bonus}",
            (255, 200, 0), 16, False, combo
        )
        self.effects.trigger_combo(combo, center_y)

    def _restart_game(self) -> None:
        """重新开始游戏"""
        self.engine.reset()
        self.effects.clear()
        if self.sound_manager:
            self.sound_manager.play_bgm()

    def update(self, dt: float) -> None:
        """更新玩家状态"""
        # 应用慢动作
        if self.effects.slow_motion_timer > 0:
            actual_dt = dt * self.effects.slow_motion_factor
        else:
            actual_dt = dt

        # 更新引擎
        self.engine.update(actual_dt)
        self.engine.update_effects()

        # 同步特效状态
        self.effects.block_flash = self.engine.shake_offset[0] / 10 if self.engine.level_up_effect > 0 else 0

        # 更新特效
        self.effects.update(dt)
        self.effects.update_particles()
        self.effects.update_floating_texts(dt)

    def handle_input(self, event: pygame.event.Event, state: str) -> Optional[str]:
        """处理输入事件"""
        return self.input_handler.handle_event(event, state)

    def handle_continuous_input(self, dt_ms: int, state: str) -> None:
        """处理连续输入"""
        self.input_handler.handle_continuous_input(dt_ms, state)

    def render(self, renderer: Renderer) -> None:
        """渲染玩家画面"""
        offset = self.board_position
        shake = tuple(self.effects.shake_offset)

        # 绘制网格
        renderer.draw_grid(self.engine.board, shake)

        # 绘制游戏板
        renderer.draw_board(self.engine.board, shake)

        # 绘制当前方块（传入幽灵位置和board用于碰撞检测）
        if self.engine.current_piece:
            ghost_positions = self.engine.get_ghost_position()
            renderer.draw_piece(
                self.engine.current_piece, shake,
                draw_ghost=True,
                ghost_positions=ghost_positions,
                board=self.engine.board
            )

        # 绘制预览方块
        renderer.draw_next_piece(self.engine.next_piece, offset)

        # 绘制特效
        self.effects.draw_effects(renderer.screen, shake)
        renderer.draw_trails(self.engine.trail_positions)
        self.effects.draw_particles(renderer.screen)
        self.effects.draw_floating_texts(renderer.screen, renderer.fonts.medium, renderer.fonts.font_name)
        self.effects.draw_level_up_effects(renderer.screen)

    def is_game_over(self) -> bool:
        """是否游戏结束"""
        return self.engine.is_game_over()

    def get_score(self) -> int:
        """获取分数"""
        return self.engine.scoring.score

    def get_level(self) -> int:
        """获取关卡"""
        return self.engine.scoring.level

    def get_lines(self) -> int:
        """获取消行数"""
        return self.engine.scoring.lines

    def get_state(self) -> Dict[str, Any]:
        """获取完整状态"""
        return {
            'player_id': self.player_id,
            'engine': self.engine.get_state_data(),
            'effects': self.effects.get_state(),
            'high_score': self.high_score,
        }

    def restore_state(self, state: Dict[str, Any]) -> None:
        """恢复状态"""
        self.player_id = state['player_id']
        self.engine.restore_state(state['engine'])
        self.effects.restore_state(state['effects'])
        self.high_score = state.get('high_score', 0)