@echo off
echo Building Peace Map APK...
call "C:\Users\Jiany\OneDrive\Desktop\test1\flutter\bin\flutter.bat" build apk --release
if %errorlevel% neq 0 (
    echo.
    echo Error: Flutter command failed. check if flutter is installed and in PATH.
    pause
    exit /b
)
echo.
echo ===================================================
echo Build Success!
echo.
echo You can find your App here:
echo %CD%\build\app\outputs\flutter-apk\app-release.apk
echo ===================================================
echo.
pause
