#!/usr/bin/env python3
"""
Enhanced Flask API Server for Web-based Fitness App
Supports user authentication, data persistence, and statistics tracking
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sys
import os
import traceback
import requests
import json
import hashlib
from datetime import datetime, timedelta
import sqlite3
from contextlib import contextmanager
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import assessment class
try:
    from assessment import StreetliftingAssessment
    print("✅ Successfully imported assessment class")
except ImportError as e:
    print(f"❌ Could not import assessment: {e}")
    print("Make sure assessment.py exists")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app, supports_credentials=True, origins=['http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:8081', 'http://127.0.0.1:8081', 'file://'])

# Model server configuration
MODEL_SERVER_URL = "http://localhost:3001"

# Database setup
DATABASE_PATH = 'fitness_app.db'

# Email configuration (update with your SMTP settings)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_username': 'your-email@gmail.com',  # Update this
    'smtp_password': 'your-app-password',     # Update this
    'from_email': 'your-email@gmail.com'     # Update this
}

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if we need to migrate existing users table
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'email' not in columns:
        print("🔄 Migrating users table to add email support...")
        # Add new columns to existing users table
        cursor.execute('ALTER TABLE users ADD COLUMN email TEXT')
        cursor.execute('ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT TRUE')  # Set existing users as verified
        cursor.execute('ALTER TABLE users ADD COLUMN verification_token TEXT')

        # Set default emails for existing users
        cursor.execute('UPDATE users SET email = username || "@example.com" WHERE email IS NULL')
        print("✅ Users table migrated - existing users can login normally")
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email_verified BOOLEAN DEFAULT FALSE,
            verification_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Programs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            program_data TEXT NOT NULL,
            assessment_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            goal TEXT,
            training_days INTEGER,
            mesocycle_week INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_programs INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            favorite_goal TEXT DEFAULT 'strength',
            avg_days_per_week REAL DEFAULT 3.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Workout logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            program_id INTEGER,
            day_number INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (program_id) REFERENCES programs (id)
        )
    ''')

    # Exercise tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exercise_name TEXT NOT NULL,
            weight REAL,
            reps INTEGER,
            sets INTEGER,
            rpe INTEGER,
            rir INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # User main exercises tracking (for progress plots)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_main_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exercise_name TEXT NOT NULL,
            is_main_exercise BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, exercise_name)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def send_verification_email(email, token):
    """Send email verification email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = email
        msg['Subject'] = "Verify your Fitness App account"

        # Create verification URL
        verification_url = f"http://localhost:3000/verify-email?token={token}"

        body = f"""
        Welcome to the Fitness App!

        Please click the link below to verify your email address:
        {verification_url}

        This link will expire in 24 hours.

        If you didn't create this account, please ignore this email.
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['smtp_username'], EMAIL_CONFIG['smtp_password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['from_email'], email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def check_model_server():
    """Check if model server is running"""
    try:
        response = requests.get(f"{MODEL_SERVER_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    model_server_ready = check_model_server()
    return jsonify({
        'status': 'healthy',
        'model_server_ready': model_server_ready,
        'model_server_url': MODEL_SERVER_URL,
        'database_ready': os.path.exists(DATABASE_PATH),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        username = data['username']
        password_hash = hash_password(data['password'])
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if user and user['password_hash'] == password_hash:
                # Check if email is verified (only for users with real emails, not migrated ones)
                if user.get('email_verified') is not None and not user['email_verified'] and not user['email'].endswith('@example.com'):
                    return jsonify({'error': 'Please verify your email before logging in'}), 401

                # Update last login
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                             (datetime.now(), user['id']))
                conn.commit()
                
                # Get user stats
                cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user['id'],))
                stats = cursor.fetchone()
                
                if not stats:
                    # Create initial stats
                    cursor.execute('''
                        INSERT INTO user_stats (user_id, total_programs, current_streak, favorite_goal, avg_days_per_week)
                        VALUES (?, 0, 0, 'strength', 3.0)
                    ''', (user['id'],))
                    conn.commit()
                    
                    cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user['id'],))
                    stats = cursor.fetchone()
                
                session['user_id'] = user['id']
                session['username'] = user['username']
                
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'joinDate': user['created_at'],
                        'stats': {
                            'totalPrograms': stats['total_programs'],
                            'currentStreak': stats['current_streak'],
                            'favoriteGoal': stats['favorite_goal'],
                            'avgDaysPerWeek': stats['avg_days_per_week']
                        }
                    }
                })
            elif not user:
                # Create new user
                cursor.execute('''
                    INSERT INTO users (username, password_hash, created_at)
                    VALUES (?, ?, ?)
                ''', (username, password_hash, datetime.now()))
                user_id = cursor.lastrowid
                
                # Create initial stats
                cursor.execute('''
                    INSERT INTO user_stats (user_id, total_programs, current_streak, favorite_goal, avg_days_per_week)
                    VALUES (?, 0, 0, 'strength', 3.0)
                ''', (user_id,))
                conn.commit()
                
                session['user_id'] = user_id
                session['username'] = username
                
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'joinDate': datetime.now().isoformat(),
                        'stats': {
                            'totalPrograms': 0,
                            'currentStreak': 0,
                            'favoriteGoal': 'strength',
                            'avgDaysPerWeek': 3.0
                        }
                    }
                })
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
                
    except Exception as e:
        print(f"❌ Login error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup endpoint with email verification"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'error': 'Username, email, and password required'}), 400

        username = data['username']
        email = data['email']
        password_hash = hash_password(data['password'])
        verification_token = generate_verification_token()

        with get_db() as conn:
            cursor = conn.cursor()

            # Check if username or email already exists
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                if existing_user['username'] == username:
                    return jsonify({'error': 'Username already exists'}), 400
                else:
                    return jsonify({'error': 'Email already exists'}), 400

            # Create new user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, email_verified, verification_token)
                VALUES (?, ?, ?, FALSE, ?)
            ''', (username, email, password_hash, verification_token))

            user_id = cursor.lastrowid
            conn.commit()

            # Initialize user stats
            cursor.execute('''
                INSERT INTO user_stats (user_id, total_programs, current_streak, favorite_goal, avg_days_per_week)
                VALUES (?, 0, 0, 'strength', 3.0)
            ''', (user_id,))
            conn.commit()

            # Send verification email
            email_sent = send_verification_email(email, verification_token)

            return jsonify({
                'success': True,
                'message': 'Account created successfully. Please check your email to verify your account.',
                'email_sent': email_sent
            })

    except Exception as e:
        print(f"Signup error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Signup failed'}), 500

@app.route('/api/auth/verify-email', methods=['GET'])
def verify_email():
    """Email verification endpoint"""
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'Verification token required'}), 400

        with get_db() as conn:
            cursor = conn.cursor()

            # Find user with this token
            cursor.execute('SELECT * FROM users WHERE verification_token = ?', (token,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'error': 'Invalid verification token'}), 400

            # Check if already verified
            if user['email_verified']:
                return jsonify({'message': 'Email already verified'})

            # Verify the email
            cursor.execute('''
                UPDATE users SET email_verified = TRUE, verification_token = NULL
                WHERE id = ?
            ''', (user['id'],))
            conn.commit()

            return jsonify({'success': True, 'message': 'Email verified successfully'})

    except Exception as e:
        print(f"Email verification error: {e}")
        return jsonify({'error': 'Email verification failed'}), 500

@app.route('/api/generate-program', methods=['POST'])
def generate_program():
    """Generate a streetlifting program based on assessment"""
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if model server is running
        if not check_model_server():
            return jsonify({
                'error': 'Model server not available',
                'message': f'Model server at {MODEL_SERVER_URL} is not responding. Start model_server.py first.'
            }), 503

        # Get assessment data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create assessment object with new field names
        assessment_data = {
            'bodyweight_pullups_max': int(data.get('bodyweight_pullups_max', 0)),
            'weighted_pullups_max': int(data.get('weighted_pullups_max', 0)),
            'bodyweight_dips_max': int(data.get('bodyweight_dips_max', 0)),
            'weighted_dips_max': int(data.get('weighted_dips_max', 0)),
            'bodyweight_muscle_ups_max': int(data.get('bodyweight_muscle_ups_max', 0)),
            'weighted_muscle_ups_max': int(data.get('weighted_muscle_ups_max', 0)),
            'bodyweight_squats_max': int(data.get('bodyweight_squats_max', 0)),
            'weighted_squats_max': int(data.get('weighted_squats_max', 0)),
            'bodyweight_pushups_max': int(data.get('bodyweight_pushups_max', 0)),
            'training_days_per_week': int(data.get('training_days_per_week', 3)),
            'mesocycle_week': int(data.get('mesocycle_week', 1)),
            'primary_goal': data.get('primary_goal', 'strength'),
            'athlete_description': data.get('athlete_description', '')
        }

        print(f"🏋️ Generating program for user {session['username']}: {assessment_data['primary_goal']} goal, {assessment_data['training_days_per_week']} days/week")

        # Call model server to generate complete weekly program
        response = requests.post(f"{MODEL_SERVER_URL}/generate",
                               json=assessment_data,
                               timeout=180)  # Increased to 3 minutes for first-time generation

        if response.status_code == 200:
            result = response.json()
            weekly_program_text = result['weekly_program']

            # Better parsing with multiple possible separators
            weekly_program = {}

            # Try different ways to split the program into days
            possible_separators = [
                r'Day (\d+):',
                r'Day (\d+)\n',
                r'Day (\d+)',
                r'DAY (\d+):',
                r'DAY (\d+)'
            ]

            import re
            parsed = False

            for separator in possible_separators:
                matches = list(re.finditer(separator, weekly_program_text, re.IGNORECASE))
                if len(matches) >= assessment_data['training_days_per_week']:
                    print(f"✅ Successfully parsed using separator: {separator}")

                    for i, match in enumerate(matches[:assessment_data['training_days_per_week']]):
                        day_num = int(match.group(1))
                        start_pos = match.start()

                        # Find the end position (next day or end of text)
                        if i + 1 < len(matches):
                            end_pos = matches[i + 1].start()
                        else:
                            end_pos = len(weekly_program_text)

                        day_content = weekly_program_text[start_pos:end_pos].strip()
                        weekly_program[day_num] = day_content

                    parsed = True
                    break

            # If parsing failed completely, just divide the text equally
            if not parsed:
                print("⚠️ Parsing failed, dividing text equally among days")
                lines = weekly_program_text.strip().split('\n')
                lines_per_day = max(1, len(lines) // assessment_data['training_days_per_week'])

                for day in range(1, assessment_data['training_days_per_week'] + 1):
                    start_line = (day - 1) * lines_per_day
                    end_line = day * lines_per_day if day < assessment_data['training_days_per_week'] else len(lines)
                    day_lines = lines[start_line:end_line]
                    weekly_program[day] = f"Day {day}:\n" + '\n'.join(day_lines)
        else:
            print(f"❌ Error generating program: {response.text}")
            # Fallback program
            weekly_program = {}
            for day in range(1, assessment_data['training_days_per_week'] + 1):
                weekly_program[day] = f"Day {day}: Error generating program - model server unavailable"

        # Create response
        program_response = {
            'id': str(int(datetime.now().timestamp())),
            'weekly_program': weekly_program,
            'assessment': assessment_data,
            'created_at': datetime.now().isoformat(),
            'generated_with_llm': True
        }

        # Save program to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO programs (user_id, program_data, assessment_data, goal, training_days, mesocycle_week)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                json.dumps(weekly_program),
                json.dumps(program_response['assessment']),
                assessment_data['primary_goal'],
                assessment_data['training_days_per_week'],
                assessment_data['mesocycle_week']
            ))

            # Update user stats
            cursor.execute('UPDATE user_stats SET total_programs = total_programs + 1, favorite_goal = ?, last_updated = ? WHERE user_id = ?',
                         (assessment_data['primary_goal'], datetime.now(), session['user_id']))
            
            # Update average days per week
            cursor.execute('SELECT AVG(training_days) as avg_days FROM programs WHERE user_id = ?', (session['user_id'],))
            avg_result = cursor.fetchone()
            if avg_result and avg_result['avg_days']:
                cursor.execute('UPDATE user_stats SET avg_days_per_week = ? WHERE user_id = ?',
                             (round(float(avg_result['avg_days']), 1), session['user_id']))
            
            conn.commit()

        print(f"✅ Program generated and saved successfully with {len(weekly_program)} days")
        return jsonify(program_response)

    except Exception as e:
        print(f"❌ Error generating program: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Program generation failed',
            'message': str(e),
            'fallback_available': False
        }), 500

@app.route('/api/programs', methods=['GET'])
def get_user_programs():
    """Get all programs for the authenticated user"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, program_data, assessment_data, created_at, goal, training_days, mesocycle_week
                FROM programs 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (session['user_id'],))
            
            programs = []
            for row in cursor.fetchall():
                program = {
                    'id': str(row['id']),
                    'weekly_program': json.loads(row['program_data']),
                    'assessment': json.loads(row['assessment_data']),
                    'created_at': row['created_at'],
                    'generated_with_llm': True
                }
                programs.append(program)
            
            return jsonify({'programs': programs})
    
    except Exception as e:
        print(f"❌ Error fetching programs: {e}")
        return jsonify({'error': 'Failed to fetch programs'}), 500

