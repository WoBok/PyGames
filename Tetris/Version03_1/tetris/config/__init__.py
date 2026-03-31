"""配置模块"""

from .settings import (
    GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, BASE_WIDTH,
    BOARD_WIDTH, BOARD_HEIGHT, BOARD_X, BOARD_Y,
    PANEL_WIDTH, PANEL_X, SCREEN_WIDTH, SCREEN_HEIGHT,
    NEON_COLORS, SPARK_COLORS, SHAPES,
    GameConfig, get_width_for_level,
)

__all__ = [
    'GRID_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT', 'BASE_WIDTH',
    'BOARD_WIDTH', 'BOARD_HEIGHT', 'BOARD_X', 'BOARD_Y',
    'PANEL_WIDTH', 'PANEL_X', 'SCREEN_WIDTH', 'SCREEN_HEIGHT',
    'NEON_COLORS', 'SPARK_COLORS', 'SHAPES',
    'GameConfig', 'get_width_for_level',
]