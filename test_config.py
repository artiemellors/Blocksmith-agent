#!/usr/bin/env python3
"""
Simple test script to validate configuration loading.
"""
import sys
from main import load_config_from_yaml


def test_config_loading():
    """Test loading the example configuration."""
    print("Testing configuration loading...")

    try:
        config = load_config_from_yaml("example_config.yaml")
        print("✓ Configuration loaded successfully!")

        print(f"\nAthlete: {config.athlete_profile.name}")
        print(f"Age: {config.athlete_profile.age}")
        print(f"HR Max: {config.athlete_profile.physiological_params.hr_max}")
        print(f"T1 Pace: {config.athlete_profile.physiological_params.threshold_t1_pace}")
        print(f"T2 Pace: {config.athlete_profile.physiological_params.threshold_t2_pace}")

        print(f"\nBlock Objectives:")
        print(f"  Goal: {config.block_objectives.primary_goal}")
        print(f"  Week 1 Mileage: {config.block_objectives.running_mileage_week1} km")
        print(f"  Weekly Progression: {config.block_objectives.weekly_progression_percent}%")
        print(f"  Duration: {config.block_objectives.block_duration_weeks} weeks")
        print(f"  Deload: {config.block_objectives.deload_week}")

        print(f"\nWeek Structure:")
        print(f"  Rest Day: {config.athlete_profile.week_structure.rest_day}")
        print(f"  Training Days: {config.athlete_profile.week_structure.get_training_days_range()}")
        print(f"  Main Sessions/Week: {config.athlete_profile.week_structure.main_sessions_per_week}")
        print(f"  Double Days: {config.athlete_profile.week_structure.double_days}")
        print(f"  Runs/Week: {config.athlete_profile.week_structure.runs_per_week}")
        print(f"  Long Run Day: {config.athlete_profile.week_structure.long_run_day}")

        print(f"\nInjury Information:")
        print(f"  Active Injuries: {config.athlete_profile.injury_info.active_injuries or 'None'}")
        print(f"  Pain Threshold (during): {config.athlete_profile.injury_info.pain_threshold_during}/10")
        print(f"  Pain Threshold (next day): {config.athlete_profile.injury_info.pain_threshold_next_day}/10")

        if config.athlete_profile.race_category:
            print(f"\nHYROX Configuration:")
            print(f"  Race Category: {config.athlete_profile.race_category}")
            print(f"  Weights Auto-Loaded: Yes")

        print("\n✓ All configuration fields validated successfully!")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_config_loading()
    sys.exit(0 if success else 1)
