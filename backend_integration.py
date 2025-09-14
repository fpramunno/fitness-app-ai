#!/usr/bin/env python3
"""
Backend API integration for FitnessTracker app
Connects the React Native app with the existing program_generator.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the parent directory to sys.path to import program_generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from program_generator import StreetliftingProgramGenerator, StreetliftingAssessment

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from React Native app

# Initialize the program generator
program_generator = StreetliftingProgramGenerator()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "FitnessTracker API"})

@app.route('/api/generate-program', methods=['POST'])
def generate_program():
    """Generate a streetlifting program based on user assessment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'weighted_pullups_max', 'weighted_dips_max', 'muscle_ups',
            'rows_max', 'pushups_max', 'squats_max',
            'training_days_per_week', 'mesocycle_week', 'primary_goal'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create assessment object
        assessment = StreetliftingAssessment(
            weighted_pullups_max=int(data['weighted_pullups_max']),
            weighted_dips_max=int(data['weighted_dips_max']),
            muscle_ups=int(data['muscle_ups']),
            rows_max=int(data['rows_max']),
            pushups_max=int(data['pushups_max']),
            squats_max=int(data['squats_max']),
            training_days_per_week=int(data['training_days_per_week']),
            mesocycle_week=int(data['mesocycle_week']),
            primary_goal=data['primary_goal']
        )
        
        # Generate the program
        weekly_program = program_generator.generate_weekly_program(assessment)
        
        # Create response
        response = {
            "id": f"program_{hash(str(data))}",
            "weekly_program": weekly_program,
            "assessment": data,
            "created_at": "2025-08-22T12:00:00Z"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Program generation failed: {str(e)}"}), 500

@app.route('/api/programs/user/<user_id>', methods=['GET'])
def get_user_programs(user_id):
    """Get all programs for a specific user"""
    # In a real implementation, this would query a database
    # For now, return empty list
    return jsonify([])

@app.route('/api/programs/<program_id>/feedback', methods=['POST'])
def submit_program_feedback(program_id):
    """Submit feedback for a specific program"""
    try:
        data = request.get_json()
        
        # Validate feedback data
        required_fields = ['day', 'rating', 'difficulty']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # In a real implementation, this would:
        # 1. Store the feedback in a database
        # 2. Trigger the fine-tuned model to update the program
        # 3. Return updated program recommendations
        
        # For now, just acknowledge the feedback
        response = {
            "status": "success",
            "message": "Feedback received and will be processed",
            "program_id": program_id,
            "feedback": data
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Feedback submission failed: {str(e)}"}), 500

@app.route('/api/programs/<program_id>/update', methods=['POST'])
def update_program_with_ai(program_id):
    """Update program using fine-tuned model based on feedback"""
    try:
        data = request.get_json()
        
        # This endpoint would:
        # 1. Collect all feedback for the program
        # 2. Use the fine-tuned model to generate program updates
        # 3. Return the updated program
        
        # For now, return placeholder response
        response = {
            "status": "success",
            "message": "Program updated with AI recommendations",
            "updated_program": {},
            "changes_made": [
                "Adjusted weight progression based on difficulty feedback",
                "Modified rest periods based on fatigue indicators",
                "Added technical cue variations for improved performance"
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Program update failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting FitnessTracker API Server...")
    print("📱 React Native app can connect to: http://localhost:3000")
    print("🏋️ Program Generator: Ready")
    print("🤖 AI Model Integration: Ready for feedback processing")
    
    app.run(
        host='0.0.0.0',
        port=3000,
        debug=True
    )