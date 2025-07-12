@echo off
title Aditya Concert Server

echo [✓] Activating your Flask project...

cd /d C:\Users\DELL\aditya_concert

REM Set the Flask app name
set FLASK_APP=ap.py

REM Start Flask server in a new background window
start "Flask Server" cmd /k python -m flask run --host=0.0.0.0 --port=5000

echo [✓] Starting Ngrok tunnel...

cd /d C:\Users\DELL\ngrok

REM Wait 4 seconds to ensure Flask starts first
timeout /t 4 >nul

start "Ngrok Tunnel" cmd /k ngrok http 5000

echo [✓] Flask and Ngrok started!
echo 🔗 Your mobile/public link will appear in the Ngrok window.
pause
