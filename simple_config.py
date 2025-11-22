"""
Simple text format configuration parser.
Reads key=value pairs from a text file.
"""
from models import (
    TrainingBlockInput,
    AthleteProfile,
    PhysiologicalParameters,
    BlockObjectives,
    InjuryInformation,
    TrainingWeekStructure,
)


def parse_bool(value: str) -> bool:
    """Parse a boolean value from string."""
    value = value.strip().lower()
    if value in ('yes', 'true', '1', 'y'):
        return True
    elif value in ('no', 'false', '0', 'n', ''):
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value}. Use yes/no, true/false, or 1/0")


def parse_list(value: str) -> list:
    """Parse a comma-separated list."""
    if not value.strip():
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def load_simple_config(file_path: str) -> TrainingBlockInput:
    """
    Load configuration from a simple text file.

    Format:
        key=value
        # Comments start with #

    Lists are comma-separated:
        specific_focus_areas=threshold running, sled work, wall balls

    Booleans can be: yes/no, true/false, 1/0
    """
    config = {}

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse key=value
            if '=' not in line:
                raise ValueError(f"Line {line_num}: Invalid format. Expected 'key=value', got: {line}")

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            config[key] = value

    # Required fields
    required_fields = [
        'name', 'age', 'hr_max', 'threshold_t1_pace', 'threshold_t2_pace',
        'primary_goal', 'running_mileage_week1'
    ]

    missing = [field for field in required_fields if field not in config]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Build physiological parameters
    phys_params = PhysiologicalParameters(
        hr_max=int(config['hr_max']),
        threshold_t1_pace=config['threshold_t1_pace'],
        threshold_t2_pace=config['threshold_t2_pace']
    )

    # Build injury information
    injury_info = InjuryInformation(
        active_injuries=parse_list(config.get('active_injuries', '')),
        pain_threshold_during=int(config.get('pain_threshold_during', 2)),
        pain_threshold_next_day=int(config.get('pain_threshold_next_day', 3)),
        soreness_cutoff_hours=int(config.get('soreness_cutoff_hours', 36)),
        volume_reduction_percent=int(config.get('volume_reduction_percent', 25))
    )

    # Build week structure (with optional customization)
    week_structure = TrainingWeekStructure(
        rest_day=config.get('rest_day', 'Monday'),
        main_sessions_per_week=int(config.get('main_sessions_per_week', 8)),
        double_days=config.get('double_days', 'Wednesday, Saturday')
    )

    # Build athlete profile
    athlete = AthleteProfile(
        name=config['name'],
        age=int(config['age']),
        physiological_params=phys_params,
        week_structure=week_structure,
        injury_info=injury_info
    )

    # Build block objectives
    objectives = BlockObjectives(
        primary_goal=config['primary_goal'],
        running_mileage_week1=int(config['running_mileage_week1']),
        weekly_progression_percent=int(config.get('weekly_progression_percent', 10)),
        block_duration_weeks=int(config.get('block_duration_weeks', 4)),
        deload_week=parse_bool(config.get('deload_week', 'yes')),
        specific_focus_areas=parse_list(config.get('specific_focus_areas', ''))
    )

    # Optional fields
    previous_block = None
    if config.get('previous_training_block_file'):
        prev_file_path = config['previous_training_block_file']
        try:
            with open(prev_file_path, 'r') as f:
                previous_block = f.read()
        except FileNotFoundError:
            print(f"Warning: Previous training block file not found: {prev_file_path}")

    additional_context = config.get('additional_context', None)
    if additional_context == '':
        additional_context = None

    return TrainingBlockInput(
        athlete_profile=athlete,
        block_objectives=objectives,
        previous_training_block=previous_block,
        additional_context=additional_context
    )


def create_simple_config_template(output_file: str):
    """Create a simple text configuration template."""

    template = """# Blocksmith Training Block Configuration
# Simple text format: key=value
# Lines starting with # are comments

# ============================================================
# ATHLETE INFORMATION
# ============================================================

name=Arthur Mellors
age=41

# ============================================================
# PHYSIOLOGICAL PARAMETERS
# ============================================================

# Maximum heart rate in bpm
hr_max=188

# Threshold paces in mm:ss format (minutes:seconds per km)
threshold_t1_pace=4:37
threshold_t2_pace=4:17

# ============================================================
# INJURY INFORMATION
# ============================================================

# List any active injuries, separated by commas
# Leave empty if no injuries
# Example: active_injuries=quad pain, shoulder soreness
active_injuries=

# Pain thresholds (0-10 scale)
pain_threshold_during=2
pain_threshold_next_day=3

# If soreness lasts longer than this many hours, reduce volume
soreness_cutoff_hours=36

# Percentage to reduce volume if soreness persists
volume_reduction_percent=25

# ============================================================
# TRAINING WEEK STRUCTURE (OPTIONAL)
# ============================================================

# Which day is your rest day?
rest_day=Monday

# Total number of main sessions per week
main_sessions_per_week=8

# Which days should have double sessions (AM + PM)?
# Comma-separated list
# Examples: Wednesday, Saturday OR Tuesday, Thursday, Saturday
double_days=Wednesday, Saturday

# ============================================================
# BLOCK OBJECTIVES
# ============================================================

# Your training goal
# Examples: BUILD, PEAK, Base building, Return to training
primary_goal=BUILD

# Starting weekly running mileage in kilometers
running_mileage_week1=40

# Percentage increase in mileage per week
weekly_progression_percent=10

# Number of build weeks before deload
block_duration_weeks=4

# Include a deload week at the end? (yes/no)
deload_week=yes

# Specific areas to focus on, separated by commas
# Examples: threshold running, sled work, wall balls, VO2 max
specific_focus_areas=threshold running, sled work, wall balls

# ============================================================
# OPTIONAL
# ============================================================

# Path to your previous training block file (leave empty if none)
# Example: previous_training_block_file=blocks/november_2024.md
previous_training_block_file=

# Any additional context or special instructions (leave empty if none)
# Example: additional_context=Focus on shoulder health this block
additional_context=
"""

    with open(output_file, 'w') as f:
        f.write(template)
