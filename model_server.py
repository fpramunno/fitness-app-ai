#!/usr/bin/env python3
"""
Model Server - Runs the LLM model on your laptop's GPU
Separate process from the API server to prevent blocking
"""

from flask import Flask, request, jsonify
import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path to import program_generator
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

try:
    from program_generator import StreetliftingProgramGenerator, StreetliftingAssessment
    print("✅ Successfully imported program_generator")
except ImportError as e:
    print(f"❌ Could not import program_generator: {e}")
    print("Make sure program_generator.py is in the parent directory")
    sys.exit(1)

app = Flask(__name__)

# Global generator instance
generator = None

def initialize_generator():
    """Initialize the program generator"""
    global generator
    try:
        print("🤖 Initializing LLM Program Generator on GPU...")
        generator = StreetliftingProgramGenerator()
        print("✅ Generator initialized successfully")
        print(f"🎯 Model device: {next(generator.model.parameters()).device}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        traceback.print_exc()
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'generator_ready': generator is not None,
        'device': str(next(generator.model.parameters()).device) if generator else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/generate', methods=['POST'])
def generate_weekly_program():
    """Generate a complete weekly program"""
    try:
        if generator is None:
            return jsonify({
                'error': 'Model not initialized',
                'message': 'The model failed to load.'
            }), 500

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create assessment object
        assessment = StreetliftingAssessment(
            bodyweight_pullups_max=int(data.get('bodyweight_pullups_max', 0)),
            weighted_pullups_max=int(data.get('weighted_pullups_max', 0)),
            bodyweight_dips_max=int(data.get('bodyweight_dips_max', 0)),
            weighted_dips_max=int(data.get('weighted_dips_max', 0)),
            bodyweight_muscle_ups_max=int(data.get('bodyweight_muscle_ups_max', 0)),
            weighted_muscle_ups_max=int(data.get('weighted_muscle_ups_max', 0)),
            bodyweight_squats_max=int(data.get('bodyweight_squats_max', 0)),
            weighted_squats_max=int(data.get('weighted_squats_max', 0)),
            bodyweight_pushups_max=int(data.get('bodyweight_pushups_max', 0)),
            training_days_per_week=int(data.get('training_days_per_week', 3)),
            mesocycle_week=int(data.get('mesocycle_week', 1)),
            primary_goal=data.get('primary_goal', 'strength'),
            athlete_description=data.get('athlete_description', '')
        )

        print(f"🏋️ Generating complete weekly program, goal: {assessment.primary_goal}")

        # Generate complete weekly program
        weekly_program = generator.generate_weekly_program(assessment)

        response = {
            'weekly_program': weekly_program,
            'generated_at': datetime.now().isoformat(),
            'model_type': 'Fine-tuned LLM' if generator.is_fine_tuned else 'Base model'
        }

        print(f"✅ Weekly program generated successfully")
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error generating weekly program: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Weekly program generation failed',
            'message': str(e)
        }), 500

@app.route('/model-status', methods=['GET'])
def model_status():
    """Get model information"""
    if generator is None:
        return jsonify({
            'model_loaded': False,
            'error': 'Generator not initialized'
        }), 500
    
    return jsonify({
        'model_loaded': True,
        'is_fine_tuned': generator.is_fine_tuned,
        'device': str(next(generator.model.parameters()).device),
        'model_type': 'Fine-tuned LLM' if generator.is_fine_tuned else 'Base model'
    })

if __name__ == '__main__':
    print("🚀 Starting Model Server (GPU inference only)...")
    
    if initialize_generator():
        print("🌐 Starting model server on http://localhost:3001")
        app.run(host='0.0.0.0', port=3001, debug=False)
    else:
        print("❌ Cannot start model server - generator initialization failed")
        sys.exit(1)