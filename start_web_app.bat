@echo off
echo ========================================
echo    AI Fitness Coach - Web App Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo [1/3] Installing required Python packages...
pip install flask flask-cors requests sqlite3 >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some packages may already be installed or failed to install
    echo Continuing anyway...
)

echo [2/3] Starting Model Server on port 3001...
start "Model Server" cmd /k "python model_server.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Web API Server on port 3000...
start "Web API Server" cmd /k "python web_api_server.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    🚀 AI Fitness Coach is now running!
echo ========================================
echo.
echo 🌐 Web Interface: Open web_app.html in your browser
echo 📡 API Server: http://localhost:3000
echo 🤖 Model Server: http://localhost:3001
echo.
echo Features:
echo ✅ User Authentication & Registration
echo ✅ AI-Powered Program Generation  
echo ✅ Personal Statistics Dashboard
echo ✅ Program History & Analytics
echo ✅ Progress Tracking
echo.
echo IMPORTANT: Make sure both servers start successfully!
echo Check the opened command windows for any errors.
echo.

REM Open the web app in default browser
echo Opening web app in your default browser...
timeout /t 2 /nobreak >nul
start "" "web_app.html"

echo.
echo Press any key to close this launcher...
echo (The servers will continue running in separate windows)
pause >nul