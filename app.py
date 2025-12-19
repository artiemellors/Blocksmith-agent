"""
Blocksmith Flask Web Application
Web interface for generating HYROX training blocks using the agentic architecture.
"""
import os
import asyncio
from flask import Flask, render_template, request, jsonify, send_file, session
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
import uuid

from models import (
    TrainingBlockInput,
    AthleteProfile,
    PhysiologicalParameters,
    BlockObjectives,
    InjuryInformation,
    GenerationConfig,
    TrainingWeekStructure,
    TrainingPhase
)
from orchestrator import AgenticOrchestrator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'blocksmith-dev-key-change-in-production')

# Store generation results temporarily (in production, use Redis or database)
generation_results = {}


@app.route('/')
def index():
    """Render the main form."""
    return render_template('index.html')


def convert_pace_to_mmss(decimal_minutes):
    """Convert decimal minutes (e.g., 5.5) to mm:ss format (e.g., '05:30')."""
    minutes = int(decimal_minutes)
    seconds = int((decimal_minutes - minutes) * 60)
    return f"{minutes:02d}:{seconds:02d}"


@app.route('/generate', methods=['POST'])
def generate_block():
    """Generate a training block from form data."""
    try:
        data = request.json

        # Build week structure
        week_structure = TrainingWeekStructure(
            rest_day=data.get('rest_day', 'Monday'),
            main_sessions_per_week=int(data.get('main_sessions_per_week', 8)),
            double_days=data.get('double_days', 'Wednesday, Saturday'),
            runs_per_week=int(data.get('runs_per_week', 4)),
            long_run_day=data.get('long_run_day', 'Sunday'),
            weekday_session_time_min=int(data.get('weekday_session_time_min', 45)),
            weekday_session_time_max=int(data.get('weekday_session_time_max', 75)),
            weekend_session_time_min=int(data.get('weekend_session_time_min', 90)),
            weekend_session_time_max=int(data.get('weekend_session_time_max', 105))
        )

        # Build physiological parameters
        # Convert decimal pace to mm:ss format
        t1_pace_decimal = float(data.get('T1_pace_min_per_km', 5.5))
        t2_pace_decimal = float(data.get('T2_pace_min_per_km', 4.8))

        phys_params = PhysiologicalParameters(
            hr_max=int(data.get('hr_max', 180)),
            threshold_t1_pace=convert_pace_to_mmss(t1_pace_decimal),
            threshold_t2_pace=convert_pace_to_mmss(t2_pace_decimal),
            vo2_max=int(data.get('vo2_max_ml_kg_min', 50)) if data.get('vo2_max_ml_kg_min') else None
        )

        # Build injury information
        injury_info = InjuryInformation(
            current_injuries=data.get('current_injuries', []),
            injury_history=data.get('injury_history', []),
            movement_restrictions=data.get('movement_restrictions', [])
        )

        # Build athlete profile
        athlete = AthleteProfile(
            name=data.get('name', 'Athlete'),
            age=int(data.get('age', 30)),
            physiological_params=phys_params,
            injury_info=injury_info,
            week_structure=week_structure,
            race_category=data.get('race_category')
        )

        # Build block objectives
        primary_goal = TrainingPhase[data.get('primary_goal', 'BUILD')]

        block_objectives = BlockObjectives(
            primary_goal=primary_goal,
            running_mileage_week1=float(data.get('running_mileage_week1', 40.0)),
            block_duration_weeks=int(data.get('block_duration_weeks', 4)),
            deload_week=data.get('deload_week', 'true').lower() == 'true',
            specific_focus_areas=data.get('specific_focus_areas', [])
        )

        # Create temporary output directory
        session_id = str(uuid.uuid4())
        output_dir = Path(tempfile.gettempdir()) / 'blocksmith' / session_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build generation config
        gen_config = GenerationConfig(
            output_dir=str(output_dir),
            model_name=data.get('model_name', 'claude-sonnet-4-5-20250929'),
            max_tokens=int(data.get('max_tokens', 16000)),
            temperature=float(data.get('temperature', 1.0))
        )

        # Build complete input
        training_input = TrainingBlockInput(
            athlete_profile=athlete,
            block_objectives=block_objectives,
            config=gen_config
        )

        # Run the orchestrator asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            AgenticOrchestrator(training_input).run_generate()
        )
        loop.close()

        # Store results
        generation_results[session_id] = {
            'result': result,
            'output_dir': str(output_dir),
            'timestamp': datetime.now().isoformat(),
            'athlete_name': athlete.name
        }

        return jsonify({
            'success': True,
            'session_id': session_id,
            'summary': {
                'athlete': athlete.name,
                'phase': primary_goal.value,
                'weeks': block_objectives.block_duration_weeks,
                'starting_mileage': block_objectives.running_mileage_week1,
                'total_tokens': result.total_tokens_used,
                'generation_time': f"{result.total_time_seconds:.1f}s"
            }
        })

    except Exception as e:
        app.logger.error(f"Generation failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    """Download generated files."""
    try:
        if session_id not in generation_results:
            return jsonify({'error': 'Session not found'}), 404

        result_data = generation_results[session_id]
        output_dir = Path(result_data['output_dir'])

        # Map file types to filenames
        file_map = {
            'training_block': 'training_block.md',
            'validation_report': 'validation_report.md',
            'summary': 'generation_summary.md'
        }

        if file_type not in file_map:
            return jsonify({'error': 'Invalid file type'}), 400

        file_path = output_dir / file_map[file_type]

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{result_data['athlete_name']}_{file_map[file_type]}"
        )

    except Exception as e:
        app.logger.error(f"Download failed: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/view/<session_id>/<content_type>')
def view_content(session_id, content_type):
    """View generated content as HTML."""
    try:
        if session_id not in generation_results:
            return jsonify({'error': 'Session not found'}), 404

        result_data = generation_results[session_id]
        output_dir = Path(result_data['output_dir'])

        # Map content types to filenames
        content_map = {
            'training_block': 'training_block.md',
            'validation': 'validation_report.md',
            'summary': 'generation_summary.md'
        }

        if content_type not in content_map:
            return jsonify({'error': 'Invalid content type'}), 400

        file_path = output_dir / content_map[content_type]

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        # Read and return content
        with open(file_path, 'r') as f:
            content = f.read()

        return jsonify({
            'success': True,
            'content': content,
            'filename': content_map[content_type]
        })

    except Exception as e:
        app.logger.error(f"View content failed: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/cleanup/<session_id>', methods=['POST'])
def cleanup_session(session_id):
    """Clean up temporary files for a session."""
    try:
        if session_id in generation_results:
            output_dir = Path(generation_results[session_id]['output_dir'])
            if output_dir.exists():
                shutil.rmtree(output_dir)
            del generation_results[session_id]
            return jsonify({'success': True})
        return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        app.logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
