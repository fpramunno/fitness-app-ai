# 🏋️ AI Fitness Coach - Web Application

A complete web-based fitness application that uses a fine-tuned LLM model to generate personalized streetlifting programs with user authentication, statistics tracking, and progress analytics.

## 🌟 Features

### 🔐 User Authentication
- Simple username/password registration and login
- Automatic account creation for new users
- Persistent user sessions
- Individual user data isolation

### 🤖 AI-Powered Program Generation
- Fine-tuned LLM model for streetlifting program creation
- Personalized programs based on:
  - Current strength levels (pull-ups, dips, muscle-ups, etc.)
  - Training frequency preferences
  - Primary fitness goals
  - Mesocycle progression

### 📊 Statistics Dashboard
- **Personal Stats**: Programs generated, current streak, favorite goals
- **Progress Tracking**: Strength progression over time
- **Analytics**: Consistency scores, workout patterns
- **Visual Dashboard**: Clean, modern interface with statistics cards

### 📚 Program Management
- **Program History**: View all previously generated programs
- **Program Details**: Full workout prescriptions with technical guidance
- **Workout Logging**: Track completed sessions
- **Pattern Analysis**: Identify training preferences and improvements

## 🏗️ Architecture

```
Web Application Stack:
├── Frontend: Single-page HTML/CSS/JavaScript app
├── Web API Server: Enhanced Flask server with user management
├── Model Server: LLM inference server (GPU-optimized)
└── Database: SQLite for user data and program storage
```

## 🚀 Quick Start

### Method 1: One-Click Launch (Windows)
```bash
# Simply double-click this file:
start_web_app.bat
```

### Method 2: Manual Setup

1. **Start the Model Server** (for AI-powered programs):
   ```bash
   python model_server.py
   ```

2. **Start the Web API Server**:
   ```bash
   python web_api_server.py
   ```

3. **Open the Web App**:
   - Open `web_app.html` in your web browser
   - Or visit: `file:///path/to/web_app.html`

## 📱 How to Use

### 1. Create Account / Login
- Enter any username and password
- New accounts are created automatically
- Your data is saved locally in the SQLite database

### 2. Generate Your First Program
1. Navigate to "New Program" 
2. Fill out the fitness assessment:
   - **Core Movements**: Pull-ups, dips, muscle-ups max weights/reps
   - **Compound Movements**: Rows, push-ups, squats
   - **Training Schedule**: Days per week, mesocycle week
   - **Primary Goal**: Strength, muscle-ups, hypertrophy, or power
3. Click "Generate My AI Program"

### 3. View Your Program
- Detailed day-by-day workout prescriptions
- Technical coaching cues and form guidance
- Rep/set schemes optimized for your level
- Options to start individual workout sessions

### 4. Track Your Progress
- **Dashboard**: Overview of your fitness journey
- **Analytics**: Detailed progress and pattern analysis
- **History**: Access all your previous programs

## 🔧 Technical Details

### Database Schema
- **Users**: Authentication and profile data
- **Programs**: Generated workout programs with assessments
- **User Stats**: Aggregated statistics and progress metrics
- **Workout Logs**: Individual session completion tracking

### API Endpoints
- `POST /api/auth/login` - User authentication/registration
- `POST /api/generate-program` - AI program generation
- `GET /api/programs` - User's program history
- `GET /api/user/stats` - Personal statistics
- `POST /api/workout/log` - Log workout completion

### Model Integration
- Connects to the existing fine-tuned LLM model
- Fallback to mock generation if model server unavailable
- Real-time status checking and error handling

## 🎯 Use Cases

### For Athletes
- **Streetlifting Competitors**: Periodized training programs
- **Calisthenics Enthusiasts**: Progressive skill development
- **General Fitness**: Structured bodyweight and weighted programs

### For Coaches
- **Client Management**: Individual program generation
- **Progress Tracking**: Monitor athlete development
- **Program Analysis**: Review training patterns and effectiveness

### For Researchers
- **Training Data**: User interaction patterns with AI-generated programs
- **Model Performance**: Real-world LLM application feedback
- **Fitness Analytics**: Population-level training trends

## 🔄 Offline Mode

The app includes intelligent fallback functionality:
- **Online Mode**: Uses fine-tuned LLM for optimal program generation
- **Offline Mode**: Falls back to rule-based program generation
- **Automatic Detection**: Seamlessly switches based on server availability

## 🛠️ Customization

### Adding New Goals
Edit the goal options in `web_app.html`:
```javascript
const goals = [
    { key: 'strength', label: 'Strength Development' },
    { key: 'your_new_goal', label: 'Your New Goal' },
    // Add more goals...
];
```

### Modifying Assessment Parameters
Update the assessment form fields to collect additional fitness data:
- Add new input fields in the HTML
- Update the assessment object in JavaScript
- Modify the backend to handle new parameters

### Custom Analytics
Extend the analytics dashboard by:
- Adding new database tables for additional metrics
- Creating new API endpoints for data retrieval
- Implementing charts and visualizations

## 📊 Example Program Output

```
MESO1 — DAY 1 — Pull-ups Focus (15kg)

Wide Grip Weighted Pull-ups
• Focus on controlled movement and scapular engagement
• Work on pendulum motion from starting position
• 5 x 1+1, rest 15-20" between mini-sets, 1:30-2:00 between sets
• Film last set for form check

Accessory work:
• Dead hangs: 3 x max time
• Scapular pull-ups: 3 x 8-10
```

## 🔮 Future Enhancements

- **Mobile Responsiveness**: Optimized mobile interface
- **Social Features**: Share programs and compete with friends
- **Advanced Analytics**: Machine learning insights on progress
- **Video Integration**: Exercise demonstration videos
- **Nutrition Tracking**: Integrated diet recommendations
- **Wearable Integration**: Connect with fitness trackers

## 🤝 Contributing

This application demonstrates the integration of:
- Modern web technologies (HTML5, CSS3, ES6+)
- AI/ML model serving and integration
- User authentication and data persistence
- Real-time statistics and analytics
- Responsive design principles

## 📄 License

This project is part of a fitness application demonstration and includes both frontend and backend components for educational and practical use.

---

**🏋️ Start your AI-powered fitness journey today!**