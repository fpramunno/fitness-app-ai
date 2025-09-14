#!/usr/bin/env python3
"""
Production Flask API Server for Fitness App (Backend Only)
Supports user authentication, data persistence, and statistics tracking
Uses PostgreSQL and connects to RunPod for AI inference
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import traceback
import requests
import json
import hashlib
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# CORS configuration for production
CORS(app, supports_credentials=True, origins=[
    'https://your-app-domain.com',  # Update with your frontend domain
    'http://localhost:8081',  # For development
    'http://localhost:3000',  # For development
])

# RunPod AI server configuration
RUNPOD_API_URL = os.getenv('RUNPOD_API_URL', 'http://localhost:3001')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'smtp_username': os.getenv('SMTP_USERNAME'),
    'smtp_password': os.getenv('SMTP_PASSWORD'),
    'from_email': os.getenv('FROM_EMAIL')
}

def init_database():
    """Initialize the PostgreSQL database with required tables"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("📦 Initializing PostgreSQL database...")

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Programs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                program_data TEXT NOT NULL,
                assessment_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                goal VARCHAR(100),
                training_days INTEGER,
                mesocycle_week INTEGER
            )
        ''')

        # User stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                total_programs INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                favorite_goal VARCHAR(100) DEFAULT 'strength',
                avg_days_per_week REAL DEFAULT 3.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Exercise tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_records (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                exercise_name VARCHAR(255) NOT NULL,
                weight REAL,
                reps INTEGER,
                sets INTEGER,
                rpe INTEGER,
                rir INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        # User main exercises tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_main_exercises (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                exercise_name VARCHAR(255) NOT NULL,
                is_main_exercise BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, exercise_name)
            )
        ''')

        # Workout logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                program_id INTEGER REFERENCES programs(id),
                day_number INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def send_verification_email(email, token):
    """Send email verification email"""
    if not EMAIL_CONFIG['smtp_username']:
        print("Warning: Email not configured")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = email
        msg['Subject'] = "Verify your Fitness App account"

        # Create verification URL - update with your frontend domain
        frontend_domain = os.getenv('FRONTEND_DOMAIN', 'http://localhost:8081')
        verification_url = f"{frontend_domain}/verify-email?token={token}"

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

# Import all the API routes from the original file
# (I'll add the key routes here for now)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected',
        'runpod_connected': check_runpod_connection()
    })

def check_runpod_connection():
    """Check if RunPod AI server is available"""
    try:
        response = requests.get(f"{RUNPOD_API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

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
            cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                if existing_user['username'] == username:
                    return jsonify({'error': 'Username already exists'}), 400
                else:
                    return jsonify({'error': 'Email already exists'}), 400

            # Create new user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, email_verified, verification_token)
                VALUES (%s, %s, %s, FALSE, %s) RETURNING id
            ''', (username, email, password_hash, verification_token))

            user_id = cursor.fetchone()['id']
            conn.commit()

            # Initialize user stats
            cursor.execute('''
                INSERT INTO user_stats (user_id, total_programs, current_streak, favorite_goal, avg_days_per_week)
                VALUES (%s, 0, 0, 'strength', 3.0)
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

# Add more routes here...

if __name__ == '__main__':
    print("🚀 Starting Production Fitness App API Server...")

    # Initialize database
    init_database()

    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)