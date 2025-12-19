"""
Running Coach Agent - Running session specialist.
Designs quality and endurance running sessions.
"""
from .base_agent import BaseAgent
from models import AthleteProfile, BlockObjectives, TrainingPhase


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

        # TRANSITION phase gets completely different running prescription
        if block_objectives.primary_goal == TrainingPhase.TRANSITION:
            prompt = f"""Using the Week 1 skeleton from the Planning Agent, expand only the running sessions into full detail.

**TRANSITION PHASE RUNNING PRESCRIPTION:**

This is a RECOVERY phase. Running sessions should be SHORT, EASY, and OPTIONAL.

**Objectives:**

- Total weekly volume: **{block_objectives.running_mileage_week1}km** (Week 1) - should be 50-60% of normal training volume
- ALL runs at Zone 1-2 ONLY (conversational pace, significantly slower than T1)
- NO threshold work, NO intervals, NO tempo runs, NO VO2 sessions
- Duration: 20-40 minutes maximum per run
- Frequency: 2-4 easy runs maximum per week
- Skip runs entirely if feeling tired or sore

**Session Types (ALL easy aerobic):**

1. **Easy Recovery Run** (Zone 1-2)
   - Duration: 20-30 minutes
   - Pace: T1+60 to T1+90 sec/km (very comfortable, conversational)
   - HR: 60-75% max (Zone 1-2)
   - Purpose: Gentle movement, promote blood flow and recovery
   - Can be replaced with easy bike or swim if preferred

2. **Short Easy Run** (Zone 1-2)
   - Duration: 25-40 minutes
   - Pace: T1+45 to T1+75 sec/km (comfortable, easy breathing)
   - HR: 65-75% max (Zone 2)
   - Purpose: Maintain basic aerobic stimulus without stress
   - Optional: Can include 3-5 × 20-30 second VERY light strides (85-90% effort, not max) with full recovery IF feeling fresh

**Structure for each run:**

- **Warm-up:** 5 min walk/very slow jog
- **Main:** Easy running at Zone 1-2, focus on relaxed form
- **Cooldown:** 5 min walk, light stretching
- **Total time:** 20-40 min including warm-up/cooldown

**CRITICAL RULES:**

- If the athlete feels ANY fatigue, cut the run short or skip it entirely
- NEVER push pace - this is recovery, not training
- Walking breaks are encouraged if needed
- Better to do 20 min easy than 40 min moderate
- Can substitute with bike, swim, or elliptical for zero-impact recovery

**Output format:**

Provide 2-4 easy running sessions (based on skeleton) with the structure above. Each should be clearly labeled as "Easy Recovery Run" with duration, pace guidance (as T1+Xs/km), and HR zones. Make it abundantly clear that these are OPTIONAL and should be skipped if the athlete isn't feeling fully recovered."""
        else:
            # All other phases (BASE, BUILD, PEAK, TAPER)
            prompt = f"""Using the Week 1 skeleton from the Planning Agent, expand only the running sessions into full detail.

**CRITICAL CONTEXT:**

Brick sessions (HYROX Combo/Brick layer) provide race-specific running practice but do NOT replace dedicated threshold development. Design true running quality sessions here - these are CLEAN running sessions with proper warm-up, focused effort at target zones, and adequate recovery. Not compromised running. Not fatigued running. Pure physiological development.

**Objectives:**

- Total weekly volume: **{block_objectives.running_mileage_week1}km** (Week 1), distributed across {runs} runs
- Phase-appropriate progression: {block_objectives.get_progression_percent():+.1f}% per week ({block_objectives.primary_goal.value} phase)
- Cover 2x Quality sessions (threshold / intervals), 1x Long Z2 run, 1x Easy Z2 run
- Alternate hard and easy days; avoid stacking high intensity
- Assign each run clear **purpose** (e.g., Threshold Intervals for clearance, Long Run for base)

**Threshold Development (Primary Focus):**

**Duration:** 8-36 minutes of quality threshold work per session

**Available Formats:**
- **Continuous Tempo:** 20-28 min @ T1 pace (builds aerobic foundation)
- **Cruise Intervals:** 2-4 × 8-15 min @ T1, 2-4 min recovery (high volume with brief breaks)
- **Threshold Intervals:** 4-8 × 3-6 min @ T2, 90-120s recovery (practice race pace)
- **Progressive Tempo:** Start @ T1, progress toward T2 (simulate fatigue)

**VO2max Development (Complementary):**

**Pace:** Faster than T2 pace (typically 10-20 seconds per km faster)
**Duration:** 2-5 minute intervals (600m-1200m)
**Formats:** 6-12 × 600m-1200m with 60-120s recovery
**Purpose:** Raise aerobic ceiling, make T2 pace feel more sustainable
**When:** Mid-block or as variation from threshold work

**Design Guidance:**
- Prioritize threshold development - it's the foundation for HYROX
- Choose session duration/format based on athlete fitness, block position, objectives
- Avoid defaulting to 1km repeats just because HYROX uses 1km segments
- Choose the session type that best serves the adaptation goal

**Structure required in output:**

For each running session, include:

- **Purpose** (why it's in the program)
- **Warm-up** (HR/RPE, drills if relevant)
- **Main set** (intervals/tempos, target pace [T1 = {t1_pace}/km, T2 = {t2_pace}/km], HR zone, RPE, distance/duration)
- **Cooldown** (easy jog, HR zone, distance/time)
- **Progression knob** (how to scale in later weeks — e.g., add reps, extend interval length, tighten rest)

**Rules:**

- **CRITICAL: Long run MUST be on {long_run_day}** ({weekend_min}–{weekend_max} min, Z2). This is non-negotiable.
- Easy run ≤60 min, Z2, recovery emphasis
- Threshold/interval runs must reference both **pace zones (T1, T2)** and **HR zones** as dials
- Where distance and time could be used, provide both (e.g., "6x1km at T1, ~{t1_pace}/km pace, HR Z3–4, 3 min jog rest")

**Output convention:**

- Present as a **list of {runs} running sessions** (not the whole week)
- Label them clearly by session type: *Run Quality 1 (Threshold Intervals)*, *Run Quality 2 (Progression Run)*, *Endurance Run (Long Z2)*, *Endurance Run (Easy Z2)*"""

        context = f"{global_context}\n\n---\n\n{week_skeleton}"
        return await self.generate(prompt, context=context)
