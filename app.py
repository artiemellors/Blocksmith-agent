#!/usr/bin/env python3
"""
Blocksmith Web Interface
Flask application for generating training blocks via web form.
"""
import os
import json
import time
import zipfile
import io
import re
from pathlib import Path
from datetime import datetime
from threading import Thread
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from models import (
    TrainingBlockInput,
    AthleteProfile,
    PhysiologicalParameters,
    BlockObjectives,
    InjuryInformation,
    TrainingWeekStructure,
    GenerationConfig,
)
from generator import TrainingBlockGenerator
from simple_config import validate_week_structure

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'blocksmith-dev-key-change-in-production')

# Store generation progress in memory (use Redis in production)
generation_status = {}


def parse_block_summary(summary_path):
    """Parse BLOCK_SUMMARY.md and extract structured data"""
    with open(summary_path, 'r') as f:
        content = f.read()

    data = {}

    # Extract phase from title (e.g., "BUILD Phase", "PEAK Phase")
    phase_match = re.search(r'Training Block - (\w+) Phase', content)
    data['phase'] = phase_match.group(1) if phase_match else 'BUILD'

    # Extract duration
    duration_match = re.search(r'\*\*Duration:\*\* (.+)', content)
    data['duration'] = duration_match.group(1) if duration_match else '4 weeks'

    # Extract starting mileage
    mileage_match = re.search(r'\*\*Starting Mileage:\*\* (\d+)', content)
    data['starting_mileage'] = int(mileage_match.group(1)) if mileage_match else 30

    # Extract focus areas
    focus_match = re.search(r'\*\*Focus Areas:\*\* (.+)', content)
    data['focus_areas'] = focus_match.group(1) if focus_match else 'General fitness'

    # Extract weeks
    weeks = []
    week_pattern = r'### Week (\d+) \((\w+)\).*?\*\*Target Mileage:\*\* ~([\d.]+) km.*?\*\*Sessions:\*\* (\d+)'

    for match in re.finditer(week_pattern, content, re.DOTALL):
        weeks.append({
            'num': int(match.group(1)),
            'type': match.group(2),
            'mileage': round(float(match.group(3))),
            'sessions': int(match.group(4))
        })

    data['weeks'] = weeks

    # Calculate mileage range for display
    if weeks:
        min_mileage = min(w['mileage'] for w in weeks)
        max_mileage = max(w['mileage'] for w in weeks)
        data['mileage_range'] = f"{min_mileage}-{max_mileage}" if min_mileage != max_mileage else str(min_mileage)
    else:
        data['mileage_range'] = "30-36"

    return data


