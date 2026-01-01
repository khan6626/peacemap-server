@echo off
set PYTHONHOME=
cd /d "c:\Users\Jiany\OneDrive\Desktop\gamma\gamma\gamma"
echo Killing old processes...
taskkill /IM ngrok.exe /F 2>nul
echo Starting Servers...
start "PeaceMap Backend" python backend\app.py
timeout /t 3
start "PeaceMap Online Link" python backend\share_server.py
echo.
echo ========================================================
echo  Servers Restarted! 
echo  Please connect your PC to Hotspot (Mobile Data) now.
echo ========================================================
pause
