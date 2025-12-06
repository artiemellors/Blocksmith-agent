"""
Training block generator engine.
Orchestrates the layer-by-layer generation process.
"""
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from models import TrainingBlockInput, GenerationConfig, HyroxWeights
from ai_providers import get_provider
from prompts import (
    get_layer_0_prompt,
    get_layer_1_prompt,
    get_layer_2_prompt,
    get_layer_3_prompt,
    get_layer_4_prompt,
    get_layer_5_prompt,
    get_layer_6_prompt,
    get_layer_7_prompt,
    get_week_progression_prompt,
    get_deload_prompt,
)


class TrainingBlockGenerator:
    """Generates complete training blocks through layered prompting."""

    def __init__(self, config: GenerationConfig, api_key: str = None):
        """
        Initialize the generator.

        Args:
            config: Generation configuration
            api_key: API key (optional, will try environment variables)
        """
        self.config = config

        # Get the appropriate AI provider
        self.provider = get_provider(
            provider_name=config.provider,
            model_name=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            api_key=api_key
        )

        self.layer_outputs: Dict[str, str] = {}

        # Create output directory
        self.output_dir = Path(config.output_directory)
        self.output_dir.mkdir(exist_ok=True)

    def generate_layer(
        self,
        layer_name: str,
        prompt: str,
        context: Optional[str] = None,
        save_output: bool = True
    ) -> str:
        """
        Generate a single layer using Claude API.

        Args:
            layer_name: Name of the layer (e.g., "Layer 0")
            prompt: The prompt for this layer
            context: Optional context from previous layers
            save_output: Whether to save the output to a file

        Returns:
            Generated text for this layer
        """
        print(f"\n{'='*60}")
        print(f"Generating {layer_name}...")
        print(f"{'='*60}\n")

        # Build the full prompt with context if provided
        full_prompt = prompt
        if context:
            full_prompt = f"{context}\n\n---\n\n{prompt}"

        # Call AI provider (abstracted)
        try:
            output = self.provider.generate(full_prompt)

            # Save output
            self.layer_outputs[layer_name] = output

            if save_output and self.config.save_intermediate_layers:
                output_file = self.output_dir / f"{layer_name.replace(' ', '_').lower()}.md"
                with open(output_file, 'w') as f:
                    f.write(f"# {layer_name}\n\n")
                    f.write(output)
                print(f"✓ Saved to {output_file}")

            # Delay to respect rate limits (3 seconds for lower-tier API accounts)
            time.sleep(3)

            return output

        except Exception as e:
            print(f"✗ Error generating {layer_name}: {str(e)}")
            raise

    def generate_complete_block(self, input_data: TrainingBlockInput) -> str:
        """
        Generate a complete training block through all layers.

        Args:
            input_data: Complete input for block generation

        Returns:
            Final assembled training block
        """
        athlete = input_data.athlete_profile
        objectives = input_data.block_objectives

        # Get race-specific HYROX weights
        hyrox_weights = HyroxWeights.get_weights(objectives.race_type)

        # Prepare injury context
        injury_context = ""
        if athlete.injury_info.active_injuries:
            injury_context = "**Active Injuries:** " + ", ".join(athlete.injury_info.active_injuries)

        # Add previous block context if provided
        previous_block_context = ""
        if input_data.previous_training_block:
            previous_block_context = f"\n\n**Previous Training Block (for context):**\n{input_data.previous_training_block[:3000]}...\n"

        # Layer 0: Context & Global Rules
        layer_0_prompt = get_layer_0_prompt(athlete, objectives, injury_context)
        if previous_block_context:
            layer_0_prompt += previous_block_context
        if input_data.additional_context:
            layer_0_prompt += f"\n\n**Additional Context:**\n{input_data.additional_context}\n"

        layer_0 = self.generate_layer("Layer 0", layer_0_prompt)

        # Layer 1: Week 1 Skeleton
        layer_1 = self.generate_layer(
            "Layer 1",
            get_layer_1_prompt(objectives, athlete),
            context=layer_0
        )

        # Layer 2: Running Sessions
        layer_2 = self.generate_layer(
            "Layer 2",
            get_layer_2_prompt(
                objectives,
                athlete.physiological_params.threshold_t1_pace,
                athlete.physiological_params.threshold_t2_pace,
                athlete
            ),
            context=f"{layer_0}\n\n{layer_1}"
        )

        # Layer 3: Max Strength Sessions
        layer_3 = self.generate_layer(
            "Layer 3",
            get_layer_3_prompt(objectives),
            context=f"{layer_0}\n\n{layer_1}"
        )

        # Layer 4: Strength Endurance Sessions
        layer_4 = self.generate_layer(
            "Layer 4",
            get_layer_4_prompt(hyrox_weights),
            context=f"{layer_0}\n\n{layer_1}"
        )

        # Layer 5: HYROX Combo / Brick Session
        layer_5 = self.generate_layer(
            "Layer 5",
            get_layer_5_prompt(hyrox_weights, objectives),
            context=f"{layer_0}\n\n{layer_1}"
        )

        # Layer 6: Aerobic Engine/Recovery & Minis
        layer_6 = self.generate_layer(
            "Layer 6",
            get_layer_6_prompt(),
            context=f"{layer_0}\n\n{layer_1}"
        )

        # Layer 7: Assemble Week 1
        week_1_context = f"{layer_0}\n\n{layer_1}\n\n{layer_2}\n\n{layer_3}\n\n{layer_4}\n\n{layer_5}\n\n{layer_6}"
        week_1 = self.generate_layer(
            "Layer 7 - Week 1",
            get_layer_7_prompt(objectives, athlete),
            context=week_1_context
        )

        # Weeks 2-4: Progressive Build
        weeks = {1: week_1}
        for week_num in range(2, objectives.block_duration_weeks + 1):
            week_context = f"{layer_0}\n\n{weeks[week_num - 1]}"
            week = self.generate_layer(
                f"Layer {7 + week_num - 1} - Week {week_num}",
                get_week_progression_prompt(week_num, weeks[week_num - 1], objectives, athlete),
                context=week_context
            )
            weeks[week_num] = week

        # Deload Week (if enabled)
        if objectives.deload_week:
            deload_week_num = objectives.block_duration_weeks + 1
            deload_context = f"{layer_0}\n\n{weeks[objectives.block_duration_weeks]}"
            week_deload = self.generate_layer(
                f"Layer {7 + objectives.block_duration_weeks} - Week {deload_week_num} Deload",
                get_deload_prompt(
                    deload_week_num,
                    weeks[objectives.block_duration_weeks],
                    objectives,
                    athlete
                ),
                context=deload_context
            )
            weeks[deload_week_num] = week_deload

        # Create Block Summary Index
        progression_pct = objectives.get_progression_percent()
        summary_content = f"""# {athlete.name}'s Training Block - {objectives.primary_goal} Phase

## Block Overview

**Duration:** {objectives.block_duration_weeks} weeks + {'1 deload week' if objectives.deload_week else 'no deload'}
**Starting Mileage:** {objectives.running_mileage_week1} km/week
**Progression:** {progression_pct:+.1f}% per week
**Focus Areas:** {', '.join(objectives.specific_focus_areas) if objectives.specific_focus_areas else 'General development'}

## Generated Weeks

"""
        for week_num in sorted(weeks.keys()):
            week_type = "Deload" if week_num == objectives.block_duration_weeks + 1 else "Build"
            mileage = objectives.running_mileage_week1 * (1 + (progression_pct / 100)) ** (week_num - 1)
            if week_type == "Deload":
                mileage = mileage * 0.65

            summary_content += f"""### Week {week_num} ({week_type})
- **File:** `layer_{7 + week_num - 1}_-_week_{week_num}.md`
- **Target Mileage:** ~{mileage:.1f} km
- **Sessions:** {athlete.week_structure.main_sessions_per_week} main sessions

"""

        summary_content += f"""
## How to Use This Block

1. **Start with Week 1** - Open the Week 1 file and follow the detailed session prescriptions
2. **Progress through each week** - Each week file contains complete session details with progression guidelines
3. **Monitor your response** - Use the intensity audits at the end of each week to verify you're hitting the target zones
4. **Adjust as needed** - Follow the substitution protocols if pain/soreness exceeds thresholds

## Files Generated

- `layer_0.md` - Context and global rules
- `layer_1.md` - Week 1 skeleton
- `layer_2.md` - Running sessions detail
- `layer_3.md` - Max strength sessions detail
- `layer_4.md` - Strength endurance sessions detail
- `layer_5.md` - HYROX combo/brick session detail
- `layer_6.md` - Aerobic engine/recovery session detail
- `layer_7_-_week_1.md` - **Complete Week 1**
"""

        for week_num in range(2, len(weeks) + 1):
            if week_num == objectives.block_duration_weeks + 1:
                summary_content += f"- `layer_{7 + week_num - 1}_-_week_{week_num}_deload.md` - **Complete Week {week_num} (Deload)**\n"
            else:
                summary_content += f"- `layer_{7 + week_num - 1}_-_week_{week_num}.md` - **Complete Week {week_num}**\n"

        summary_content += "\n---\n\n*Generated by Blocksmith - Automated HYROX Training Block Generator*"

        # Save the block summary
        summary_file = self.output_dir / "BLOCK_SUMMARY.md"
        with open(summary_file, 'w') as f:
            f.write(summary_content)

        print(f"\n{'='*60}")
        print(f"✓ Complete training block generated!")
        print(f"✓ Block summary saved to {summary_file}")
        print(f"✓ Individual week files saved in {self.output_dir}/")
        print(f"{'='*60}\n")

        return summary_content

    def get_layer_output(self, layer_name: str) -> Optional[str]:
        """Get the output from a specific layer."""
        return self.layer_outputs.get(layer_name)

    def save_summary(self):
        """Save a summary of all generated layers."""
        summary_file = self.output_dir / "generation_summary.md"
        with open(summary_file, 'w') as f:
            f.write("# Training Block Generation Summary\n\n")
            for layer_name in self.layer_outputs.keys():
                f.write(f"- {layer_name}: ✓\n")
            f.write(f"\nTotal layers generated: {len(self.layer_outputs)}\n")
        print(f"✓ Summary saved to {summary_file}")
