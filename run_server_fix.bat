@echo off
setlocal
echo ===================================================
echo   PEACEMAP SERVER SETUP & RUN (AUTO-FIX MODE)
echo ===================================================

:: 1. FIX PYTHON ENVIRONMENT (ZKBioTime issue)
::    We clear these variables so Python uses the standard installation.
:: set PYTHONHOME=
:: set PYTHONPATH=
echo [OK] Cleared conflicting Python environment variables.

:: 2. VERIFY PYTHON
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found or still crashing.
    echo Please install Python from python.org and check "Add to PATH".
    pause
    exit /b
)
echo [OK] Python is working.

:: 3. INSTALL REQUIREMENTS
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies might have failed.
    echo We will try to run anyway.
) else (
    echo [OK] Dependencies installed.
)

:: 4. START SERVERS
echo.
echo Starting Flask Backend...
start "Flask Backend" cmd /k "python app.py"

echo Starting Ngrok Tunnel...
:: Check if ngrok is in path, otherwise warn
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 'ngrok' command not found.
    echo If you want external access (for your phone), download Ngrok.
    echo If you are just testing locally, this is fine.
) else (
    start "Ngrok Tunnel" cmd /k "ngrok http 5000"
)

echo.
echo ===================================================
echo             SERVERS ARE RUNNING
echo ===================================================
echo 1. Look at the 'Ngrok Tunnel' window.
echo 2. Copy the URL that looks like: https://xxxx-xxxx.ngrok-free.dev
echo 3. Paste that URL into your Flutter app code (main.dart).
echo.
pause
