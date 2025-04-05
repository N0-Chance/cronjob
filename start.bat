@echo off
echo cronjob - Automated Job Resume and Cover Letter Writer
echo ====================================================
echo Let's get you a job!
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check if pip is installed and upgrade it
echo Checking pip installation...
python -m pip install --upgrade pip

:: Install requirements
echo Installing required packages...
python -m pip install -r requirements.txt

:: Check if .env exists
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo Please create a .env file with your configuration.
    echo See README.md for required settings.
    echo.
    pause
)

:: Check if config/user.json exists
if not exist config\user.json (
    echo.
    echo WARNING: config/user.json not found!
    echo Please create your user profile from user-example.json.
    echo.
    pause
)

:: Run the main script
echo.
echo Starting cronjob pipeline...
python src/main.py

pause 