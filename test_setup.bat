@echo off
echo Creating test environment...
echo.

:: Create a temporary directory
set TEST_DIR=test_cronjob
if exist %TEST_DIR% (
    echo Removing existing test directory...
    rmdir /s /q %TEST_DIR%
)
mkdir %TEST_DIR%

:: Copy essential files
echo Copying project files...
xcopy /E /I /Y . %TEST_DIR%\

:: Remove critical files to simulate fresh install
echo Setting up test environment...
cd %TEST_DIR%
del .env
del config\user.json
del db\data.db 2>nul

:: Run the start script
echo.
echo Running start.bat...
echo.
start.bat

echo.
echo Test complete. Press any key to clean up...
pause

:: Clean up
cd ..
rmdir /s /q %TEST_DIR% 