@echo off
echo Setting up Python virtual environment...

:: Check if .venv exists, if not create it
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo Setup complete! Virtual environment is now active.
echo You can now run: python main.py
pause
