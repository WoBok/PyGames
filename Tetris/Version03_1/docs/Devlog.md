### uv venv
1. uv init --python 3.12
2. uv venv
3. uv add pygame

### build
1. uv add pyinstaller
2. uv run pyinstaller --onefile --windowed --add-data "Audio;Audio" tetris.py