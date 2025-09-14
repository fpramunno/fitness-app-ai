# 🏋️ FitnessTracker - Local Setup Guide

## 📁 What You Downloaded

You have the complete fitness app project with:
- ✅ React Native/Expo frontend
- ✅ Program generator integration  
- ✅ Backend API (Flask)
- ✅ All your existing Python code
- ✅ Static HTML version

## 🖥️ System Requirements

### Required Software:
1. **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
2. **Python** (v3.8+) - [Download here](https://python.org/)
3. **Git** (optional but recommended)

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
# Navigate to the project
cd ExpoFitnessApp

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install flask flask-cors
```

### Step 2: Start the Backend API

```bash
# In terminal 1 - Start backend
python3 backend_integration.py
```

You should see:
```
🚀 Starting FitnessTracker API Server...
📱 React Native app can connect to: http://localhost:3000
```

### Step 3: Start the Frontend

```bash
# In terminal 2 - Start frontend
npm run web
```

This opens your browser automatically at `http://localhost:8081`

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | `http://localhost:8081` | Full React Native app |
| **Static Version** | `http://localhost:8082/static_app.html` | Backup HTML version |
| **Backend API** | `http://localhost:3000` | Program generation API |

## 🛠️ Alternative: One-Command Start

Use the development script:

```bash
chmod +x start_dev.sh
./start_dev.sh
```

This starts both backend and frontend automatically.

## 📱 App Features

### ✅ Working Features:
- **Assessment Form** - Input your fitness levels
- **Program Generator** - AI creates personalized programs
- **Program Display** - View weekly workout schedules
- **Backend Integration** - Connects to your program_generator.py

### 🔄 Ready to Implement:
- Daily workout interface
- Feedback collection system
- Progress tracking
- Fine-tuned model integration

## 🐛 Troubleshooting

### Port Already in Use:
```bash
# Kill existing processes
npx kill-port 3000
npx kill-port 8081
```

### React Native Web Issues:
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
```

### Python Dependencies:
```bash
pip install --upgrade flask flask-cors
```

## 📁 Project Structure

```
ExpoFitnessApp/
├── src/
│   ├── components/
│   │   └── program/          # Assessment & Program Display
│   ├── screens/
│   │   └── program/          # Main Program Generator Screen
│   ├── services/
│   │   └── api/              # API integration
│   └── types/                # TypeScript definitions
├── backend_integration.py    # Flask API server
├── static_app.html          # Standalone HTML version
├── start_dev.sh             # Development startup script
└── package.json             # Node.js dependencies
```

## 🎯 Next Development Steps

1. **Test program generation** with your fitness data
2. **Implement daily workout interface** for exercise execution
3. **Add feedback collection** for program optimization
4. **Integrate fine-tuned model** for adaptive programming
5. **Build for mobile** using Expo CLI

## 📞 Support

If you encounter issues:
1. Check that both Node.js and Python are installed
2. Ensure ports 3000 and 8081 are available
3. Try the static HTML version as backup
4. Check browser console for error messages

---

**🎉 You now have a complete AI-powered fitness app ready for development!**