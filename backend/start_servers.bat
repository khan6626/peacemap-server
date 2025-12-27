@echo off
set PYTHONHOME=
echo Starting Flask Backend...
start "Flask Backend" cmd /k "python app.py"
timeout /t 5
echo Starting Ngrok Tunnel...
start "Ngrok Tunnel" cmd /k "ngrok http 5000"
echo Servers started. Please ensure the URL in the app matches the ngrok URL.
pause
