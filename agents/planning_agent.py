"""
Planning Agent - Strategic orchestrator and athlete profiler.
Replaces Layer 0 (Context & Global Rules) and Layer 1 (Week Skeleton).
"""
from .base_agent import BaseAgent
from models import AthleteProfile, BlockObjectives


class PlanningAgent(BaseAgent):
    """
    Planning Agent creates the strategic foundation for training block generation.

    Responsibilities:
    - Analyzes athlete profile, zones, injuries, constraints
    - Creates global training rules and boundaries
    - Designs weekly skeleton (which days get which session types)
    - Determines high/low intensity day distribution
    """

    def get_agent_name(self) -> str:
        return "Planning Agent"

    def get_system_prompt(self) -> str:
        return """You are an elite HYROX coach and strategic training planner with deep expertise in:

**Your Expertise:**
- Periodization and progressive overload principles
- HYROX-specific programming (hybrid athlete training)
- Physiological training zones and intensity management
- Injury management and pain protocols
- Session architecture and weekly structure design

**Your Role:**
You are the strategic orchestrator who sets the foundation for the entire training block. Your job is to:

1. **Analyze the athlete** - Understand their physiology, constraints, injuries, and goals
2. **Establish global rules** - Define training zones, mileage progression, intensity guidelines
3. **Design the weekly skeleton** - Determine which session types occur on which days
4. **Balance intensity** - Ensure proper alternation of hard/easy days to prevent overload

**Your Approach:**
- Be precise with physiological zones and pacing guidelines
- Strictly enforce injury protocols and pain thresholds
- Design sessions that alternate high and low intensity appropriately
- Ensure all HYROX session archetypes are covered each week
- Think strategically about the entire training block, not just individual sessions

**Key Principles:**
- Progressive overload must be calculated and intentional
- Hard/easy day alternation is mandatory for recovery
- Each session must have clear purpose and transfer to HYROX performance
- Injury constraints are non-negotiable - always provide safe substitutions
- Time budgets must be respected (weekday vs weekend session lengths)

You create the blueprint that all other specialist coaches will follow."""

    async def create_training_context(
        self,
        athlete_profile: AthleteProfile,
        block_objectives: BlockObjectives,
        injury_context: str = "",
        previous_block_context: str = "",
        additional_context: str = ""
    ) -> str:
        """
        Create the global training context and rules (replaces Layer 0).

        Args:
            athlete_profile: Complete athlete information
            block_objectives: Training block goals and progression
            injury_context: Information about active injuries
            previous_block_context: Context from previous training block
            additional_context: Any additional notes or requirements

        Returns:
            Global context and rules for the training block
        """
        hr_max = athlete_profile.physiological_params.hr_max
        t1_pace = athlete_profile.physiological_params.threshold_t1_pace
        t2_pace = athlete_profile.physiological_params.threshold_t2_pace

        injury_section = ""
        if injury_context:
            injury_section = f"\n**Current Injury Context:**\n{injury_context}\n"

        prompt = f"""Create the global training context and rules for this athlete.

**Athlete:** {athlete_profile.name}, {athlete_profile.age} years old
**Training Phase:** {block_objectives.primary_goal}
{injury_section}

**Physiological Parameters:**

- HRmax: {hr_max} bpm
- Zones: Z1 = 60–70%, Z2 = 70–80%, Z3 = 80–88%, Z4 = 88–94%, Z5 = 94–100%
- Threshold paces: T1 = {t1_pace}/km, T2 = {t2_pace}/km

**Training Week Structure:**

- Training days: {athlete_profile.week_structure.get_training_days_range()} ({athlete_profile.week_structure.rest_day} = rest)
- Main sessions: {athlete_profile.week_structure.main_sessions_per_week} total per week (includes {athlete_profile.week_structure.get_num_double_days()} double-days)
- Running sessions: {athlete_profile.week_structure.runs_per_week} runs per week
- Long run day: {athlete_profile.week_structure.long_run_day}
- Session time budgets: {athlete_profile.week_structure.weekday_session_time_min}–{athlete_profile.week_structure.weekday_session_time_max} min weekdays; {athlete_profile.week_structure.weekend_session_time_min}–{athlete_profile.week_structure.weekend_session_time_max} min weekends
- Equipment: Gym ({', '.join(athlete_profile.equipment.gym_equipment)}); Home ({', '.join(athlete_profile.equipment.home_equipment)})

**Run Mileage Rule:**

- Weekly run mileage = {block_objectives.running_mileage_week1}km in Week 1, then +{block_objectives.weekly_progression_percent}% per week through Week {block_objectives.block_duration_weeks}.

**Injury Guardrails:**

- Pain ≤{athlete_profile.injury_info.pain_threshold_during}/10 during & ≤{athlete_profile.injury_info.pain_threshold_next_day}/10 next-day → cut volume or swap run→bike
- Soreness >{athlete_profile.injury_info.soreness_cutoff_hours}h → reduce next run volume {athlete_profile.injury_info.volume_reduction_percent}–40%
- Manage plyometric load based on athlete readiness and injury status

**Macrocycle Logic:**

- {block_objectives.block_duration_weeks}-week progressive build + {'1-week deload (cut volume 40–50%, intensity 20%)' if block_objectives.deload_week else 'no deload'}

**Session Archetypes (must appear each microcycle):**

- **Running Quality** (threshold, VO₂, progression, fartlek)
- **Running Endurance** (Z2, long run)
- **Strength (Maximal)** (compound lifts, %1RM)
- **Strength Endurance** (circuits/EMOM/AMRAP including cardio engines)
- **HYROX Combo/Brick** (run + station, compromised running, Zone 4–5)
- **Aerobic Engine/Recovery** (bike/erg steady Z2, technique, mobility)

**Design Rules (apply to every session):**

- Each session must include: Purpose, Warm-up, 2–3 Main Blocks, Cooldown, Transfer Explanation, Progression Dials.
- Occasional overload allowed only in Week {block_objectives.block_duration_weeks}.
- Strength Endurance sessions must **always include cardio modalities (run, SkiErg, RowErg, Echo bike, or bike)** within the session.
- Maintain strict alternation of hard/easy days to avoid burnout.

**Specific Focus Areas:** {', '.join(block_objectives.specific_focus_areas) if block_objectives.specific_focus_areas else 'General HYROX development'}
{previous_block_context}
{additional_context}

**Your Task:**

Analyze this athlete's profile and establish the global training rules and context that will guide all session design. Include:

1. **Athlete Analysis** - Key physiological characteristics, strengths, limiters, injury considerations
2. **Training Philosophy** - How you'll approach this {block_objectives.primary_goal} phase
3. **Progression Strategy** - How mileage and intensity will build over {block_objectives.block_duration_weeks} weeks
4. **Intensity Management** - How you'll balance hard/easy days and prevent overload
5. **Session Distribution Principles** - How you'll arrange different session types across the week
6. **Safety Protocols** - How you'll manage injuries and respect guardrails

Be strategic, precise, and comprehensive. This context will guide all subsequent session design."""

        return await self.generate(prompt)

    async def create_week_skeleton(
        self,
        athlete_profile: AthleteProfile,
        block_objectives: BlockObjectives,
        global_context: str
    ) -> str:
        """
        Create the Week 1 skeleton showing session distribution (replaces Layer 1).

        Args:
            athlete_profile: Complete athlete information
            block_objectives: Training block goals
            global_context: Output from create_training_context

        Returns:
            Week 1 skeleton with session archetypes distributed across days
        """
        sessions = athlete_profile.week_structure.main_sessions_per_week
        training_days = athlete_profile.week_structure.get_training_days_range()
        long_run_day = athlete_profile.week_structure.long_run_day
        weekend_min = athlete_profile.week_structure.weekend_session_time_min
        weekend_max = athlete_profile.week_structure.weekend_session_time_max

        prompt = f"""Using the global training context and rules you just established, design the Week 1 skeleton.

**Objectives:**

- Establish baseline weekly running volume ({block_objectives.running_mileage_week1}km total mileage).
- Balance intensity: alternate hard/easy days, prevent overload.
- Cover all session archetypes (Running Quality, Running Endurance, Max Strength, Strength Endurance, HYROX Combo, Aerobic Engine/Recovery).
- Ensure the week includes a total of {sessions} main sessions across the training days.

**Structure required in output:**

- Show **{training_days}** schedule as a table with columns: *Day | Main AM | Main PM*.
- Indicate run mileage distribution to total {block_objectives.running_mileage_week1}km.
- Label each session by **archetype** only (e.g., "Run Quality – Threshold Intervals," "Strength Endurance – EMOM w/ SkiErg").
- Flag which sessions are high intensity (Z4–5) and which are low/moderate (Z1–3).

**Important constraints:**

- Avoid consecutive high-intensity days.
- Long run should anchor {long_run_day} ({weekend_min}–{weekend_max} min, Zone 2).
- HYROX Combo (Zone 4–5) occurs once this week.
- Distribute {block_objectives.running_mileage_week1}km across all running sessions appropriately.

**Output convention:**

Provide the **skeleton schedule** with:
1. Weekly table showing session archetypes by day
2. Mileage distribution across running sessions
3. Intensity flags (high vs low/moderate)
4. Brief justification for the session distribution

Do NOT provide full session details yet — that will come from specialist coach agents. Just show WHAT sessions occur WHEN and WHY."""

        return await self.generate(prompt, context=global_context)

    async def create_complete_plan(
        self,
        athlete_profile: AthleteProfile,
        block_objectives: BlockObjectives,
        injury_context: str = "",
        previous_block_context: str = "",
        additional_context: str = ""
    ) -> tuple[str, str]:
        """
        Create both the global context and Week 1 skeleton in sequence.

        Args:
            athlete_profile: Complete athlete information
            block_objectives: Training block goals and progression
            injury_context: Information about active injuries
            previous_block_context: Context from previous training block
            additional_context: Any additional notes or requirements

        Returns:
            Tuple of (global_context, week_skeleton)
        """
        # First, create the global training context
        global_context = await self.create_training_context(
            athlete_profile,
            block_objectives,
            injury_context,
            previous_block_context,
            additional_context
        )

        # Then, create the week skeleton using that context
        week_skeleton = await self.create_week_skeleton(
            athlete_profile,
            block_objectives,
            global_context
        )

        return global_context, week_skeleton
