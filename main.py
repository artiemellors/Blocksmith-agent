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
from orchestrator import AgenticOrchestrator
from simple_config import load_simple_config, create_simple_config_template


# Load environment variables
load_dotenv()


def load_config(config_file: str) -> TrainingBlockInput:
    """
    Load configuration from either YAML or simple text format.

    Detects format based on file extension:
    - .yaml or .yml -> YAML format
    - .txt or .conf -> Simple text format

    Args:
        config_file: Path to the configuration file

    Returns:
        TrainingBlockInput object
    """
    file_path = Path(config_file)

    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    # Detect format by extension
    ext = file_path.suffix.lower()

    if ext in ['.txt', '.conf']:
        return load_simple_config(config_file)
    elif ext in ['.yaml', '.yml']:
        return load_config_from_yaml(config_file)
    else:
        raise ValueError(
            f"Unknown configuration file format: {ext}\n"
            "Supported formats: .txt, .conf (simple text) or .yaml, .yml (YAML)"
        )


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
    help='Path to configuration file (.txt, .yaml, or .yml)'
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

    # Load configuration (auto-detects format)
    click.echo(f"Loading configuration from: {config}")
    try:
        input_data = load_config(config)
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
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=True),
    required=True,
    help='Path to configuration file (.txt, .yaml, or .yml)'
)
@click.option(
    '--output-dir',
    '-o',
    type=click.Path(),
    default='output-agentic',
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
def generate_agentic(config, output_dir, api_key, model, save_layers):
    """Generate a training block using the agentic architecture (Stage 2 - Parallel Coach Agents)."""

    if not api_key:
        click.echo("Error: API key not provided. Set ANTHROPIC_API_KEY environment variable or use --api-key", err=True)
        sys.exit(1)

    click.echo(f"\n{'='*60}")
    click.echo("Blocksmith - Agentic Architecture (Stage 2)")
    click.echo(f"{'='*60}\n")

    # Load configuration (auto-detects format)
    click.echo(f"Loading configuration from: {config}")
    try:
        input_data = load_config(config)
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
    click.echo(f"Model: {model}")
    click.echo(f"\nStage 2: Planning + Parallel Coach Agents")
    click.echo(f"Future Stages: Coordinator Agent, QA Agent\n")

    # Confirm
    if not click.confirm("Proceed with agentic generation?"):
        click.echo("Cancelled.")
        sys.exit(0)

    # Generate using agentic architecture
    try:
        orchestrator = AgenticOrchestrator(gen_config, api_key)
        summary = orchestrator.run_generate(input_data)

        click.echo(f"\n{'='*60}")
        click.echo("STAGE 2 COMPLETE!")
        click.echo(f"{'='*60}")
        click.echo(f"\nGeneration summary saved to:")
        click.echo(f"  {Path(output_dir) / 'AGENTIC_STAGE_2_SUMMARY.md'}")

        if save_layers:
            click.echo(f"\nAgent outputs saved in: {output_dir}/")
            click.echo(f"  Phase 1 (Planning):")
            click.echo(f"    - agentic_layer_0_context.md")
            click.echo(f"    - agentic_layer_1_skeleton.md")
            click.echo(f"  Phase 2 (Parallel Coaches):")
            click.echo(f"    - agentic_layer_2_running.md")
            click.echo(f"    - agentic_layer_3_strength.md")
            click.echo(f"    - agentic_layer_4_strength_endurance.md")
            click.echo(f"    - agentic_layer_5_hyrox.md")
            click.echo(f"    - agentic_layer_6_recovery.md")

        click.echo(f"\nNext: Implement Stage 3 (Programming Coordinator)")
        click.echo(f"      Implement Stage 4 (Quality Assurance Agent)")

    except Exception as e:
        click.echo(f"\n✗ Generation failed: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('output_file', type=click.Path())
def create_config(output_file):
    """Create a sample YAML configuration file.

    For a simpler format, use: create-config-simple
    """

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
  primary_goal: "BUILD"  # Examples: BUILD, PEAK, Base building, etc.
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
@click.argument('output_file', type=click.Path())
def create_config_simple(output_file):
    """Create a simple text configuration file (RECOMMENDED).

    This format is much easier to edit than YAML!
    Just key=value pairs, no indentation needed.
    """
    try:
        create_simple_config_template(output_file)
        click.echo(f"✓ Simple text configuration created: {output_file}")
        click.echo(f"\nThis format is easier to edit - just change the values!")
        click.echo(f"\nEdit this file with your details, then run:")
        click.echo(f"  python main.py generate --config {output_file}")
    except Exception as e:
        click.echo(f"✗ Error creating configuration: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("Blocksmith v1.0.0")
    click.echo("Automated HYROX Training Block Generator")


if __name__ == '__main__':
    cli()
