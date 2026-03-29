"""Tetris - Neon Edition

重构后的模块化俄罗斯方块游戏

使用方法:
    python main.py

模块结构:
    tetris/
    ├── config/         # 配置
    ├── core/           # 核心逻辑
    ├── effects/        # 特效
    ├── audio/          # 音效
    ├── rendering/      # 渲染
    ├── input/          # 输入
    ├── ui/             # 界面
    ├── player/         # 玩家管理
    ├── utils/          # 工具函数
    └── main.py         # 入口
"""

from tetris import main

if __name__ == "__main__":
    main()