"""
Strength Coach Agent - Strength and strength endurance specialist.
Designs max strength and strength endurance sessions.
"""
from .base_agent import BaseAgent


class StrengthCoachAgent(BaseAgent):
    """
    Strength Coach Agent designs strength and strength endurance sessions.

    Responsibilities:
    - Max strength sessions (compound lifts, low reps, high load)
    - Strength endurance sessions (circuits, EMOMs, cardio integration)
    - Progressive overload strategies
    - HYROX-specific strength transfer
    - Injury-aware exercise selection and modifications
    """

    def get_agent_name(self) -> str:
        return "Strength Coach Agent"

    def get_system_prompt(self) -> str:
        return """You are an elite strength and conditioning coach specializing in HYROX and hybrid athlete training.

**Your Expertise:**
- Maximal strength development (compound lifts, periodization)
- Strength endurance and work capacity
- HYROX-specific strength stations (sleds, carries, wall balls, lunges)
- Circuit training and metabolic conditioning
- Exercise selection for hybrid athletes
- Injury management and movement substitutions
- Progressive overload strategies

**Your Role:**
You design both max strength and strength endurance sessions. Your sessions must:
- Build absolute strength that transfers to HYROX performance
- Develop strength endurance for sustained effort under fatigue
- Integrate cardio modalities to simulate race demands
- Manage fatigue and recovery appropriately
- Provide clear load prescriptions (%1RM, RPE, or explicit weights)

**Key Principles:**

**For Max Strength:**
- Focus on compound lifts (squat, deadlift, bench/press, pull-ups)
- Low reps (3-6 range), high quality, adequate rest
- Build economy, resilience, and neural efficiency
- Sessions ≤75 min
- No overlap with hard running on same day

**For Strength Endurance:**
- Build work capacity under fatigue
- Pair strength movements with cardio intervals (run, ski, row, bike)
- Simulate HYROX demands (sleds, carries, wall balls, burpees, lunges)
- HR in upper Z2 → mid Z4
- Sessions 60-75 min
- ALWAYS include cardio modalities within the session

**Your Approach:**
- Be specific with sets, reps, loads, rest periods
- Provide clear warm-up and mobility protocols
- Include accessory work for weak links
- Design progressive overload strategies
- Provide exercise substitutions for injuries
- Think about cumulative fatigue and recovery

You create strength sessions that build the power, endurance, and resilience needed for HYROX excellence."""

    async def design_strength_sessions(
        self,
        global_context: str,
        week_skeleton: str
    ) -> str:
        """
        Design max strength sessions for Week 1.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week 1 skeleton from Planning Agent

        Returns:
            Detailed max strength session designs
        """
        prompt = """Design all Max Strength sessions for Week 1 based on the skeleton plan.

**Objectives:**

- Build absolute strength in compound lifts → improved economy, resilience, and transfer into HYROX strength endurance.
- Focus on low rep, high quality lifts.
- Keep sessions ≤75 min.
- No overlapping same-day fatigue with hard run sessions.

**Structure required in output:**

For each strength session, include:

- **Purpose** (why it's in the program)
- **Warm-up** (mobility, activation, ramp-up sets)
- **Main lifts** (2–3 compound lifts: squat, deadlift, bench/press, pull-up variants). Explicit sets × reps × %1RM or RPE.
- **Accessory work** (1–2 short blocks targeting weak links or HYROX transfer — e.g., core stability, unilateral strength, grip).
- **Cooldown** (mobility, breathing reset, stretch priority areas).
- **Progression knob** (e.g., increase load by 2.5–5%, add 1 set, tighten rest).

**Rules:**

- Use rep schemes in the **3–6 rep** range for compounds.
- Accessories may include unilateral lifts (lunges, RDLs), core, or posterior chain balance.
- No more than 4 total main compound lifts per session.
- Keep rest long (2–3 min for heavy compounds, 60–90s for accessories).

**Output convention:**

- Present as a **list of 1–2 Max Strength sessions** (as per Week 1 skeleton).
- Label them clearly: *Strength Session 1 (Lower Body Max)*, *Strength Session 2 (Upper/Full Body Max)*.

Design strength sessions that build the absolute strength foundation for HYROX performance."""

        context = f"{global_context}\n\n---\n\n{week_skeleton}"
        return await self.generate(prompt, context=context)

    async def design_strength_endurance_sessions(
        self,
        global_context: str,
        week_skeleton: str
    ) -> str:
        """
        Design strength endurance sessions for Week 1.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week 1 skeleton from Planning Agent

        Returns:
            Detailed strength endurance session designs
        """
        prompt = """Design all Strength Endurance sessions for Week 1 based on the skeleton plan.

**Objectives:**

- Build the ability to sustain submaximal strength under fatigue.
- Improve work capacity and efficiency in HYROX-specific stations (sleds, carries, wall balls, lunges, burpees).
- Force adaptation by pairing **strength movements with cardio intervals** to simulate race demands.
- Time cap: 60–75 min.

**Structure required in output:**

For each strength endurance session, include:

- **Purpose** (clear link to HYROX transfer).
- **Warm-up** (mobility, activation, light machine work).
- **Main Blocks** (2–3 blocks using EMOMs, AMRAPs, circuits, or interval pairings of cardio + functional strength). Must include at least one machine (run, ski, row, echo/bike) per block. Explicit reps/sets/duration, intensity targets (HR zone, RPE, or pace).
- **Cooldown** (walk, flush, mobility, breathing).
- **Progression knob** (volume, density, load, or machine interval length).

**Rules:**

- Keep heart rate between **upper Zone 2 → mid Zone 4**, depending on block.
- Alternate knee-dominant vs. hip-dominant strength movements to manage fatigue.
- Each block should last **8–20 minutes**.
- Sessions should balance load: one more *sled/carry/burpee focused*; one more *wall ball/lunge/erg focused*.
- Explicit substitutions if running volume needs capping (swap to bike/erg).

**Output convention:**

- Present as a **list of 2 Strength Endurance sessions** (as per Week 1 skeleton).
- Label clearly: *Strength Endurance Session 1 (Erg + Functional Strength)*, *Strength Endurance Session 2 (Run + HYROX Circuit)*.

Design strength endurance sessions that build work capacity and HYROX-specific resilience."""

        context = f"{global_context}\n\n---\n\n{week_skeleton}"
        return await self.generate(prompt, context=context)

    async def design_all_strength_sessions(
        self,
        global_context: str,
        week_skeleton: str
    ) -> tuple[str, str]:
        """
        Design both max strength and strength endurance sessions.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week 1 skeleton from Planning Agent

        Returns:
            Tuple of (max_strength_sessions, strength_endurance_sessions)
        """
        # Design max strength sessions
        max_strength = await self.design_strength_sessions(global_context, week_skeleton)

        # Design strength endurance sessions
        strength_endurance = await self.design_strength_endurance_sessions(global_context, week_skeleton)

        return max_strength, strength_endurance
