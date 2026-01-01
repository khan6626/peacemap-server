@echo off
echo Uploading to GitHub...
git branch -M main
git push -u origin main
echo.
echo If asked for login, please sign in with your browser or token.
pause
