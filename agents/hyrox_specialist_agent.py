"""
HYROX Specialist Agent - HYROX combo/brick session specialist.
Designs race-specific sessions combining running and stations.
"""
from .base_agent import BaseAgent


class HYROXSpecialistAgent(BaseAgent):
    """
    HYROX Specialist Agent designs HYROX-specific combo/brick sessions.

    Responsibilities:
    - HYROX combo sessions (running + stations)
    - Brick workouts simulating race conditions
    - Lactate tolerance and clearance training
    - Station transition practice
    - Compromised running under fatigue
    """

    def get_agent_name(self) -> str:
        return "HYROX Specialist Agent"

    def get_system_prompt(self) -> str:
        return """You are an elite HYROX coach specializing in race-specific preparation and hybrid training.

**Your Expertise:**
- HYROX race demands and pacing strategies
- Compromised running (running while fatigued from stations)
- HYROX station technique and efficiency
- Lactate tolerance and clearance under fatigue
- Brick workouts (run + station combinations)
- Transition practice and economy
- Zone 4-5 intensity management
- Mental toughness and race simulation

**Your Role:**
You design HYROX combo/brick sessions that replicate race conditions. Your sessions must:
- Simulate HYROX race demands (running + stations under fatigue)
- Train lactate tolerance and clearance
- Practice station transitions and pacing
- Build mental resilience for high-intensity effort
- Operate primarily in Zone 4-5 with strategic recovery

**Key Principles:**
- Always combine running with HYROX stations (sled push/pull, SkiErg, row, burpees, wall balls, lunges, sandbag, farmers carry)
- Target total work time 45-60 minutes
- Simulate cumulative fatigue: shorter runs + higher station volume early, longer runs + lower station volume later
- Keep intensity high (Z4-5) but recoverable - don't redline early
- Practice transitions and station efficiency
- Provide substitutions for running load management (bike/erg alternatives)

**Your Approach:**
- Be specific with distances, reps, paces, HR targets
- Include at least 2 HYROX stations per block
- Design 2-3 blocks that progressively build fatigue
- Provide pacing guidance for compromised running
- Include technique cues for stations
- Think about race-specific transfer and simulation

You create HYROX sessions that prepare athletes for the unique demands of hybrid racing."""

    async def design_hyrox_session(
        self,
        global_context: str,
        week_skeleton: str
    ) -> str:
        """
        Design the HYROX combo/brick session for Week 1.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week 1 skeleton from Planning Agent

        Returns:
            Detailed HYROX combo/brick session design
        """
        prompt = """Design the HYROX Combo / Brick session for Week 1 based on the skeleton plan.

**Objectives:**

- Replicate HYROX race demands (compromised running, station transitions, Zone 4–5 intensity).
- Train lactate tolerance and clearance while fatigued.
- Practice pacing, breathing, and station efficiency under pressure.

**Structure required in output:**

For the HYROX Combo / Brick session, include:

- **Purpose** (link to specific HYROX race demands).
- **Warm-up** (run prep, machine primer, dynamic mobility).
- **Main Blocks** (2–3 blocks combining running intervals with HYROX stations; examples: Run → Sled Push/Pull, Run → Burpee Broad Jumps, Run → Wall Balls). Explicit distances, reps, paces, heart rate targets (Zone 4–5), RPE guidance, and rest.
- **Cooldown** (HR drop, mobility, walking, breathing drills).
- **Progression knob** (increase run distance per station, reduce rest, add rounds, or increase station volume).

**Rules:**

- Always include **running + at least 2 HYROX stations per block**.
- Target total work time **45–60 minutes**.
- Sessions should simulate cumulative fatigue: **shorter runs, higher station volume** in early blocks; **longer runs, reduced volume** in later blocks.
- Keep intensity high (Zone 4–5) but with recoverable sets — do not "redline" early.
- Provide substitutions if running load needs managing (swap to bike/erg).

**Output convention:**

- Deliver as a **single HYROX Combo / Brick session** (for Week 1).
- Label clearly: *HYROX Combo / Brick Session – Week 1*.

Design a session that simulates race demands and builds HYROX-specific fitness."""

        context = f"{global_context}\n\n---\n\n{week_skeleton}"
        return await self.generate(prompt, context=context)
