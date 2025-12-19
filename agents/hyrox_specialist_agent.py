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
        week_skeleton: str,
        hyrox_weights=None,
        block_objectives=None
    ) -> str:
        """
        Design the HYROX combo/brick session with phase-specific programming.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week skeleton from Planning Agent
            hyrox_weights: Official HYROX race weights (HyroxWeights object)
            block_objectives: Training block objectives (BlockObjectives object)

        Returns:
            Detailed HYROX combo/brick session design
        """
        # Import here to avoid circular dependency
        from models import HyroxWeights, BlockObjectives

        # Use default Men's weights if not provided
        if hyrox_weights is None:
            hyrox_weights = HyroxWeights.for_division("Men")

        # Determine focus instructions based on phase
        if block_objectives and block_objectives.primary_goal:
            phase = block_objectives.primary_goal.upper()
        else:
            phase = "BUILD"  # Default to BUILD if not specified

        if phase == "BASE":
            focus_instructions = (
                "Focus: BASE STATION STRENGTH & ACTIVE RECOVERY.\n"
                "- Primary purpose is to build base strength and skill on key HYROX stations WITHOUT compromising aerobic development.\n"
                "- NO compromised running in BASE phase. Aerobic base development must stay clean with dedicated Zone 2 runs.\n"
                "- Station loads may be overloaded 5–15% above race weight for one or two focus stations, with moderate volumes (25–50% race volume).\n"
                "- Between station sets: Use active recovery cardio (bike, SkiErg, or RowErg) at Z1-Z2 for 1:30-2:30 to practice "
                "lactate clearance and HR management, followed by 1:00 standing rest. OR use complete rest (2:30-3:00) if athlete is new to HYROX.\n"
                "- Focus: Station technique, strength endurance, lactate clearance skill (not race-specific running fatigue).\n"
                "- Example session: 5 rounds of Sled Push 25m + Sled Pull 25m, then 2:00 easy bike (Z2, breathing focus) + 1:00 standing rest.\n"
                "- Progression: Start with complete rest in weeks 1-2, add active recovery cardio in weeks 3-4.\n"
            )
        elif phase == "BUILD":
            focus_instructions = (
                "Focus: THRESHOLD INTEGRATION.\n"
                "- Purpose is to connect your clean threshold work to HYROX specificity: running strongly at or just below T1 after hard stations.\n"
                "- Use 400–800 m run segments at around T1 pace (occasionally T1+10 sec/km if fatigue builds).\n"
                "- Total compromised running should be ~3–5 km.\n"
                "- Station loads are typically at race weight; mild overload (5–10%) is allowed for one key station.\n"
            )
        elif phase == "PEAK":
            focus_instructions = (
                "Focus: RACE SIMULATION.\n"
                "- Purpose is to rehearse race-day demands with mini HYROX blocks.\n"
                "- Use 600–1000 m run segments between stations, mostly at T1 pace with occasional segments nudging toward T2 "
                "(e.g. 5-10s/km faster than T1 pace).\n"
                "- Total compromised running should be ~4–6 km.\n"
                "- Station volumes should be 70–100% of race volume for selected stations; at most one station may be slightly overloaded.\n"
            )
        elif phase == "TAPER":
            focus_instructions = (
                "Focus: SHARPNESS & CONFIDENCE.\n"
                "- Purpose is to remind the body of HYROX patterns without creating heavy fatigue.\n"
                "- Use 400–800 m run segments with most running at T1+20 to T1+45 sec/km, and only a few short bouts at T1 pace.\n"
                "- Total compromised running should be ~2–3 km.\n"
                "- Station volumes should be 25–50% of race volume at race weight, with no overload.\n"
            )
        else:  # TRANSITION
            focus_instructions = (
                "Focus: SKIP THIS SESSION ENTIRELY.\n\n"
                "**TRANSITION PHASE: HYROX combo/brick sessions should NOT be included.**\n\n"
                "This is a RECOVERY phase. The athlete is recovering from a competition or hard training block.\n\n"
                "**DO NOT prescribe:**\n"
                "- Any HYROX combo sessions\n"
                "- Any brick sessions\n"
                "- Any compromised running\n"
                "- Any race-weight station work\n"
                "- Any Zone 3+ work\n\n"
                "**Instead, if the skeleton from Layer 1 mistakenly includes a HYROX combo session, REPLACE it with:**\n"
                "- Option 1: Complete rest day (PREFERRED)\n"
                "- Option 2: 30-40 min easy aerobic work (bike/erg/swim at Zone 1-2, HR 60-75% max, RPE 3-4)\n"
                "- Option 3: Gentle mobility/yoga session (30-40 min, no strength work)\n\n"
                "**CRITICAL:** Do NOT provide a traditional HYROX combo workout. State clearly: 'SKIP - TRANSITION phase focuses on recovery. Use a rest day or replace with 30-40 min easy bike/erg at Z1-2 instead.'\n"
            )

        prompt = f"""Using Layer 0 rules, the current TrainingPhase, and the weekly skeleton from Layer 1, expand only the HYROX Combo / Brick session into a fully detailed workout.

You are designing a single HYROX combo / brick session that trains compromised running and HYROX station execution.

**Official HYROX Race Specifications:**

- Sled Push: {hyrox_weights.sled_push_kg}kg
- Sled Pull: {hyrox_weights.sled_pull_kg}kg
- Farmers Carry: {hyrox_weights.farmers_carry_kg[0]}kg per hand (2×{hyrox_weights.farmers_carry_kg[0]}kg total)
- Sandbag Lunges: {hyrox_weights.sandbag_kg}kg
- Wall Balls: {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m target

**100% Race Volume Reference:**

- Sled Push: 50m
- Sled Pull: 50m
- Wall Balls: 100 reps
- Farmers Carry: 200m
- Sandbag Lunges: 100m
- SkiErg: 1000m
- RowErg: 1000m

**Phase-specific focus:**

{focus_instructions}

**Intensity guidance using T1 and T2:**

- T1 pace is the primary reference for strong but sustainable work.
- When the athlete should run slower than T1, express this as T1+seconds per km, for example:
  - "Easy steady run at around T1+30s/km"
  - "Controlled recovery run at around T1+45s/km"
- When the athlete should push harder than T1 but not full T2, use:
  - "5-10s/km faster than T1 pace" (e.g., T1-5 to T1-10s/km)
  - Or describe as "strong tempo, between T1 and T2 pace"
- Avoid prescribing vague zones alone; always anchor runs to T1/T2 or T1±seconds per km.

**Valid combo / brick patterns (choose ONE primary pattern for this session):**

1. **Station → Run → Rest**
   - One or two HYROX stations performed first, followed by a run segment, then planned rest.
   - Example: Sled Push + Sled Pull → 600 m run @ around T1 pace → 90 s rest.

2. **Run → Station → Run → Rest**
   - Run into a station, then run out of it, then rest.
   - Best for BUILD and PEAK when you want both station output and compromised running.
   - Example: 400 m @ T1 pace → 25 m Sled Push → 400–600 m @ T1+10s/km → 2:00 rest.

3. **Station A + Station B → Run → Rest**
   - Two related stations chained together before the run (e.g. sled + lunges, row + farmers).
   - Emphasises local muscular fatigue before the compromised run.

4. **Run → Station A + Station B → Run → Rest**
   - A longer, more advanced pattern used primarily in PEAK blocks.
   - Run into a two-station block, then finish with a compromised run before resting.

5. **Run → Station → Run → Station → Wall Balls → Rest**
   - Start with a run, hit a HYROX station, then a compromised run, then another station, and always finish the round with wall balls as the final station.
   - Best for BUILD and PEAK phases when you want repeated exposure to running into and out of fatigue, with the classic HYROX wall ball finish each round.
   - Wall ball volumes by phase:
     * BASE: 20-30 wall balls per round
     * BUILD: 30-50 wall balls per round
     * PEAK: 50-100 wall balls per round (race volume)
     * TAPER: 15-25 wall balls per round

6. **Erg → Station → Run → Station → Run → Wall Balls → Rest**
   - Begin on an erg (SkiErg or RowErg), move into a station, then a compromised run, another station, another compromised run, and always finish the round with wall balls.
   - This is an advanced race-feel pattern. **Use this pattern ONLY in PEAK phase or late BUILD phase (weeks 3-4).** This is the most advanced pattern and requires high fitness.
   - Wall ball volumes same as pattern 5 above.

**Pattern selection by phase:**

- BASE: DO NOT use the standard patterns above (they all include running). Instead, use station-only patterns:
  * Station A + Station B → Active Recovery Cardio (bike/erg Z1-Z2) + Rest
  * Station Block (1-3 stations) → Active Recovery Cardio + Rest
  * Example: Sled Push + Sled Pull → 2:00 easy bike + 1:00 standing rest
- BUILD: Use patterns 2-5 (adding complexity and race patterns)
- PEAK: Use patterns 4-6 (full race simulation)
- TAPER: Use patterns 1-2 (keep it simple and clean)

For BUILD, PEAK, and TAPER patterns (with running):
- At least half of all run segments in the main set must come **after** station work (compromised running).
- Do not design the entire workout as Run → Station only; the key adaptation is running after stations.
- When using patterns 5 or 6, ensure wall balls always appear as the final station in each round.

**Run distance and volume guidelines:**

- BASE:
  - NO running in brick/combo sessions. Station work only with active recovery cardio (bike/erg) or complete rest between sets.
  - This preserves aerobic base development and allows clean Zone 2 running in dedicated run sessions.
  - Between station sets: 1:30-2:30 easy bike/SkiErg/RowErg (Z1-Z2) + 1:00 standing rest, OR 2:30-3:00 complete rest.

- BUILD:
  - Use 400–800 m run segments.
  - Total compromised running ≈ 3–5 km.
  - Most runs around T1 pace (occasionally T1+10s/km if fatigue accumulates).

- PEAK:
  - Use 600–1000 m run segments.
  - Total compromised running ≈ 4–6 km.
  - Most runs around T1 pace, with some segments 5-10s/km faster than T1 pace.

- TAPER:
  - Use 400–800 m run segments.
  - Total compromised running ≈ 2–3 km.
  - Most runs at T1+20 to T1+45s/km, with only a few short segments at T1 pace.

**Rest period guidelines:**

- BASE: 1:30-2:30 active recovery cardio (bike/SkiErg/RowErg at Z1-Z2) + 1:00 standing rest, OR 2:30-3:00 complete rest (use complete rest for beginners or weeks 1-2, add active recovery weeks 3-4)
- BUILD: 90s-2:00 (partial recovery, building work capacity)
- PEAK: 60s-90s (race-like rest, high density)
- TAPER: 2:00-3:00 (keep it fresh)

**Station load and volume guidance:**

- BASE:
  - One or two focus stations may be overloaded 5–15% above race weight.
  - Volumes are moderate (around 25–50% of race volume per focus station).
- BUILD:
  - Most stations at race weight.
  - One key station may be mildly overloaded (5–10% heavier) with 50–80% of race volume.
- PEAK:
  - Selected stations at 70–100% of race volume.
  - At most one station may be slightly overloaded in a given session.
- TAPER:
  - Stations at race weight, 25–50% of race volume.
  - No overload.

**Deload week (if applicable):**

- Reduce compromised running volume by ~40% (e.g., 2km instead of 3-5km)
- Use patterns 1-2 only (simple structure)
- Station volumes at 30-40% of race volume
- Rest periods extended to 2:30-3:00
- Keep movement quality high, end feeling fresh

Across weeks in a block, rotate which stations are the focus so the athlete practices running after:
- Sleds (push/pull)
- Sandbag lunges
- Wall balls
- SkiErg
- RowErg
- Farmers carries

**Expected total session duration (including warmup/cooldown):**

- BASE: 45-60 min
- BUILD: 50-70 min
- PEAK: 60-80 min
- TAPER: 30-45 min

**Warmup structure:**

- 5-10 min easy running (around T1+60s/km or easier)
- Dynamic mobility (focus on hips, shoulders, thoracic spine)
- 1-2 rehearsals of primary stations at 50% effort/load
- 1-2 short run strides (100m at around T1 pace)

**Cooldown structure:**

- 5-10 min easy jog/walk (around T1+60s/km or slower)
- Light stretching for hips, quads, shoulders, lats (stations are demanding on these muscle groups)

**Design rules:**

- Choose ONE primary pattern from the list above and use it consistently in the main set.
- Design 1–3 main blocks depending on phase (fewer, longer blocks for PEAK; more, shorter blocks for BASE and TAPER).
- Ensure the session is one of the harder sessions of the week, but still recoverable within 48–72 hours.
- Always finish with a clear cooldown and an explanation of how to progress this session in the next block (e.g. adding a round, slightly increasing a run distance, or trimming rest).

**Output format:**

Return the full session in this structure:

1. **Session title**
2. **Purpose** (1–3 sentences, referencing phase and intended adaptation)
3. **Warm-up** (with sets, durations, and intensities relative to T1/T2)
4. **Main set** (clearly structured rounds/blocks using one of the valid patterns)
5. **Cooldown**
6. **Progression notes** (how to make this harder/easier in future blocks)

Keep the language concise and coaching-friendly."""

        context = f"{global_context}\n\n---\n\n{week_skeleton}"
        return await self.generate(prompt, context=context)
