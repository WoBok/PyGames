# Build script (PowerShell) - run from project folder
python -m pip install -r requirements.txt
python -m pip install pyinstaller
# Create one-file GUI executable (no console window)
pyinstaller --noconsole --onefile --name "NeonTetris" tetris.py

# Result: dist\NeonTetris.exe
