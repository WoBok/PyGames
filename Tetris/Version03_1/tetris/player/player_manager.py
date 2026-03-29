"""玩家管理器"""

from typing import List, Optional, Dict
import pygame

from .player import Player
from ..config import GameConfig
from ..audio import SoundManager
from ..input import KeyBindings


class PlayerManager:
    """多玩家管理器"""

    def __init__(
        self,
        config: Optional[GameConfig] = None,
        sound_manager: Optional[SoundManager] = None
    ):
        self.config = config or GameConfig()
        self.sound_manager = sound_manager
        self.players: List[Player] = []

    def add_player(
        self,
        player_id: str,
        board_position: tuple = (0, 0),
        key_bindings: Optional[KeyBindings] = None
    ) -> Player:
        """添加玩家"""
        player = Player(
            player_id,
            self.config,
            board_position,
            key_bindings,
            self.sound_manager
        )
        self.players.append(player)
        return player

    def remove_player(self, player_id: str) -> None:
        """移除玩家"""
        self.players = [p for p in self.players if p.player_id != player_id]

    def get_player(self, player_id: str) -> Optional[Player]:
        """获取玩家"""
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_all_players(self) -> List[Player]:
        """获取所有玩家"""
        return self.players

    def update_all(self, dt: float) -> None:
        """更新所有玩家"""
        for player in self.players:
            player.update(dt)

    def handle_input_all(self, event: pygame.event.Event, state: str) -> Optional[str]:
        """处理所有玩家输入"""
        for player in self.players:
            result = player.handle_input(event, state)
            if result:
                return result
        return None

    def handle_continuous_input_all(self, dt_ms: int, state: str) -> None:
        """处理所有玩家连续输入"""
        for player in self.players:
            player.handle_continuous_input(dt_ms, state)

    def render_all(self, renderer) -> None:
        """渲染所有玩家"""
        for player in self.players:
            player.render(renderer)

    def check_game_over(self) -> List[Player]:
        """检查游戏结束的玩家"""
        return [p for p in self.players if p.is_game_over()]

    def get_scores(self) -> Dict[str, int]:
        """获取所有玩家分数"""
        return {p.player_id: p.get_score() for p in self.players}

    def get_winners(self) -> List[Player]:
        """获取获胜者（分数最高）"""
        if not self.players:
            return []
        max_score = max(p.get_score() for p in self.players)
        return [p for p in self.players if p.get_score() == max_score]

    def reset_all(self) -> None:
        """重置所有玩家"""
        for player in self.players:
            player.engine.reset()
            player.effects.clear()

    def clear(self) -> None:
        """清除所有玩家"""
        self.players.clear()