@app.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (session['user_id'],))
            stats = cursor.fetchone()
            
            # Get workout count
            cursor.execute('SELECT COUNT(*) as count FROM workout_logs WHERE user_id = ?', (session['user_id'],))
            workout_count = cursor.fetchone()['count']
            
            if stats:
                return jsonify({
                    'totalPrograms': stats['total_programs'],
                    'currentStreak': stats['current_streak'],
                    'favoriteGoal': stats['favorite_goal'],
                    'avgDaysPerWeek': stats['avg_days_per_week'],
                    'totalWorkouts': workout_count,
                    'consistencyScore': min(100, stats['total_programs'] * 10),
                    'strengthProgression': 0  # Would need historical data to calculate
                })
            else:
                return jsonify({
                    'totalPrograms': 0,
                    'currentStreak': 0,
                    'favoriteGoal': 'strength',
                    'avgDaysPerWeek': 3.0,
                    'totalWorkouts': 0,
                    'consistencyScore': 0,
                    'strengthProgression': 0
                })
    
    except Exception as e:
        print(f"❌ Error fetching user stats: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500

@app.route('/api/workout/log', methods=['POST'])
def log_workout():
    """Log a completed workout"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        program_id = data.get('program_id')
        day_number = data.get('day_number')
        notes = data.get('notes', '')
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workout_logs (user_id, program_id, day_number, notes)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], program_id, day_number, notes))
            
            # Update streak (simplified logic)
            cursor.execute('UPDATE user_stats SET current_streak = current_streak + 1 WHERE user_id = ?',
                         (session['user_id'],))
            conn.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"❌ Error logging workout: {e}")
        return jsonify({'error': 'Failed to log workout'}), 500

@app.route('/api/exercise/log', methods=['POST'])
def log_exercise():
    """Log exercise performance data"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data or not data.get('exercise_name'):
            return jsonify({'error': 'Exercise name required'}), 400

        exercise_name = data['exercise_name']
        weight = data.get('weight')
        reps = data.get('reps')
        sets = data.get('sets')
        rpe = data.get('rpe')
        rir = data.get('rir')
        notes = data.get('notes', '')

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO exercise_records (user_id, exercise_name, weight, reps, sets, rpe, rir, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], exercise_name, weight, reps, sets, rpe, rir, notes))
            conn.commit()

        return jsonify({'success': True, 'message': 'Exercise logged successfully'})

    except Exception as e:
        print(f"❌ Error logging exercise: {e}")
        return jsonify({'error': 'Failed to log exercise'}), 500

