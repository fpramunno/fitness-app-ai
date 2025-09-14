#!/bin/bash

# FitnessTracker Development Startup Script
echo "🏋️ Starting FitnessTracker Development Environment"
echo "=================================================="

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Flask..."
    pip install flask flask-cors
fi

# Start the backend API in background
echo "🚀 Starting Backend API (port 3000)..."
python3 backend_integration.py &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start the Expo development server
echo "📱 Starting Expo Web Development Server (port 8081)..."
echo ""
echo "💡 Development URLs:"
echo "   📱 App Preview: http://localhost:8081"
echo "   🔧 API Server: http://localhost:3000"
echo "   📊 API Health: http://localhost:3000/api/health"
echo ""
echo "🎯 Features Available:"
echo "   ✅ Program Generator Integration"
echo "   ✅ Live Web Preview"
echo "   ✅ Assessment Form"
echo "   ✅ Program Display"
echo "   🔄 Ready for feedback system"
echo ""
echo "Press Ctrl+C to stop all services"

# Load nvm and start Expo
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

npm run web

# Cleanup: Kill background processes when script exits
trap "echo 'Stopping services...'; kill $BACKEND_PID 2>/dev/null" EXIT