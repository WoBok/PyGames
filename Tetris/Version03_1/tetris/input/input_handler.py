"""输入处理模块"""

import pygame
from typing import Dict, Callable, Optional, Tuple
from dataclasses import dataclass


@dataclass
class KeyBindings:
    """按键绑定配置"""
    left: int = pygame.K_LEFT
    right: int = pygame.K_RIGHT
    down: int = pygame.K_DOWN
    rotate: int = pygame.K_UP
    hard_drop: int = pygame.K_SPACE
    pause: int = pygame.K_p
    restart: int = pygame.K_r
    help: int = pygame.K_h

    @classmethod
    def player1(cls) -> 'KeyBindings':
        """玩家1按键绑定"""
        return cls()

    @classmethod
    def player2(cls) -> 'KeyBindings':
        """玩家2按键绑定"""
        return cls(
            left=pygame.K_a,
            right=pygame.K_d,
            down=pygame.K_s,
            rotate=pygame.K_w,
            hard_drop=pygame.K_LSHIFT,
            pause=pygame.K_ESCAPE,
            restart=pygame.K_r,
            help=pygame.K_h
        )


class InputHandler:
    """输入处理器"""

    def __init__(self, key_bindings: Optional[KeyBindings] = None):
        self.key_bindings = key_bindings or KeyBindings()

        # 按键重复计时器
        self.key_repeat_timers: Dict[int, int] = {}
        self.key_repeat_delay = 170  # 初始延迟（毫秒）
        self.key_repeat_interval = 50  # 重复间隔（毫秒）

        # 回调函数
        self.on_move_left: Optional[Callable] = None
        self.on_move_right: Optional[Callable] = None
        self.on_move_down: Optional[Callable] = None
        self.on_rotate: Optional[Callable] = None
        self.on_hard_drop: Optional[Callable] = None
        self.on_pause: Optional[Callable] = None
        self.on_restart: Optional[Callable] = None
        self.on_help: Optional[Callable] = None

    def handle_event(self, event: pygame.event.Event, state: str) -> Optional[str]:
        """
        处理输入事件
        返回新的游戏状态（如果需要切换）
        """
        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event.key, state)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event.key)

        return None

    def _handle_keydown(self, key: int, state: str) -> Optional[str]:
        """处理按键按下"""
        kb = self.key_bindings

        if state == "start":
            if key == kb.hard_drop:
                return "playing"
            elif key == kb.help:
                return "help_from_start"

        elif state == "help":
            if key == kb.help or key == pygame.K_ESCAPE:
                return "return_from_help"

        elif state == "playing":
            if key == kb.pause:
                return "paused"
            elif key == kb.help:
                return "help_from_playing"
            elif key == kb.left:
                self._trigger_callback(self.on_move_left)
                self.key_repeat_timers[kb.left] = self.key_repeat_delay
            elif key == kb.right:
                self._trigger_callback(self.on_move_right)
                self.key_repeat_timers[kb.right] = self.key_repeat_delay
            elif key == kb.down:
                self._trigger_callback(self.on_move_down)
                self.key_repeat_timers[kb.down] = self.key_repeat_delay
            elif key == kb.rotate:
                self._trigger_callback(self.on_rotate)
            elif key == kb.hard_drop:
                self._trigger_callback(self.on_hard_drop)
            elif key == kb.restart:
                self._trigger_callback(self.on_restart)

        elif state == "paused":
            if key == kb.pause:
                return "playing"

        elif state == "gameover":
            if key == kb.restart:
                self._trigger_callback(self.on_restart)
                return "playing"

        return None

    def _handle_keyup(self, key: int) -> None:
        """处理按键释放"""
        if key in self.key_repeat_timers:
            self.key_repeat_timers[key] = 0

    def handle_continuous_input(self, dt_ms: int, state: str) -> None:
        """处理连续输入（长按）"""
        if state != "playing":
            return

        keys = pygame.key.get_pressed()
        kb = self.key_bindings

        for key in [kb.left, kb.right, kb.down]:
            if keys[key]:
                if key in self.key_repeat_timers and self.key_repeat_timers[key] > 0:
                    self.key_repeat_timers[key] -= dt_ms
                    if self.key_repeat_timers[key] <= 0:
                        self.key_repeat_timers[key] = self.key_repeat_interval
                        if key == kb.left:
                            self._trigger_callback(self.on_move_left)
                        elif key == kb.right:
                            self._trigger_callback(self.on_move_right)
                        elif key == kb.down:
                            self._trigger_callback(self.on_move_down)

    def _trigger_callback(self, callback: Optional[Callable]) -> None:
        """触发回调"""
        if callback:
            callback()

    def reset_repeat_timers(self) -> None:
        """重置按键重复计时器"""
        self.key_repeat_timers.clear()