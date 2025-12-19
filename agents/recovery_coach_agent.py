"""
Recovery Coach Agent - Aerobic recovery and base building specialist.
Designs low-intensity recovery sessions.
"""
from .base_agent import BaseAgent


class RecoveryCoachAgent(BaseAgent):
    """
    Recovery Coach Agent designs aerobic recovery sessions.

    Responsibilities:
    - Low-intensity aerobic work (Z2 bike/erg)
    - Recovery between high-intensity sessions
    - Movement quality and technique work
    - Breathing and mobility protocols
    - Non-running cardiovascular stimulus
    """

    def get_agent_name(self) -> str:
        return "Recovery Coach Agent"

    def get_system_prompt(self) -> str:
        return """You are an expert recovery and aerobic base building coach specializing in hybrid athlete training.

**Your Expertise:**
- Aerobic base development
- Active recovery protocols
- Low-intensity cardiovascular training
- Movement quality and breathing mechanics
- Mobility and tissue quality
- Recovery modalities (bike, erg, swimming)
- Parasympathetic nervous system activation
- Training load management

**Your Role:**
You design recovery and aerobic engine sessions that support hard training. Your sessions must:
- Build aerobic base without running stress
- Promote recovery between high-intensity sessions
- Maintain cardiovascular training stimulus
- Improve movement quality and technique
- Support parasympathetic recovery

**Key Principles:**
- Use non-impact modalities (bike, SkiErg, rower) to reduce running load
- Target Zone 2 heart rate (70-80% HRmax)
- Sessions 30-50 minutes of steady work
- Include technique cues for efficiency
- Emphasize breathing mechanics and rhythm
- Provide mobility and stretching protocols
- Design sessions that feel restorative, not draining

**Your Approach:**
- Be specific with HR targets and perceived effort
- Include technique and form cues
- Provide warm-up and cooldown structure
- Explain HYROX transfer (aerobic base supports everything)
- Design progression strategies (extend duration, add tempo surges)
- Think about cumulative fatigue management

You create recovery sessions that build the aerobic engine while promoting adaptation and freshness."""

    async def design_recovery_session(
        self,
        global_context: str,
        week_skeleton: str
    ) -> str:
        """
        Design the aerobic recovery session for Week 1.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week 1 skeleton from Planning Agent

        Returns:
            Detailed aerobic recovery session design
        """
        prompt = """Design the Aerobic Engine / Recovery session for Week 1 based on the skeleton plan.

**Objectives:**

- Build aerobic base without running stress
- Promote recovery between high-intensity sessions
- Maintain movement quality and cardiovascular training stimulus

**Structure required in output:**

- **Purpose** (why low-intensity bike/erg work supports HYROX training).
- **Warm-up** (5–10 min ramp-up).
- **Main work** (30–50 min steady Z2 on bike or erg; technique cues; HR targets).
- **Cooldown** (mobility, stretch, breathwork).
- **Substitutions** (alternative modalities if needed).
- **HYROX Transfer** (how this supports race performance).
- **Progression knob** (extend duration, add short tempo surges in later weeks).

**Output convention:**

- Present as **1 complete Aerobic Engine/Recovery session** with full detail.
- Label clearly: *Aerobic Engine / Recovery Session – Week 1*.

Design a session that builds aerobic base while promoting recovery and freshness."""

        context = f"{global_context}\n\n---\n\n{week_skeleton}"
        return await self.generate(prompt, context=context)
