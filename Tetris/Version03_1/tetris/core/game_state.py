"""游戏状态管理"""

from enum import Enum
from typing import Optional


class GameState(Enum):
    """游戏状态枚举"""
    START = "start"
    PLAYING = "playing"
    PAUSED = "paused"
    HELP = "help"
    GAME_OVER = "gameover"


class StateMachine:
    """游戏状态机"""

    # 状态转换规则
    TRANSITIONS = {
        GameState.START: [GameState.PLAYING, GameState.HELP],
        GameState.PLAYING: [GameState.PAUSED, GameState.HELP, GameState.GAME_OVER],
        GameState.PAUSED: [GameState.PLAYING],
        GameState.HELP: [GameState.START, GameState.PLAYING, GameState.PAUSED],
        GameState.GAME_OVER: [GameState.PLAYING],
    }

    def __init__(self):
        self._state = GameState.START
        self._previous_state: Optional[GameState] = None

    def get_state(self) -> GameState:
        """获取当前状态"""
        return self._state

    def set_state(self, state: GameState) -> bool:
        """设置状态，返回是否成功"""
        if self.can_transition(self._state, state):
            self._previous_state = self._state
            self._state = state
            return True
        return False

    def can_transition(self, from_state: GameState, to_state: GameState) -> bool:
        """检查是否可以转换"""
        allowed = self.TRANSITIONS.get(from_state, [])
        return to_state in allowed

    def get_previous_state(self) -> Optional[GameState]:
        """获取上一个状态"""
        return self._previous_state

    def restore_previous_state(self) -> bool:
        """恢复上一个状态"""
        if self._previous_state and self.can_transition(self._state, self._previous_state):
            self._state = self._previous_state
            self._previous_state = None
            return True
        return False

    def reset(self) -> None:
        """重置状态机"""
        self._state = GameState.START
        self._previous_state = None