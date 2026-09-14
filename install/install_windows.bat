@echo off
cd /d "%~dp0\.."

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m venv .venv
) else (
    where python >nul 2>nul
    if not %errorlevel%==0 (
        echo Python was not found.
        echo Install Python 3 and enable "Add Python to PATH".
        pause
        exit /b 1
    )
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo VOID installation completed.
echo Run with: run.bat
pause
