@echo off
echo Setting up Python environment with uv...

:: Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv not found. Please install uv first:
    echo Visit: https://docs.astral.sh/uv/getting-started/installation/
    echo Or run: pip install uv
    pause
    exit /b 1
)

:: Create virtual environment and install dependencies
echo Creating virtual environment and installing dependencies...
uv sync

echo Setup complete! To activate the environment, run:
echo .venv\Scripts\activate
echo.
pause
