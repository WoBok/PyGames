@echo off
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconsole --onefile --name "NeonTetris" tetris.py

echo Build finished. See the dist\NeonTetris.exe
pause
