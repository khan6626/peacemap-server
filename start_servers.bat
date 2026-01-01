@echo off
setlocal

:: FIX FOR ZKBioTime / PYTHON CONFLICTS
:: set PYTHONHOME=
:: set PYTHONPATH=

echo Starting Flask Backend (Safe Mode)...
:: We launch a new window that explicitely clears variables again before running python
start "Flask Backend" cmd /k "python app.py"

timeout /t 3 >nul

echo Starting Ngrok Tunnel...
start "Ngrok Tunnel" cmd /k "ngrok http 5000"

echo.
echo ======================================================
echo   OPEN THE 'Ngrok Tunnel' WINDOW TO SEE THE CODE
echo ======================================================
echo.
pause
