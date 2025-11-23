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


def validate_week_structure(week_structure: TrainingWeekStructure):
    """
    Validate that the training week structure is logically consistent.

    Raises ValueError if the configuration is invalid.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Get counts
    num_rest_days = week_structure.get_num_rest_days()
    num_training_days = week_structure.get_num_training_days()
    num_double_days = week_structure.get_num_double_days()
    total_sessions = week_structure.main_sessions_per_week
    runs_per_week = week_structure.runs_per_week

    # Validate: must have at least 1 training day
    if num_training_days < 1:
        raise ValueError(
            f"❌ Invalid training week structure\n"
            f"   Rest days: {week_structure.rest_days} ({num_rest_days} days)\n"
            f"   Problem: You need at least 1 training day per week!\n"
            f"   Suggestion: Reduce your rest days to 6 or fewer."
        )

    # Validate: sessions must fit within training days
    min_sessions = num_training_days
    max_sessions = num_training_days * 2  # if all days are doubles

    if total_sessions < min_sessions:
        raise ValueError(
            f"❌ Invalid training week structure\n"
            f"   Rest days: {week_structure.rest_days} ({num_rest_days} days)\n"
            f"   Training days: {num_training_days} days\n"
            f"   Total sessions: {total_sessions}\n"
            f"   Problem: You need at least {min_sessions} sessions ({num_training_days} training days × 1 session minimum)\n"
            f"   Suggestion: Increase total_sessions_per_week to at least {min_sessions}"
        )

    if total_sessions > max_sessions:
        raise ValueError(
            f"❌ Invalid training week structure\n"
            f"   Rest days: {week_structure.rest_days} ({num_rest_days} days)\n"
            f"   Training days: {num_training_days} days\n"
            f"   Total sessions: {total_sessions}\n"
            f"   Problem: You can't fit {total_sessions} sessions in {num_training_days} training days (max is {max_sessions})\n"
            f"   Suggestion: Either reduce total_sessions_per_week to {max_sessions} or reduce rest days"
        )

    # Validate: double days must match the math
    required_double_days = total_sessions - num_training_days

    if num_double_days != required_double_days:
        if required_double_days == 0:
            if week_structure.double_days:
                raise ValueError(
                    f"❌ Invalid training week structure\n"
                    f"   Training days: {num_training_days}\n"
                    f"   Total sessions: {total_sessions}\n"
                    f"   Double days specified: {week_structure.double_days} ({num_double_days} days)\n"
                    f"   Problem: You don't need any double days ({total_sessions} sessions / {num_training_days} training days = 1 per day)\n"
                    f"   Suggestion: Set double_days= (leave empty)"
                )
        else:
            if not week_structure.double_days:
                raise ValueError(
                    f"❌ Invalid training week structure\n"
                    f"   Training days: {num_training_days}\n"
                    f"   Total sessions: {total_sessions}\n"
                    f"   Double days specified: {num_double_days}\n"
                    f"   Double days needed: {required_double_days}\n"
                    f"   Problem: You need {required_double_days} double days to fit {total_sessions} sessions in {num_training_days} training days\n"
                    f"   Suggestion: Specify {required_double_days} days for double_days (e.g., double_days=Wednesday, Saturday)"
                )
            else:
                raise ValueError(
                    f"❌ Invalid training week structure\n"
                    f"   Training days: {num_training_days}\n"
                    f"   Total sessions: {total_sessions}\n"
                    f"   Double days specified: {week_structure.double_days} ({num_double_days} days)\n"
                    f"   Double days needed: {required_double_days}\n"
                    f"   Problem: Mismatch! You specified {num_double_days} double days but need {required_double_days}\n"
                    f"   Suggestion: Adjust double_days to have exactly {required_double_days} days"
                )

    # Validate: runs must not exceed total sessions
    if runs_per_week > total_sessions:
        raise ValueError(
            f"❌ Invalid training week structure\n"
            f"   Total sessions: {total_sessions}\n"
            f"   Runs per week: {runs_per_week}\n"
            f"   Problem: You can't have more runs ({runs_per_week}) than total sessions ({total_sessions})\n"
            f"   Suggestion: Reduce runs_per_week to {total_sessions} or less"
        )

    # Validate: long run day must be a training day
    rest_days_list = week_structure.get_rest_days_list()
    if week_structure.long_run_day in rest_days_list:
        raise ValueError(
            f"❌ Invalid training week structure\n"
            f"   Long run day: {week_structure.long_run_day}\n"
            f"   Rest days: {week_structure.rest_days}\n"
            f"   Problem: Your long run is scheduled on a rest day!\n"
            f"   Suggestion: Change long_run_day to a training day"
        )

    # Validate: long run day is a valid day
    if week_structure.long_run_day not in days:
        raise ValueError(
            f"❌ Invalid training week structure\n"
            f"   Long run day: {week_structure.long_run_day}\n"
            f"   Problem: '{week_structure.long_run_day}' is not a valid day of the week\n"
            f"   Suggestion: Use one of: {', '.join(days)}"
        )


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
    # Support both old and new field names for backward compatibility
    rest_days = config.get('rest_days') or config.get('rest_day', 'Monday')
    total_sessions = config.get('total_sessions_per_week') or config.get('main_sessions_per_week', '8')

    week_structure = TrainingWeekStructure(
        rest_days=rest_days,
        main_sessions_per_week=int(total_sessions),
        double_days=config.get('double_days', 'Wednesday, Saturday'),
        runs_per_week=int(config.get('runs_per_week', 4)),
        long_run_day=config.get('long_run_day', 'Sunday')
    )

    # Validate the training week structure
    validate_week_structure(week_structure)

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
# TRAINING WEEK STRUCTURE
# ============================================================

# Which days do you rest? (comma-separated)
# Examples: Monday OR Monday, Wednesday OR Friday
rest_days=Monday

# How many total sessions per week do you want?
# (System calculates based on your training days how many double days you need)
total_sessions_per_week=8

# Which days should have double sessions (AM + PM)?
# Leave empty if no double days needed, or specify days (comma-separated)
# Examples: Wednesday, Saturday OR Tuesday, Thursday, Saturday
# NOTE: Must match the math (total_sessions - training_days = double_days needed)
double_days=Wednesday, Saturday

# How many of your sessions should be runs?
runs_per_week=4

# Which training day should have your long run?
# Examples: Sunday, Saturday
long_run_day=Sunday

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