@app.route('/api/exercise/main', methods=['POST'])
def add_main_exercise():
    """Add exercise to main exercises for tracking"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data or not data.get('exercise_name'):
            return jsonify({'error': 'Exercise name required'}), 400

        exercise_name = data['exercise_name']

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO user_main_exercises (user_id, exercise_name, is_main_exercise)
                VALUES (?, ?, TRUE)
            ''', (session['user_id'], exercise_name))
            conn.commit()

        return jsonify({'success': True, 'message': 'Main exercise added'})

    except Exception as e:
        print(f"❌ Error adding main exercise: {e}")
        return jsonify({'error': 'Failed to add main exercise'}), 500

@app.route('/api/exercise/main', methods=['GET'])
def get_main_exercises():
    """Get user's main exercises"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT exercise_name, created_at FROM user_main_exercises
                WHERE user_id = ? AND is_main_exercise = TRUE
                ORDER BY created_at
            ''', (session['user_id'],))

            exercises = [{'name': row['exercise_name'], 'added_at': row['created_at']}
                        for row in cursor.fetchall()]

        return jsonify({'exercises': exercises})

    except Exception as e:
        print(f"❌ Error getting main exercises: {e}")
        return jsonify({'error': 'Failed to get main exercises'}), 500

@app.route('/api/exercise/progress/<exercise_name>', methods=['GET'])
def get_exercise_progress(exercise_name):
    """Get progress data for a specific exercise"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        # Get optional date range
        days_back = request.args.get('days', 90, type=int)
        start_date = datetime.now() - timedelta(days=days_back)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, weight, reps, sets, rpe, rir, notes
                FROM exercise_records
                WHERE user_id = ? AND exercise_name = ? AND date >= ?
                ORDER BY date ASC
            ''', (session['user_id'], exercise_name, start_date))

            records = []
            for row in cursor.fetchall():
                records.append({
                    'date': row['date'],
                    'weight': row['weight'],
                    'reps': row['reps'],
                    'sets': row['sets'],
                    'rpe': row['rpe'],
                    'rir': row['rir'],
                    'notes': row['notes']
                })

        return jsonify({
            'exercise_name': exercise_name,
            'records': records,
            'total_sessions': len(records)
        })

    except Exception as e:
        print(f"❌ Error getting exercise progress: {e}")
        return jsonify({'error': 'Failed to get exercise progress'}), 500

