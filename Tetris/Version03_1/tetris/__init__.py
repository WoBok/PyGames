"""Tetris 游戏包"""

from .config import (
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT,
    BOARD_WIDTH, BOARD_HEIGHT, BOARD_X, BOARD_Y,
    PANEL_WIDTH, PANEL_X, SCREEN_WIDTH, SCREEN_HEIGHT,
    NEON_COLORS, SPARK_COLORS, SHAPES,
    GameConfig,
)
from .utils import get_resource_path, get_data_path
from .core import (
    Board, Tetromino, ScoringSystem,
    GameState, StateMachine, GameEngine,
    Event, GameEngineEvents
)
from .audio import SoundManager
from .effects import Particle, FloatingText, Star, EffectManager
from .rendering import SurfaceCache, BlockRenderer, FontManager, Renderer
from .input import InputHandler, KeyBindings
from .player import Player, PlayerManager
from .main import GameRunner, main

__all__ = [
    # config
    'GRID_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT',
    'BOARD_WIDTH', 'BOARD_HEIGHT', 'BOARD_X', 'BOARD_Y',
    'PANEL_WIDTH', 'PANEL_X', 'SCREEN_WIDTH', 'SCREEN_HEIGHT',
    'NEON_COLORS', 'SPARK_COLORS', 'SHAPES',
    'GameConfig',
    # utils
    'get_resource_path', 'get_data_path',
    # core
    'Board', 'Tetromino', 'ScoringSystem',
    'GameState', 'StateMachine', 'GameEngine',
    'Event', 'GameEngineEvents',
    # audio
    'SoundManager',
    # effects
    'Particle', 'FloatingText', 'Star', 'EffectManager',
    # rendering
    'SurfaceCache', 'BlockRenderer', 'FontManager', 'Renderer',
    # input
    'InputHandler', 'KeyBindings',
    # player
    'Player', 'PlayerManager',
    # main
    'GameRunner', 'main',
]