@echo off
setlocal

echo ===================================================
echo   PEACEMAP CLEAN START (Fixing empty backend window)
echo ===================================================

:: 1. Install Requirements (just in case)
"C:\Users\Jiany\AppData\Local\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt >nul 2>&1

:: 2. Start Servers
echo.
echo Starting Flask Backend...
start "Flask Backend" backend_launcher.bat

echo Starting Ngrok Tunnel...
start "Ngrok Tunnel" cmd /k "ngrok http 5000"

echo.
echo ===================================================
echo             SERVERS ARE STARTING
echo ===================================================
echo Check the new windows.
echo.
pause
