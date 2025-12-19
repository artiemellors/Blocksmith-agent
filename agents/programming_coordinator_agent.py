"""
Programming Coordinator Agent - Block assembly and progression specialist.
Coordinates all sessions into a complete training block with progressive overload.
"""
from .base_agent import BaseAgent
from models import AthleteProfile, BlockObjectives


class ProgrammingCoordinatorAgent(BaseAgent):
    """
    Programming Coordinator Agent assembles and progresses the training block.

    Responsibilities:
    - Assemble Week 1 from all coach outputs
    - Apply progressive overload for Weeks 2-4
    - Design deload week (if enabled)
    - Ensure coherence across the entire block
    - Manage intensity distribution and recovery
    """

    def get_agent_name(self) -> str:
        return "Programming Coordinator Agent"

    def get_system_prompt(self) -> str:
        return """You are an elite programming coordinator specializing in periodization and progressive overload.

**Your Expertise:**
- Periodization theory and block programming
- Progressive overload principles (volume, intensity, density)
- Deload design and recovery management
- Training coherence and session sequencing
- Hard/easy day alternation and double-session placement
- Phase-specific progression strategies
- HYROX-specific periodization

**Your Role:**
You coordinate all specialist coach outputs into a complete, coherent training block. You are the architect who ensures:
- Week 1 is properly assembled from all coach sessions
- Progressive overload is applied correctly for Weeks 2-4
- Deload week (if included) properly reduces volume while maintaining sharpness
- Training days follow the athlete's week structure
- Hard and easy days alternate appropriately
- Double-session days are well-balanced

**Key Principles:**

**Progressive Overload (Weeks 2-4):**
- Volume increases follow phase-appropriate rates (BASE: 10%, BUILD: 5%, PEAK: 2.5%)
- Running mileage scales by the weekly progression percentage
- Strength volume increases via: reps → sets → load (in that order)
- HYROX volume scales conservatively (station work %, run distance)
- Intensity should NOT increase significantly - progression is volume-driven
- Complexity can increase slightly (e.g., shorter rest, tighter pacing windows)

**Deload Week Design:**
- Volume reduced to ~60% of peak week (Week 3 or 4)
- Intensity maintained or slightly reduced (keeps neural patterns sharp)
- Running: reduce mileage but keep some quality work at race pace
- Strength: reduce sets/reps, maintain load on key lifts
- HYROX: reduce station volume, keep some race-pace segments
- Recovery: maintain or increase recovery modalities

**Session Assembly & Coherence:**
- Respect the athlete's week structure (rest days, double days, long run day)
- Hard sessions should NOT be back-to-back
- Double-day sessions should balance AM/PM (e.g., quality AM, easy PM)
- Long run must be on the specified day (non-negotiable)
- Total sessions per week must match main_sessions_per_week
- Consider cumulative fatigue across the week

**Phase-Specific Progression:**
- BASE: Volume increases, technique focus, aerobic foundation
- BUILD: Threshold work increases, moderate volume increases
- PEAK: Race-specific work, conservative volume increases, intensity maintenance
- TAPER: Volume decreases, intensity maintained, sharpening focus
- TRANSITION: Minimal progression, recovery emphasis

**Your Approach:**
- Read all coach outputs carefully to understand Week 1
- Calculate volume increases based on phase and progression rate
- Apply progressive overload intelligently (not just "add more")
- Design deload as strategic recovery, not just "less"
- Ensure each week is coherent and executable
- Provide clear progression notes for the athlete

You create complete training blocks that build fitness progressively while managing fatigue and ensuring long-term development."""

    async def coordinate_training_block(
        self,
        athlete_profile: AthleteProfile,
        block_objectives: BlockObjectives,
        global_context: str,
        week_skeleton: str,
        running_sessions: str,
        strength_sessions: str,
        hyrox_session: str,
        recovery_session: str
    ) -> str:
        """
        Coordinate all coach outputs into a complete training block.

        Args:
            athlete_profile: Complete athlete information
            block_objectives: Training block goals and structure
            global_context: Global training context from Planning Agent
            week_skeleton: Week 1 skeleton from Planning Agent
            running_sessions: Running sessions from Running Coach
            strength_sessions: Strength sessions from Strength Coach (max + SE)
            hyrox_session: HYROX session from HYROX Specialist
            recovery_session: Recovery session from Recovery Coach

        Returns:
            Complete training block with Weeks 1-4 (+ deload if enabled)
        """
        # Calculate weekly volumes using the new VolumeProgressionStrategy
        weekly_volumes = block_objectives.get_weekly_volumes()

        # Get number of weeks for the block
        num_weeks = block_objectives.block_duration_weeks

        # Prepare week structure info
        rest_day = athlete_profile.week_structure.rest_day
        training_days = athlete_profile.week_structure.get_training_days_range()
        double_days = athlete_profile.week_structure.double_days
        long_run_day = athlete_profile.week_structure.long_run_day
        main_sessions = athlete_profile.week_structure.main_sessions_per_week

        # Format weekly volumes for prompt
        volume_schedule = "\n".join([
            f"- Week {i+1}: {vol}km ({block_objectives.get_progression_percent():+.1f}% from Week {i})"
            for i, vol in enumerate(weekly_volumes)
        ])

        prompt = f"""Coordinate all coach outputs into a complete {num_weeks}-week training block{" + deload week" if block_objectives.deload_week else ""}.

**Athlete Week Structure:**
- Rest Day: {rest_day}
- Training Days: {training_days}
- Main Sessions/Week: {main_sessions}
- Double Days: {double_days}
- Long Run Day: {long_run_day}

**Training Phase:** {block_objectives.primary_goal.value}

**Running Volume Schedule:**
{volume_schedule}
{"- Deload Week: " + str(int(weekly_volumes[-1] * 0.6)) + "km (~60% of peak week)" if block_objectives.deload_week else ""}

**Progression Rate:** {block_objectives.get_progression_percent():+.1f}% per week (phase-appropriate)

**Coach Outputs to Coordinate:**

### Running Sessions (Week 1)
{running_sessions}

### Strength Sessions (Week 1)
{strength_sessions}

### HYROX Combo Session (Week 1)
{hyrox_session}

### Recovery Session (Week 1)
{recovery_session}

---

**Your Task:**

1. **Assemble Week 1:**
   - Organize all coach sessions into a coherent weekly schedule
   - Assign each session to a specific day (respecting week structure)
   - Ensure hard/easy alternation and proper double-day balance
   - Long run MUST be on {long_run_day}
   - Total sessions should equal {main_sessions}
   - Show full details for each session (as provided by coaches)

2. **Build Weeks 2-{num_weeks} with Progressive Overload:**
   - Apply phase-appropriate volume increases
   - Running: Follow the volume schedule above
   - Strength: Increase via reps → sets → load (in that order)
   - HYROX: Scale station work % and run distances conservatively
   - Maintain intensity, increase volume
   - Provide clear "Week X Changes" notes for each week

3. {"Design Deload Week (Week " + str(num_weeks + 1) + "):" if block_objectives.deload_week else "Skip deload (not requested):"}
   {"- Reduce volume to ~60% of peak week" if block_objectives.deload_week else "- No deload week in this block"}
   {"- Maintain intensity on key sessions" if block_objectives.deload_week else ""}
   {"- Keep some race-pace work for sharpness" if block_objectives.deload_week else ""}
   {"- Emphasize recovery and adaptation" if block_objectives.deload_week else ""}
   {"- Show which sessions are modified and how" if block_objectives.deload_week else ""}

**Output Format:**

# {block_objectives.primary_goal.value} Training Block - {num_weeks} Weeks{" + Deload" if block_objectives.deload_week else ""}

## Week 1

**Monday** ({rest_day if rest_day == "Monday" else "Training Day"})
[Session details or REST]

**Tuesday**
[Session details - AM/PM if double day]

[Continue for all 7 days...]

**Week 1 Summary:**
- Total Running: [X]km
- Total Sessions: [X]
- Quality Days: [days]
- Recovery Days: [days]

---

## Week 2

**Week 2 Changes:**
- Running volume: [X]km (+Y% from Week 1)
- Strength progression: [specific changes]
- HYROX progression: [specific changes]

[Continue with daily breakdown...]

---

[Repeat for Weeks 3-{num_weeks}...]

"""
        # Add deload week section if enabled
        deload_section = ""
        if block_objectives.deload_week:
            deload_section = """
---

## Deload Week

**Deload Strategy:**
[Explain volume reduction and what's maintained]

[Daily breakdown...]

"""

        prompt += deload_section + """
**Block Summary:**
- Phase: {block_objectives.primary_goal.value}
- Total Weeks: {num_weeks + (1 if block_objectives.deload_week else 0)}
- Running Volume Progression: [Week 1-{num_weeks} range]
- Focus Areas Addressed: {", ".join(block_objectives.specific_focus_areas)}

**Progression Notes:**
[Overall progression strategy and athlete guidance]

---

Create a complete, coherent training block that progressively builds fitness while managing fatigue."""

        # Build context from all inputs
        context = f"{global_context}\n\n---\n\n{week_skeleton}"

        return await self.generate(prompt, context=context, max_tokens=16000)
