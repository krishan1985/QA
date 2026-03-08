@echo off
echo ===========================================
echo   Starting Sigma Testing AI Agent Setup...
echo ===========================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation.
    pause
    exit /b
)

:: Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed but Python is.
    echo Attempting to install pip...
    python -m ensurepip --default-pip
)

echo.
echo [1/2] Installing required dependencies...
echo This might take a few minutes the first time.
pip install -r backend\requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies. Please check the error above.
    pause
    exit /b
)

echo.
echo [2/2] Starting the Sigma AI Backend Server...
echo The dashboard will be accessible via browser once this is running.
python backend\main.py

pause