def generate_block_async(session_id: str, input_data: TrainingBlockInput, api_key: str, output_dir: str, ai_provider: str = 'anthropic', model_name: str = 'claude-sonnet-4-5-20250929'):
    """
    Generate training block asynchronously and update progress.

    Args:
        session_id: Unique session identifier
        input_data: Training block input configuration
        api_key: API key for the selected provider
        output_dir: Output directory for generated files
        ai_provider: AI provider to use ('anthropic', 'openai', or 'gemini')
        model_name: Model to use for generation
    """
    try:
        generation_status[session_id] = {
            'status': 'running',
            'progress': 0,
            'message': 'Starting generation...',
            'error': None
        }

        # Create generation config
        gen_config = GenerationConfig(
            provider=ai_provider,
            model_name=model_name,
            save_intermediate_layers=True,
            output_directory=output_dir
        )

        # Create generator
        generator = TrainingBlockGenerator(gen_config, api_key)

        # Monkey-patch the generate_layer method to track progress
        original_generate_layer = generator.generate_layer
        layer_count = [0]  # Use list for mutable closure
        total_layers = 13  # Approximate number of layers

        def tracked_generate_layer(layer_name: str, prompt: str, context: str = None, save_output: bool = True) -> str:
            layer_count[0] += 1
            progress_pct = min(95, int((layer_count[0] / total_layers) * 100))  # Cap at 95% until complete
            generation_status[session_id].update({
                'progress': progress_pct,
                'message': layer_name  # Send just the layer name, JS will convert to friendly message
            })
            return original_generate_layer(layer_name, prompt, context, save_output)

        generator.generate_layer = tracked_generate_layer

        # Generate the block
        final_block = generator.generate_complete_block(input_data)
        generator.save_summary()

        # Read the block summary content for preview
        summary_file = f'{output_dir}/BLOCK_SUMMARY.md'
        summary_content = ""
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                summary_content = f.read()

        # Collect all relevant files for ZIP download
        output_path = Path(output_dir)
        files_to_zip = []

        # Add BLOCK_SUMMARY.md
        if output_path.joinpath('BLOCK_SUMMARY.md').exists():
            files_to_zip.append(('BLOCK_SUMMARY.md', str(output_path / 'BLOCK_SUMMARY.md')))

        # Add all complete week files (layer_7 onwards)
        for layer_file in sorted(output_path.glob('layer_[7-9]*.md')):
            files_to_zip.append((layer_file.name, str(layer_file)))
        for layer_file in sorted(output_path.glob('layer_1[0-9]*.md')):
            files_to_zip.append((layer_file.name, str(layer_file)))

        # Mark as complete (don't include files_to_zip in status - not JSON serializable)
        generation_status[session_id].update({
            'status': 'complete',
            'progress': 100,
            'message': 'Training block generated successfully!',
            'output_file': summary_file,
            'output_dir': output_dir,
            'summary_content': summary_content,
            '_files_to_zip': files_to_zip,  # Store separately, not returned in JSON
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in generation thread: {error_details}")

        generation_status[session_id].update({
            'status': 'error',
            'progress': 0,
            'message': 'Generation failed',
            'error': str(e)
        })


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors for API routes."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    return error


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions."""
    import traceback
    print(f"Unhandled exception: {traceback.format_exc()}")

    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    raise e


@app.route('/')
def index():
    """Render the main form page."""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    """
    API endpoint to start training block generation.

    Expects JSON with configuration data matching the simple text format.
    Returns a session_id for tracking progress.
    """
    try:
        data = request.json

        # Get AI provider settings from form (default to Anthropic/Claude)
        ai_provider = data.get('ai_provider', 'anthropic')
        model_name = data.get('model_name', 'claude-sonnet-4-5-20250929')

        # Get appropriate API key based on provider
        if ai_provider == "anthropic":
            api_key = os.getenv('ANTHROPIC_API_KEY')
            key_name = 'ANTHROPIC_API_KEY'
        elif ai_provider == "openai":
            api_key = os.getenv('OPENAI_API_KEY')
            key_name = 'OPENAI_API_KEY'
        elif ai_provider == "gemini":
            api_key = os.getenv('GOOGLE_API_KEY')
            key_name = 'GOOGLE_API_KEY'
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown AI provider: {ai_provider}'
            }), 400

        if not api_key:
            return jsonify({
                'success': False,
                'error': f'API key not configured. Please set {key_name} in .env file'
            }), 500

        # Build athlete profile
        phys_params = PhysiologicalParameters(
            hr_max=int(data['hr_max']),
            threshold_t1_pace=data['threshold_t1_pace'],
            threshold_t2_pace=data['threshold_t2_pace']
        )

        # Parse injury information
        active_injuries = []
        if data.get('active_injuries'):
            active_injuries = [i.strip() for i in data['active_injuries'].split(',') if i.strip()]

        injury_info = InjuryInformation(
            active_injuries=active_injuries,
            pain_threshold_during=int(data.get('pain_threshold_during', 2)),
            pain_threshold_next_day=int(data.get('pain_threshold_next_day', 3)),
            soreness_cutoff_hours=int(data.get('soreness_cutoff_hours', 36)),
            volume_reduction_percent=int(data.get('volume_reduction_percent', 25))
        )

        # Build week structure with validation
        week_structure = TrainingWeekStructure(
            rest_days=data.get('rest_days', 'Monday'),
            main_sessions_per_week=int(data['total_sessions_per_week']),
            double_days=data.get('double_days', ''),
            runs_per_week=int(data['runs_per_week']),
            long_run_day=data.get('long_run_day', 'Sunday')
        )

        # Validate week structure
        validate_week_structure(week_structure)

        athlete = AthleteProfile(
            name=data['name'],
            age=int(data['age']),
            physiological_params=phys_params,
            week_structure=week_structure,
            injury_info=injury_info
        )

        # Build block objectives
        specific_focus_areas = []
        if data.get('specific_focus_areas'):
            specific_focus_areas = [f.strip() for f in data['specific_focus_areas'].split(',') if f.strip()]

        # Handle optional weekly progression override
        weekly_override = data.get('weekly_progression_override')
        if weekly_override and str(weekly_override).strip():
            weekly_override = float(weekly_override)
        else:
            weekly_override = None

        objectives = BlockObjectives(
            primary_goal=data['primary_goal'],
            running_mileage_week1=float(data['running_mileage_week1']),
            weekly_progression_override=weekly_override,
            block_duration_weeks=int(data.get('block_duration_weeks', 4)),
            deload_week=data.get('deload_week', 'yes').lower() in ['yes', 'true', '1'],
            race_type=data.get('race_type'),  # Add race category
            specific_focus_areas=specific_focus_areas
        )

        # Handle previous training block file upload
        previous_block = None
        if data.get('previous_block_content'):
            previous_block = data['previous_block_content']

        # Additional context
        additional_context = data.get('additional_context', None)

        # Create input
        input_data = TrainingBlockInput(
            athlete_profile=athlete,
            block_objectives=objectives,
            previous_training_block=previous_block,
            additional_context=additional_context
        )

        # Create unique session ID
        session_id = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

        # Create output directory
        output_dir = f"output/web_generations/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Start generation in background thread
        thread = Thread(target=generate_block_async, args=(session_id, input_data, api_key, output_dir, ai_provider, model_name))
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Generation started',
            'provider': ai_provider,
            'model': model_name
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@app.route('/api/status/<session_id>')
def get_status(session_id):
    """
    Get generation status for a session.

    Returns progress, status, and any error messages.
    """
    try:
        if session_id not in generation_status:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        # Return status but exclude internal fields that aren't JSON serializable
        status = generation_status[session_id].copy()
        status.pop('_files_to_zip', None)  # Remove internal field

        return jsonify({
            'success': True,
            **status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting status: {str(e)}'
        }), 500


@app.route('/success/<generation_id>')
def success(generation_id):
    """Render the success page with parsed block data."""
    try:
        # Parse the block summary
        summary_path = f'output/web_generations/{generation_id}/BLOCK_SUMMARY.md'

        if not os.path.exists(summary_path):
            return "Training block not found", 404

        block_data = parse_block_summary(summary_path)

        return render_template('success.html',
                             generation_id=generation_id,
                             block=block_data)
    except Exception as e:
        return f"Error loading training block: {str(e)}", 500


@app.route('/download/<generation_id>')
def download_by_id(generation_id):
    """
    Download the generated training block as a ZIP file by generation ID.
    """
    try:
        output_dir = f'output/web_generations/{generation_id}'
        output_path = Path(output_dir)

        if not output_path.exists():
            return jsonify({
                'success': False,
                'error': 'Training block not found'
            }), 404

        # Collect files to zip
        files_to_zip = []

        # Add BLOCK_SUMMARY.md
        if output_path.joinpath('BLOCK_SUMMARY.md').exists():
            files_to_zip.append(('BLOCK_SUMMARY.md', str(output_path / 'BLOCK_SUMMARY.md')))

        # Add all complete week files (layer_7 onwards)
        for layer_file in sorted(output_path.glob('layer_[7-9]*.md')):
            files_to_zip.append((layer_file.name, str(layer_file)))
        for layer_file in sorted(output_path.glob('layer_1[0-9]*.md')):
            files_to_zip.append((layer_file.name, str(layer_file)))

        if not files_to_zip:
            return jsonify({
                'success': False,
                'error': 'No files found to download'
            }), 404

        # Create ZIP file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, filepath in files_to_zip:
                if os.path.exists(filepath):
                    zf.write(filepath, filename)

        memory_file.seek(0)

        # Generate download filename with date
        download_name = f'training_block_{datetime.now().strftime("%Y%m%d")}.zip'

        return send_file(
            memory_file,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<session_id>')
def download_file(session_id):
    """
    Download the generated training block as a ZIP file with all relevant files.
    (Legacy API endpoint for backward compatibility)
    """
    if session_id not in generation_status:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404

    status = generation_status[session_id]
    if status['status'] != 'complete':
        return jsonify({
            'success': False,
            'error': 'Generation not complete'
        }), 400

    files_to_zip = status.get('_files_to_zip', [])
    if not files_to_zip:
        return jsonify({
            'success': False,
            'error': 'No files found to download'
        }), 404

    # Create ZIP file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, filepath in files_to_zip:
            if os.path.exists(filepath):
                zf.write(filepath, filename)

    memory_file.seek(0)

    # Generate download filename with date
    download_name = f'training_block_{datetime.now().strftime("%Y%m%d")}.zip'

    return send_file(
        memory_file,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/zip'
    )


if __name__ == '__main__':
    # Create output directory
    os.makedirs('output/web_generations', exist_ok=True)

    # Production vs Development configuration
    is_production = os.getenv('FLASK_ENV') == 'production'

    if is_production:
        # Production: Let gunicorn handle the server (this code won't run)
        # This is just a fallback if someone runs python app.py directly
        app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
    else:
        # Development: Use Flask's built-in server
        app.run(debug=True, host='127.0.0.1', port=5000)
