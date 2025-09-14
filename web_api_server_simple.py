#!/usr/bin/env python3
"""
Simple Flask API Server for Fitness App (SQLite version)
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import traceback
import requests
import json
import hashlib
from datetime import datetime, timedelta
import sqlite3
from contextlib import contextmanager
import secrets

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# CORS configuration
CORS(app, supports_credentials=True, origins=[
    'https://*.onrender.com',  # Allow all Render domains
    'https://*.vercel.app',    # Allow all Vercel domains
    'https://fitness-app-frontend-psi.vercel.app',  # Old frontend domain
    'https://fitness-app-frontend-poqig2wv2-francesco-pio-ramunnos-projects.vercel.app',  # New frontend domain
    'http://localhost:8081',   # For development
    'http://localhost:3000',   # For development
])

# RunPod AI server configuration
RUNPOD_API_URL = os.getenv('RUNPOD_API_URL', 'http://localhost:3001')

# Database setup (using SQLite for now)
DATABASE_PATH = 'fitness_app.db'

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("📦 Initializing SQLite database...")

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email_verified BOOLEAN DEFAULT TRUE,
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

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection and tables
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            tables = [row[0] for row in cursor.fetchall()]

            if 'users' in tables and 'user_stats' in tables:
                db_status = 'connected_with_tables'
            else:
                db_status = f'connected_missing_tables: {tables}'

    except Exception as e:
        db_status = f'error: {str(e)}'

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': db_status,
        'runpod_connected': check_runpod_connection()
    })

@app.route('/init-db', methods=['POST'])
def init_db_endpoint():
    """Initialize database tables"""
    try:
        init_database()
        return jsonify({'success': True, 'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'error': f'Database initialization failed: {str(e)}'}), 500

@app.route('/admin/users', methods=['GET'])
def list_users():
    """List all registered users (for debugging)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.username, u.email, u.created_at, u.last_login,
                       s.total_programs, s.current_streak, s.favorite_goal
                FROM users u
                LEFT JOIN user_stats s ON u.id = s.user_id
                ORDER BY u.created_at DESC
            ''')
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'created_at': row['created_at'],
                    'last_login': row['last_login'],
                    'total_programs': row['total_programs'] or 0,
                    'current_streak': row['current_streak'] or 0,
                    'favorite_goal': row['favorite_goal'] or 'strength'
                })

            return jsonify({
                'success': True,
                'users': users,
                'total_count': len(users)
            })
    except Exception as e:
        return jsonify({'error': f'Failed to list users: {str(e)}'}), 500

def check_runpod_connection():
    """Check if RunPod AI server is available"""
    try:
        response = requests.get(f"{RUNPOD_API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'error': 'Username, email, and password required'}), 400

        username = data['username']
        email = data['email']
        password_hash = hash_password(data['password'])

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

            # Create new user (email_verified = TRUE for now)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, email_verified)
                VALUES (?, ?, ?, TRUE)
            ''', (username, email, password_hash))

            user_id = cursor.lastrowid
            conn.commit()

            # Initialize user stats
            cursor.execute('''
                INSERT INTO user_stats (user_id, total_programs, current_streak, favorite_goal, avg_days_per_week)
                VALUES (?, 0, 0, 'strength', 3.0)
            ''', (user_id,))
            conn.commit()

            return jsonify({
                'success': True,
                'message': 'Account created successfully!'
            })

    except Exception as e:
        print(f"Signup error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Signup failed'}), 500

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
                # Update last login
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                             (datetime.now(), user['id']))
                conn.commit()

                # Set session
                session['user_id'] = user['id']
                session['username'] = user['username']

                # Get user stats
                cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user['id'],))
                stats = cursor.fetchone()

                if not stats:
                    # Create default stats if they don't exist
                    cursor.execute('''
                        INSERT INTO user_stats (user_id, total_programs, current_streak, favorite_goal, avg_days_per_week)
                        VALUES (?, 0, 0, 'strength', 3.0)
                    ''', (user['id'],))
                    conn.commit()
                    stats = {
                        'total_programs': 0,
                        'current_streak': 0,
                        'favorite_goal': 'strength',
                        'avg_days_per_week': 3.0
                    }
                else:
                    stats = {
                        'total_programs': stats['total_programs'],
                        'current_streak': stats['current_streak'],
                        'favorite_goal': stats['favorite_goal'],
                        'avg_days_per_week': stats['avg_days_per_week']
                    }

                return jsonify({
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'stats': {
                            'totalPrograms': stats['total_programs'],
                            'currentStreak': stats['current_streak'],
                            'favoriteGoal': stats['favorite_goal'],
                            'avgDaysPerWeek': stats['avg_days_per_week']
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

@app.route('/api/generate-program', methods=['POST'])
def generate_program_fallback():
    """Generate program using fallback method when RunPod is not available"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create a simple fallback program
        program_data = {
            'Day 1': 'Upper Pull Day:\n• Pull-ups: 4x8\n• Rows: 3x10\n• Bicep Curls: 3x12',
            'Day 2': 'Upper Push Day:\n• Dips: 4x8\n• Push-ups: 3x12\n• Tricep Extensions: 3x10',
            'Day 3': 'Lower Body Day:\n• Squats: 4x10\n• Lunges: 3x12\n• Calf Raises: 3x15'
        }

        response = {
            'weekly_program': program_data,
            'generated_at': datetime.now().isoformat(),
            'model_type': 'Fallback generation (RunPod not connected)'
        }

        return jsonify(response)

    except Exception as e:
        print(f"❌ Error in fallback generation: {e}")
        return jsonify({'error': 'Program generation failed'}), 500

# Auto-initialize database on import (for production)
try:
    init_database()
    print("✅ Database auto-initialized on startup")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")

if __name__ == '__main__':
    print("🚀 Starting Simple Fitness App API Server...")

    # Initialize database again to be sure
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)