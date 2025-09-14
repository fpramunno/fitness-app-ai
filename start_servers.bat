@echo off
echo Starting Streetlifting Program Generator Servers...
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting Python LLM API Server...
echo Server will be available at http://localhost:3000
echo.

python api_server.py