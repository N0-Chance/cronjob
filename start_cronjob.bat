@echo off
cd /d %~dp0

:: Create venv and install requirements if needed
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo Thanks for using cronjob!
:: Launch GUI using pythonw.exe in a separate process
start "" venv\Scripts\pythonw.exe src\gui\start_gui.py

:: Exit .bat immediately
exit
