"""
Agentic Orchestrator for Blocksmith
Manages the workflow of specialist agents to generate training blocks.
"""
import asyncio
from pathlib import Path
from typing import Dict, Optional
from anthropic import Anthropic

from models import TrainingBlockInput, GenerationConfig
from agents import PlanningAgent


class AgenticOrchestrator:
    """
    Orchestrates multiple specialist agents to generate training blocks.

    Stage 1: Planning Agent only
    Future stages: Will add coach agents, coordinator, and QA agent
    """

    def __init__(self, config: GenerationConfig, api_key: str):
        """
        Initialize the orchestrator.

        Args:
            config: Generation configuration
            api_key: Anthropic API key
        """
        self.config = config
        self.client = Anthropic(api_key=api_key)
        self.outputs: Dict[str, str] = {}

        # Create output directory
        self.output_dir = Path(config.output_directory)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize agents
        self.planning_agent = PlanningAgent(
            client=self.client,
            model_name=config.model_name
        )

    def save_output(self, name: str, content: str, description: str = ""):
        """
        Save an output to a file.

        Args:
            name: Filename (without extension)
            content: Content to save
            description: Optional description for logging
        """
        if not self.config.save_intermediate_layers:
            return

        output_file = self.output_dir / f"{name}.md"
        with open(output_file, 'w') as f:
            if description:
                f.write(f"# {description}\n\n")
            f.write(content)

        print(f"✓ Saved to {output_file}")

    async def generate_training_block(self, input_data: TrainingBlockInput) -> str:
        """
        Generate a complete training block using specialist agents.

        Stage 1: Uses Planning Agent only (proof of concept)
        Future stages: Will orchestrate multiple agents in parallel

        Args:
            input_data: Complete input for block generation

        Returns:
            Summary of generated content
        """
        athlete = input_data.athlete_profile
        objectives = input_data.block_objectives

        print(f"\n{'='*60}")
        print(f"Starting Agentic Training Block Generation")
        print(f"{'='*60}\n")
        print(f"Athlete: {athlete.name}, {athlete.age} years old")
        print(f"Block: {objectives.primary_goal} - {objectives.block_duration_weeks} weeks")
        print(f"Starting Mileage: {objectives.running_mileage_week1}km/week")
        print(f"\n{'='*60}\n")

        # Prepare injury context
        injury_context = ""
        if athlete.injury_info.active_injuries:
            injury_context = "**Active Injuries:** " + ", ".join(athlete.injury_info.active_injuries)

        # Prepare previous block context
        previous_block_context = ""
        if input_data.previous_training_block:
            previous_block_context = f"\n\n**Previous Training Block (for context):**\n{input_data.previous_training_block[:3000]}...\n"

        # Prepare additional context
        additional_context = ""
        if input_data.additional_context:
            additional_context = f"\n\n**Additional Context:**\n{input_data.additional_context}\n"

        # ============================================================
        # STAGE 1: PLANNING AGENT
        # ============================================================

        print("\n" + "="*60)
        print("PHASE 1: Strategic Planning")
        print("="*60 + "\n")

        # Generate global context and week skeleton
        global_context, week_skeleton = await self.planning_agent.create_complete_plan(
            athlete_profile=athlete,
            block_objectives=objectives,
            injury_context=injury_context,
            previous_block_context=previous_block_context,
            additional_context=additional_context
        )

        # Save outputs
        self.save_output(
            "agentic_layer_0_context",
            global_context,
            "Global Training Context & Rules (Planning Agent)"
        )
        self.save_output(
            "agentic_layer_1_skeleton",
            week_skeleton,
            "Week 1 Skeleton (Planning Agent)"
        )

        # Store for future use
        self.outputs["global_context"] = global_context
        self.outputs["week_skeleton"] = week_skeleton

        # ============================================================
        # FUTURE STAGES: Coach agents, assembly, progression, QA
        # ============================================================

        # Stage 2 will add: Running Coach, Strength Coach, HYROX Specialist, Recovery Coach (parallel)
        # Stage 3 will add: Programming Coordinator (assembly & progression)
        # Stage 4 will add: QA Agent (validation & regeneration)

        # Create summary for Stage 1
        summary = self._create_stage_1_summary(athlete, objectives)

        print(f"\n{'='*60}")
        print(f"✓ Stage 1 Complete - Planning Agent Proof of Concept")
        print(f"{'='*60}\n")

        return summary

    def _create_stage_1_summary(self, athlete, objectives) -> str:
        """Create a summary for Stage 1 output."""
        summary = f"""# Blocksmith Agentic Generation - Stage 1 (Planning Agent)

## Block Overview

**Athlete:** {athlete.name}, {athlete.age} years old
**Phase:** {objectives.primary_goal}
**Duration:** {objectives.block_duration_weeks} weeks + {'1 deload week' if objectives.deload_week else 'no deload'}
**Starting Mileage:** {objectives.running_mileage_week1} km/week
**Progression:** +{objectives.weekly_progression_percent}% per week
**Focus Areas:** {', '.join(objectives.specific_focus_areas) if objectives.specific_focus_areas else 'General development'}

## Stage 1 Outputs

### Planning Agent (Proof of Concept)

✓ **Global Training Context** - `agentic_layer_0_context.md`
  - Athlete analysis and physiological parameters
  - Training zones and progression strategy
  - Injury protocols and safety guardrails
  - Session distribution principles

✓ **Week 1 Skeleton** - `agentic_layer_1_skeleton.md`
  - Weekly schedule with session archetypes
  - Intensity distribution (high/low days)
  - Mileage allocation across running sessions
  - Strategic justification for session placement

## Next Stages (Not Yet Implemented)

**Stage 2:** Specialist Coach Agents (parallel session design)
- Running Coach Agent
- Strength Coach Agent
- HYROX Specialist Agent
- Recovery Coach Agent

**Stage 3:** Programming Coordinator (assembly & progression)
- Week 1 assembly
- Weeks 2-4 progressive build
- Deload week design

**Stage 4:** Quality Assurance Agent (validation)
- Constraint validation
- Regeneration loops
- Quality checks

## How to Use These Outputs

The Planning Agent has created:
1. **Strategic foundation** - All training rules and athlete context
2. **Weekly blueprint** - Session types and when they occur

In future stages, specialist coaches will use these to design detailed sessions.

---

*Generated by Blocksmith Agentic Architecture (Stage 1 - Proof of Concept)*
"""

        # Save summary
        summary_file = self.output_dir / "AGENTIC_STAGE_1_SUMMARY.md"
        with open(summary_file, 'w') as f:
            f.write(summary)

        print(f"✓ Stage 1 summary saved to {summary_file}")

        return summary

    def run_generate(self, input_data: TrainingBlockInput) -> str:
        """
        Synchronous wrapper for generate_training_block.

        Args:
            input_data: Complete input for block generation

        Returns:
            Summary of generated content
        """
        return asyncio.run(self.generate_training_block(input_data))
