"""
Running Coach Agent - Running session specialist.
Designs quality and endurance running sessions.
"""
from .base_agent import BaseAgent
from models import AthleteProfile, BlockObjectives


class RunningCoachAgent(BaseAgent):
    """
    Running Coach Agent designs all running sessions.

    Responsibilities:
    - Quality runs (threshold, intervals, VO2 max)
    - Endurance runs (long Z2, easy Z2)
    - Mileage distribution and progression
    - Pace and intensity management
    """

    def get_agent_name(self) -> str:
        return "Running Coach Agent"

    def get_system_prompt(self) -> str:
        return """You are an elite running coach specializing in HYROX and hybrid athlete training.

**Your Expertise:**
- Running mechanics and economy for hybrid athletes
- Threshold training and lactate clearance
- VO2 max development
- Endurance base building
- Pacing strategies for compromised running (post-HYROX stations)
- Progressive overload in running volume and intensity
- Injury-aware programming and running substitutions

**Your Role:**
You design all running sessions for the training block. Your sessions must:
- Build running economy and speed for HYROX racing
- Develop aerobic base through Z2 endurance work
- Improve threshold and VO2 max capacity
- Distribute mileage appropriately across the week
- Balance high-intensity and recovery running
- Provide clear pacing guidelines (pace zones, HR zones, RPE)

**Key Principles:**
- Running volume must be distributed across quality and endurance sessions
- Quality sessions (threshold, intervals) need precise pacing and rest intervals
- Long runs anchor the week and build aerobic base
- Easy runs promote recovery and maintain weekly volume
- Every session needs clear warm-up, main work, and cooldown structure
- Progression must be calculated and intentional (distance, intensity, or volume)
- Always provide substitutions for injury management (bike/erg alternatives)

**Your Approach:**
- Be specific with paces (T1, T2) and heart rate zones
- Provide both time and distance metrics where applicable
- Include drills and form cues for running economy
- Design sessions that transfer directly to HYROX performance
- Think about cumulative fatigue across the week
- Ensure recovery between hard efforts

You create running sessions that build the aerobic engine and speed needed for HYROX success."""

    async def design_running_sessions(
        self,
        athlete_profile: AthleteProfile,
        block_objectives: BlockObjectives,
        global_context: str,
        week_skeleton: str
    ) -> str:
        """
        Design all running sessions for Week 1.

        Args:
            athlete_profile: Complete athlete information
            block_objectives: Training block goals
            global_context: Global training context from Planning Agent
            week_skeleton: Week 1 skeleton from Planning Agent

        Returns:
            Detailed running session designs
        """
        runs = athlete_profile.week_structure.runs_per_week
        long_run_day = athlete_profile.week_structure.long_run_day
        weekend_min = athlete_profile.week_structure.weekend_session_time_min
        weekend_max = athlete_profile.week_structure.weekend_session_time_max
        t1_pace = athlete_profile.physiological_params.threshold_t1_pace
        t2_pace = athlete_profile.physiological_params.threshold_t2_pace

        prompt = f"""Design all running sessions for Week 1 based on the skeleton plan.

**Objectives:**

- Total weekly volume: **{block_objectives.running_mileage_week1}km** (Week 1), distributed across {runs} runs.
- Gradual build: +{block_objectives.weekly_progression_percent}% mileage per week in following weeks.
- Cover 2x Quality sessions (threshold / intervals), 1x Long Z2 run, 1x Easy Z2 run.
- Alternate hard and easy days; avoid stacking high intensity.
- Assign each run clear **purpose** (e.g., Threshold Intervals for clearance, Long Run for base).

**Structure required in output:**

For each running session, include:

- **Purpose** (why it's in the program)
- **Warm-up** (HR/RPE, drills if relevant)
- **Main set** (intervals/tempos, target pace [T1 = {t1_pace}/km, T2 = {t2_pace}/km], HR zone, RPE, distance/duration)
- **Cooldown** (easy jog, HR zone, distance/time)
- **Progression knob** (how to scale in later weeks — e.g., add reps, extend interval length, tighten rest)

**Rules:**

- Long run anchored on {long_run_day} ({weekend_min}–{weekend_max} min, Z2).
- Easy run ≤60 min, Z2, recovery emphasis.
- Threshold/interval runs must reference both **pace zones (T1, T2)** and **HR zones** as dials.
- Where distance and time could be used, provide both (e.g., "6x1km at T1, ~{t1_pace}/km pace, HR Z3–4, 3 min jog rest").

**Output convention:**

- Present as a **list of {runs} running sessions** (not the whole week).
- Label them clearly by session type: *Run Quality 1 (Threshold Intervals)*, *Run Quality 2 (Progression Run)*, *Endurance Run (Long Z2)*, *Endurance Run (Easy Z2)*.
- Ensure total mileage sums to approximately {block_objectives.running_mileage_week1}km.

Design running sessions that build the speed and endurance foundation for HYROX success."""

        context = f"{global_context}\n\n---\n\n{week_skeleton}"
        return await self.generate(prompt, context=context)
