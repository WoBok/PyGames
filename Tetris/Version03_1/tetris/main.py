"""游戏主入口"""

import pygame
import random
from typing import Optional, List

# 使用绝对导入或直接导入模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tetris.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_WIDTH, BOARD_HEIGHT,
    GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, GameConfig
)
from tetris.core import GameEngine, GameState, StateMachine
from tetris.audio import SoundManager
from tetris.effects import Star, EffectManager
from tetris.rendering import Renderer, FontManager
from tetris.player import Player, PlayerManager
from tetris.utils import get_data_path, load_json_data, save_json_data


class GameRunner:
    """游戏运行器"""

    def __init__(self, num_players: int = 1):
        # 初始化pygame
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)

        # 配置
        self.config = GameConfig()

        # 创建窗口
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        try:
            self.screen = pygame.display.set_mode(
                (self.config.screen_width, self.config.screen_height),
                flags
            )
        except Exception:
            self.screen = pygame.display.set_mode(
                (self.config.screen_width, self.config.screen_height)
            )

        pygame.display.set_caption("Tetris - Neon Edition")

        # 时钟
        self.clock = pygame.time.Clock()

        # 音效
        self.sound_manager = SoundManager()

        # 渲染器
        self.renderer = Renderer(self.screen, self.config)

        # 状态机
        self.state_machine = StateMachine()
        self.previous_state = GameState.START

        # 高分
        self.high_score = self._load_high_score()

        # 玩家管理
        self.num_players = num_players
        self.player_manager = PlayerManager(self.config, self.sound_manager)
        self._setup_players()

        # 背景星星
        self.stars: List[Star] = []
        for _ in range(80):
            self.stars.append(Star(
                random.randint(0, self.config.screen_width),
                random.randint(0, self.config.screen_height),
                self.config.screen_width,
                self.config.screen_height
            ))

        # 时间
        self.time = 0

    def _setup_players(self) -> None:
        """设置玩家"""
        if self.num_players == 1:
            # 单人模式
            self.player_manager.add_player("player1", (0, 0))
        else:
            # 多人模式（需要调整布局）
            # TODO: 实现多人布局
            self.player_manager.add_player("player1", (0, 0))

    def _load_high_score(self) -> int:
        """加载最高分"""
        filepath = get_data_path("highscore.json")
        return load_json_data(filepath, "high_score", 0)

    def _save_high_score(self) -> None:
        """保存最高分"""
        filepath = get_data_path("highscore.json")
        save_json_data(filepath, {"high_score": self.high_score})

    def reset_game(self) -> None:
        """重置游戏"""
        self.player_manager.reset_all()
        self.sound_manager.stop_bgm()

    def handle_input(self, event: pygame.event.Event) -> None:
        """处理输入"""
        state = self.state_machine.get_state()
        state_str = state.value

        # 状态转换
        if event.type == pygame.KEYDOWN:
            if state == GameState.START:
                if event.key == pygame.K_SPACE:
                    self.state_machine.set_state(GameState.PLAYING)
                    self.sound_manager.play_bgm()
                elif event.key == pygame.K_h:
                    self.previous_state = state
                    self.state_machine.set_state(GameState.HELP)

            elif state == GameState.HELP:
                if event.key in (pygame.K_h, pygame.K_ESCAPE):
                    self.state_machine.restore_previous_state()

            elif state == GameState.PLAYING:
                if event.key == pygame.K_p:
                    self.state_machine.set_state(GameState.PAUSED)
                    self.sound_manager.pause_bgm()
                elif event.key == pygame.K_h:
                    self.previous_state = state
                    self.state_machine.set_state(GameState.HELP)
                elif event.key == pygame.K_r:
                    self.reset_game()
                    self.sound_manager.play_bgm()

            elif state == GameState.PAUSED:
                if event.key == pygame.K_p:
                    self.state_machine.set_state(GameState.PLAYING)
                    self.sound_manager.resume_bgm()

            elif state == GameState.GAME_OVER:
                if event.key == pygame.K_r:
                    self.reset_game()
                    self.state_machine.set_state(GameState.PLAYING)
                    self.sound_manager.play_bgm()

        # 玩家输入处理
        if self.state_machine.get_state() == GameState.PLAYING:
            for player in self.player_manager.get_all_players():
                player.handle_input(event, state_str)

    def handle_continuous_input(self, dt_ms: int) -> None:
        """处理连续输入"""
        state = self.state_machine.get_state()
        if state == GameState.PLAYING:
            for player in self.player_manager.get_all_players():
                player.handle_continuous_input(dt_ms, state.value)

    def update(self, dt: float) -> None:
        """更新游戏状态"""
        self.time += dt
        self.renderer.update(dt)

        state = self.state_machine.get_state()

        if state == GameState.PLAYING:
            # 更新背景音乐
            self.sound_manager.update_bgm(dt)

            # 更新玩家
            for player in self.player_manager.get_all_players():
                player.update(dt)

                # 检查游戏结束
                if player.is_game_over():
                    self.state_machine.set_state(GameState.GAME_OVER)
                    self.sound_manager.stop_bgm()
                    self.sound_manager.play_sound('game_over')

                    # 更新最高分
                    score = player.get_score()
                    if score > self.high_score:
                        self.high_score = score
                        self._save_high_score()

    def render(self) -> None:
        """渲染画面"""
        state = self.state_machine.get_state()

        if state == GameState.START:
            self.renderer.draw_start_screen()

        elif state == GameState.HELP:
            self.renderer.draw_help_screen()

        elif state == GameState.PLAYING:
            player = self.player_manager.get_player("player1")
            if player:
                # 背景
                self.renderer.draw_background(self.stars)

                # 分隔线
                self.renderer.draw_divider()

                # 面板
                self.renderer.draw_panel(
                    self.high_score,
                    player.get_score(),
                    player.get_lines(),
                    player.get_level(),
                    player.effects.level_up_effect
                )

                # 玩家渲染
                player.render(self.renderer)

        elif state == GameState.PAUSED:
            player = self.player_manager.get_player("player1")
            if player:
                self.renderer.draw_background(self.stars)
                self.renderer.draw_grid()
                self.renderer.draw_board(player.engine.board)
                if player.engine.current_piece:
                    self.renderer.draw_piece(player.engine.current_piece)
                self.renderer.draw_next_piece(player.engine.next_piece)
                self.renderer.draw_divider()
                self.renderer.draw_panel(
                    self.high_score,
                    player.get_score(),
                    player.get_lines(),
                    player.get_level()
                )
                self.renderer.draw_pause_screen()

        elif state == GameState.GAME_OVER:
            player = self.player_manager.get_player("player1")
            if player:
                self.renderer.draw_background(self.stars)
                self.renderer.draw_grid()
                self.renderer.draw_board(player.engine.board)
                self.renderer.draw_panel(
                    self.high_score,
                    player.get_score(),
                    player.get_lines(),
                    player.get_level()
                )
                self.renderer.draw_gameover_screen(
                    player.get_score(),
                    player.get_score() >= self.high_score
                )

        pygame.display.flip()

    def run(self) -> None:
        """运行游戏主循环"""
        running = True
        last_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            dt_ms = current_time - last_time
            last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_input(event)

            self.handle_continuous_input(dt_ms)
            self.update(dt)
            self.render()

            self.clock.tick(60)

        pygame.quit()


def main():
    """主函数"""
    game = GameRunner(num_players=1)
    game.run()


if __name__ == "__main__":
    main()