@app.route('/api/exercise/dashboard', methods=['GET'])
def get_exercise_dashboard():
    """Get exercise dashboard data with progress for all main exercises"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        with get_db() as conn:
            cursor = conn.cursor()

            # Get main exercises
            cursor.execute('''
                SELECT exercise_name FROM user_main_exercises
                WHERE user_id = ? AND is_main_exercise = TRUE
                ORDER BY created_at
            ''', (session['user_id'],))

            main_exercises = [row['exercise_name'] for row in cursor.fetchall()]

            # Get recent progress for each main exercise
            dashboard_data = {}
            for exercise in main_exercises:
                cursor.execute('''
                    SELECT date, weight, reps, sets
                    FROM exercise_records
                    WHERE user_id = ? AND exercise_name = ?
                    ORDER BY date DESC
                    LIMIT 10
                ''', (session['user_id'], exercise))

                recent_records = []
                for row in cursor.fetchall():
                    recent_records.append({
                        'date': row['date'],
                        'weight': row['weight'],
                        'reps': row['reps'],
                        'sets': row['sets']
                    })

                dashboard_data[exercise] = {
                    'recent_records': recent_records,
                    'total_sessions': len(recent_records)
                }

        return jsonify({
            'main_exercises': main_exercises,
            'progress_data': dashboard_data
        })

    except Exception as e:
        print(f"❌ Error getting exercise dashboard: {e}")
        return jsonify({'error': 'Failed to get exercise dashboard'}), 500

@app.route('/api/exercise/chart/<exercise_name>', methods=['GET'])
def get_exercise_chart_data(exercise_name):
    """Get exercise data formatted for charts/plots"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        # Get optional parameters
        days_back = request.args.get('days', 180, type=int)
        metric = request.args.get('metric', 'weight')  # weight, volume, max_reps
        start_date = datetime.now() - timedelta(days=days_back)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, weight, reps, sets, rpe, rir
                FROM exercise_records
                WHERE user_id = ? AND exercise_name = ? AND date >= ?
                ORDER BY date ASC
            ''', (session['user_id'], exercise_name, start_date))

            records = cursor.fetchall()

            # Prepare chart data
            chart_data = {
                'dates': [],
                'values': [],
                'labels': [],
                'exercise_name': exercise_name,
                'metric': metric
            }

            for row in records:
                date_str = row['date'][:10]  # Get just the date part
                chart_data['dates'].append(date_str)

                if metric == 'weight' and row['weight']:
                    chart_data['values'].append(float(row['weight']))
                    chart_data['labels'].append(f"{row['weight']}kg")
                elif metric == 'volume' and row['weight'] and row['reps'] and row['sets']:
                    volume = float(row['weight']) * int(row['reps']) * int(row['sets'])
                    chart_data['values'].append(volume)
                    chart_data['labels'].append(f"{volume:.0f}kg")
                elif metric == 'max_reps' and row['reps']:
                    chart_data['values'].append(int(row['reps']))
                    chart_data['labels'].append(f"{row['reps']} reps")
                else:
                    chart_data['dates'].pop()  # Remove the date if no valid data

            # Calculate trend if enough data points
            if len(chart_data['values']) >= 2:
                first_value = chart_data['values'][0]
                last_value = chart_data['values'][-1]
                trend = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
                chart_data['trend_percentage'] = round(trend, 2)
                chart_data['trend_direction'] = 'up' if trend > 0 else 'down' if trend < 0 else 'stable'

            return jsonify(chart_data)

    except Exception as e:
        print(f"❌ Error getting chart data: {e}")
        return jsonify({'error': 'Failed to get chart data'}), 500

@app.route('/api/model-status', methods=['GET'])
def model_status():
    """Get information about the model server"""
    try:
        if not check_model_server():
            return jsonify({
                'model_loaded': False,
                'error': 'Model server not available'
            }), 503
        
        response = requests.get(f"{MODEL_SERVER_URL}/model-status", timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'model_loaded': False,
                'error': 'Failed to get model status'
            }), 500
            
    except Exception as e:
        return jsonify({
            'model_loaded': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Fitness App Web API Server...")
    print("📦 Initializing database...")
    init_database()
    print("📡 This server will connect to model server at http://localhost:3001")
    print("⚠️  Make sure to run model_server.py first for AI-powered programs!")
    print("🌐 Starting Flask server on http://localhost:3000")
    print("🔐 Features: User auth, data persistence, statistics tracking")
    app.run(host='0.0.0.0', port=3000, debug=True)