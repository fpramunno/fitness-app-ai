#!/usr/bin/env python3
"""
Flask API Server for Streetlifting Program Generator
Connects the Expo React Native app to the Python LLM backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback
import requests
from datetime import datetime

# Import assessment class (no heavy dependencies)
try:
    from assessment import StreetliftingAssessment
    print("✅ Successfully imported assessment class")
except ImportError as e:
    print(f"❌ Could not import assessment: {e}")
    print("Make sure assessment.py exists")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for React Native

# Model server configuration
MODEL_SERVER_URL = "http://localhost:3001"

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
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate-program', methods=['POST'])
def generate_program():
    """Generate a streetlifting program based on assessment"""
    try:
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

        # Create assessment object
        assessment = StreetliftingAssessment(
            weighted_pullups_max=int(data.get('weighted_pullups_max', 0)),
            weighted_dips_max=int(data.get('weighted_dips_max', 0)),
            muscle_ups=int(data.get('muscle_ups', 0)),
            rows_max=int(data.get('rows_max', 0)),
            pushups_max=int(data.get('pushups_max', 0)),
            squats_max=int(data.get('squats_max', 0)),
            training_days_per_week=int(data.get('training_days_per_week', 3)),
            mesocycle_week=int(data.get('mesocycle_week', 1)),
            primary_goal=data.get('primary_goal', 'strength')
        )

        print(f"🏋️ Generating program for: {assessment.primary_goal} goal, {assessment.training_days_per_week} days/week")

        # Generate program by calling model server for each day
        weekly_program = {}
        for day in range(1, assessment.training_days_per_week + 1):
            session_data = {
                'weighted_pullups_max': assessment.weighted_pullups_max,
                'weighted_dips_max': assessment.weighted_dips_max,
                'muscle_ups': assessment.muscle_ups,
                'rows_max': assessment.rows_max,
                'pushups_max': assessment.pushups_max,
                'squats_max': assessment.squats_max,
                'training_days_per_week': assessment.training_days_per_week,
                'mesocycle_week': assessment.mesocycle_week,
                'primary_goal': assessment.primary_goal,
                'day': day
            }
            
            # Call model server for this day's session
            response = requests.post(f"{MODEL_SERVER_URL}/generate", 
                                   json=session_data, 
                                   timeout=60)
            
            if response.status_code == 200:
                session_result = response.json()
                weekly_program[day] = session_result['session']
            else:
                print(f"❌ Error generating day {day}: {response.text}")
                weekly_program[day] = f"Error generating session for day {day}"

        # Create response in expected format
        response = {
            'id': str(int(datetime.now().timestamp())),
            'weekly_program': weekly_program,
            'assessment': {
                'weighted_pullups_max': assessment.weighted_pullups_max,
                'weighted_dips_max': assessment.weighted_dips_max,
                'muscle_ups': assessment.muscle_ups,
                'rows_max': assessment.rows_max,
                'pushups_max': assessment.pushups_max,
                'squats_max': assessment.squats_max,
                'training_days_per_week': assessment.training_days_per_week,
                'mesocycle_week': assessment.mesocycle_week,
                'primary_goal': assessment.primary_goal
            },
            'created_at': datetime.now().isoformat(),
            'generated_with_llm': True
        }

        print(f"✅ Program generated successfully with {len(weekly_program)} days")
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error generating program: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Program generation failed',
            'message': str(e),
            'fallback_available': False
        }), 500

@app.route('/api/model-status', methods=['GET'])
def model_status():
    """Get information about the model server"""
    try:
        if not check_model_server():
            return jsonify({
                'model_loaded': False,
                'error': 'Model server not available'
            }), 503
        
        # Get status from model server
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
    print("🚀 Starting Streetlifting Program Generator API Server...")
    print("📡 This server will connect to model server at http://localhost:3001")
    print("⚠️  Make sure to run model_server.py first!")
    print("🌐 Starting Flask server on http://localhost:3000")
    app.run(host='0.0.0.0', port=3000, debug=False)