#!/usr/bin/env python3
"""
Blocksmith - Automated HYROX Training Block Generator
CLI interface for generating training blocks.
"""
import os
import sys
from pathlib import Path
import click
import yaml
from dotenv import load_dotenv

from models import (
    TrainingBlockInput,
    AthleteProfile,
    PhysiologicalParameters,
    BlockObjectives,
    InjuryInformation,
    GenerationConfig,
)
from generator import TrainingBlockGenerator


# Load environment variables
load_dotenv()


def load_config_from_yaml(config_file: str) -> TrainingBlockInput:
    """
    Load training block configuration from a YAML file.

    Args:
        config_file: Path to the YAML configuration file

    Returns:
        TrainingBlockInput object
    """
    with open(config_file, 'r') as f:
        data = yaml.safe_load(f)

    # Build the athlete profile
    phys_params = PhysiologicalParameters(**data['physiological_parameters'])

    injury_info = InjuryInformation()
    if 'injury_information' in data:
        injury_info = InjuryInformation(**data['injury_information'])

    athlete = AthleteProfile(
        name=data['athlete']['name'],
        age=data['athlete']['age'],
        physiological_params=phys_params,
        injury_info=injury_info
    )

    # Build block objectives
    objectives = BlockObjectives(**data['block_objectives'])

    # Load previous block if path provided
    previous_block = None
    if 'previous_training_block_file' in data and data['previous_training_block_file']:
        prev_file = Path(data['previous_training_block_file'])
        if prev_file.exists():
            with open(prev_file, 'r') as f:
                previous_block = f.read()

    # Additional context
    additional_context = data.get('additional_context', None)

    return TrainingBlockInput(
        athlete_profile=athlete,
        block_objectives=objectives,
        previous_training_block=previous_block,
        additional_context=additional_context
    )


@click.group()
def cli():
    """Blocksmith - Automated HYROX Training Block Generator"""
    pass


@cli.command()
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=True),
    required=True,
    help='Path to YAML configuration file'
)
@click.option(
    '--output-dir',
    '-o',
    type=click.Path(),
    default='output',
    help='Output directory for generated files'
)
@click.option(
    '--api-key',
    '-k',
    envvar='ANTHROPIC_API_KEY',
    help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
)
@click.option(
    '--model',
    '-m',
    default='claude-sonnet-4-5-20250929',
    help='Claude model to use'
)
@click.option(
    '--save-layers/--no-save-layers',
    default=True,
    help='Save intermediate layer outputs'
)
def generate(config, output_dir, api_key, model, save_layers):
    """Generate a complete training block from a configuration file."""

    if not api_key:
        click.echo("Error: API key not provided. Set ANTHROPIC_API_KEY environment variable or use --api-key", err=True)
        sys.exit(1)

    click.echo(f"\n{'='*60}")
    click.echo("Blocksmith - Training Block Generator")
    click.echo(f"{'='*60}\n")

    # Load configuration
    click.echo(f"Loading configuration from: {config}")
    try:
        input_data = load_config_from_yaml(config)
    except Exception as e:
        click.echo(f"Error loading configuration: {str(e)}", err=True)
        sys.exit(1)

    # Create generation config
    gen_config = GenerationConfig(
        model_name=model,
        save_intermediate_layers=save_layers,
        output_directory=output_dir
    )

    # Display summary
    click.echo(f"\nAthlete: {input_data.athlete_profile.name}, {input_data.athlete_profile.age} years old")
    click.echo(f"Block Type: {input_data.block_objectives.primary_goal}")
    click.echo(f"Duration: {input_data.block_objectives.block_duration_weeks} weeks + {'deload' if input_data.block_objectives.deload_week else 'no deload'}")
    click.echo(f"Starting Mileage: {input_data.block_objectives.running_mileage_week1} km/week")
    click.echo(f"Output Directory: {output_dir}")
    click.echo(f"Model: {model}\n")

    # Confirm
    if not click.confirm("Proceed with generation?"):
        click.echo("Cancelled.")
        sys.exit(0)

    # Generate
    try:
        generator = TrainingBlockGenerator(gen_config, api_key)
        final_block = generator.generate_complete_block(input_data)
        generator.save_summary()

        click.echo(f"\n{'='*60}")
        click.echo("SUCCESS!")
        click.echo(f"{'='*60}")
        click.echo(f"\nYour complete training block is ready at:")
        click.echo(f"  {Path(output_dir) / 'complete_training_block.md'}")

        if save_layers:
            click.echo(f"\nIntermediate layers saved in: {output_dir}/")

    except Exception as e:
        click.echo(f"\n✗ Generation failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('output_file', type=click.Path())
def create_config(output_file):
    """Create a sample configuration file."""

    sample_config = """# Blocksmith Training Block Configuration

athlete:
  name: "Arthur Mellors"
  age: 41

physiological_parameters:
  hr_max: 188
  threshold_t1_pace: "4:37"  # mm:ss per km
  threshold_t2_pace: "4:17"  # mm:ss per km

injury_information:
  active_injuries: []  # e.g., ["quad pain", "shoulder soreness"]
  pain_threshold_during: 2  # 0-10 scale
  pain_threshold_next_day: 3  # 0-10 scale
  soreness_cutoff_hours: 36
  volume_reduction_percent: 25

block_objectives:
  primary_goal: "REBUILD"  # REBUILD, BUILD, PEAK, etc.
  running_mileage_week1: 40  # km
  weekly_progression_percent: 10  # % increase per week
  block_duration_weeks: 4  # number of build weeks
  deload_week: true  # include deload week after build weeks
  specific_focus_areas:
    - "threshold running"
    - "sled work"
    - "wall balls"

# Optional: Path to previous training block markdown file
previous_training_block_file: null  # e.g., "previous_block.md"

# Optional: Additional context or special requests
additional_context: null
"""

    with open(output_file, 'w') as f:
        f.write(sample_config)

    click.echo(f"✓ Sample configuration created: {output_file}")
    click.echo(f"\nEdit this file with your details, then run:")
    click.echo(f"  python main.py generate --config {output_file}")


@cli.command()
def version():
    """Show version information."""
    click.echo("Blocksmith v1.0.0")
    click.echo("Automated HYROX Training Block Generator")


if __name__ == '__main__':
    cli()
