@echo off
setlocal
title Desktop Floating Spider Installer
cls
echo ============================================================
echo       Desktop Floating Spider - Windows Auto Installer
echo ============================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not detected in your system PATH!
    echo.
    echo Please download and install Python 3.8+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python "%~dp0setup_interactive.py"
if %errorlevel% neq 0 (
    echo.
    echo [!] Setup exited with a non-zero code.
    pause
)
