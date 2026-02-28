# Neon Tetris — 打包说明

此仓库包含一个基于 `pygame` 的单文件游戏 `tetris.py`。

**依赖**
- Python 3.8+ (Windows 下建议使用与 `pygame` 兼容的版本)
- `pygame`（已在 `requirements.txt` 中列出）
- `pyinstaller`（用于生成可执行文件）

**快速打包（PowerShell）**
```powershell
.\build.ps1
```

**快速打包（命令行）**
```bat
build.bat
```

或手动运行命令：
```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconsole --onefile --name "NeonTetris" tetris.py
```

**输出**
- 可执行文件位于 `dist\NeonTetris.exe`。
- `build`、`dist` 和 `.spec` 文件会由 `pyinstaller` 生成。

**注意事项**
- 如果你使用 Python 3.13，请确认 `pygame` 是否有可用的二进制轮子，否则可能需要从源编译或使用兼容版本的 Python（如 3.10/3.11）。
- 如果想包含外部资源（图标、字体等），请使用 `--add-data` 参数并调整 `pyinstaller` 命令。

如需我直接在当前环境运行打包（需要安装 `pyinstaller`），告诉我我可以开始构建并验证生成的可执行文件。