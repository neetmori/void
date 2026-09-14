@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    echo VOID is not installed yet.
    echo Run install\install_windows.bat first.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python void.py
