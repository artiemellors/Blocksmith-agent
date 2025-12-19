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
        week_skeleton: str,
        week_number: int = 1,
        block_duration_weeks: int = 4
    ) -> str:
        """
        Design max strength sessions with sophisticated periodization.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week skeleton from Planning Agent
            week_number: Current week number (default 1)
            block_duration_weeks: Total block duration (default 4)

        Returns:
            Detailed max strength session designs
        """
        # Determine which phase based on week number and block duration
        # Midpoint transition: first half = Phase 1 (6-8 reps), second half = Phase 2 (4-5 reps)
        midpoint = block_duration_weeks / 2

        if week_number <= midpoint:
            # Phase 1: Higher volume (6-8 reps)
            rep_instructions = """**Phase 1: Volume Accumulation (Weeks 1-{mid})** ← YOU ARE HERE

You are in the HIGHER REP RANGE phase (6-8 reps).

**Rep Range**: 4 sets × 6-8 reps
**Rep Targets**: 8-7-7-6 or 8-8-7-7
**Load**: ~70-75% estimated 1RM
**RPE**: 7-8 on most sets
**Rest**: 2 min (lower body), 90s (upper body)

**Focus**: Build work capacity, reinforce technique, accumulate training volume with moderate loads.""".format(mid=int(midpoint))
        else:
            # Phase 2: Higher intensity (4-5 reps)
            rep_instructions = """**Phase 2: Intensity Peak (Weeks {start}-{end})** ← YOU ARE HERE

You are in the LOWER REP RANGE phase (4-5 reps).

**Rep Range**: 4 sets × 4-5 reps
**Rep Targets**: 5-5-4-4 or 5-5-5-4
**Load**: ~80-85% estimated 1RM
**RPE**: 8-9 on most sets
**Rest**: 2 min (lower body), 90s (upper body)

**Focus**: Peak strength with heavier loads, maintain volume through increased weight.""".format(
                start=int(midpoint)+1,
                end=block_duration_weeks
            )

        prompt = f"""Design all Max Strength sessions for Week {week_number} based on the skeleton plan.

**Objectives:**

**PHASE-SPECIFIC REP RANGE MANDATE:**

{rep_instructions}

**General Objectives:**

- Build absolute strength in HYROX-relevant compound lifts → improved running economy, station performance, injury resilience
- Use periodized rep ranges: higher volume early (6-8 reps), higher intensity later (4-5 reps)
- Keep sessions 75-85 minutes total
- Schedule at least 24 hours away from threshold/interval running sessions

**Session Structure:**

1. **Warm-up (15 min)**
   - General: 5 min cardio at easy pace (row/ski/bike) HR 120-130
   - Mobility: 5 min (hip 90/90 stretch 60s each side, spiderman with reach 5/side, goblet squat hold 60s, band pull-aparts 20 reps, dead bugs 10/side)
   - Specific: 5 min ramp sets for first compound (empty bar × 10, 40% × 5, 60% × 3, 75% × 1, rest 60-90s between)

2. **Compound Lifts (50 min total)**
   - Exactly 3 lifts: ONE from each category below
   - Time allocation: 20 min (hip-dominant) + 18 min (knee-dominant) + 12 min (upper body)

3. **Accessory Circuit (12-15 min)**
   - 4 exercises, 3-4 rounds, 60-90s rest between rounds

4. **Cooldown (5 min)**
   - Hip flexor stretch 90s/side, hamstring stretch 90s/side, thoracic rotation 10/side
   - 2 min diaphragmatic breathing (4s in, 6s out)

**COMPOUND LIFT SELECTION RULES:**

**Rule 1: Pick EXACTLY ONE from each category (total = 3 lifts)**

**Category A (Hip-Dominant):**
- Trap Bar Deadlift (PREFERRED - best HYROX transfer)
- Conventional Deadlift
- Romanian Deadlift (RDL)

**Category B (Knee-Dominant):**
- Front Squat (PREFERRED - best HYROX transfer)
- Goblet Squat (heavy DB/KB)
- High Bar Back Squat
- Avoid: Low bar back squat (poor HYROX transfer)

**Category C (Upper Body):**
- Push Press (PREFERRED - best wall ball transfer)
- Weighted Chin-Ups (choose if pulling weaker than pushing)
- Incline Bench Press (30-45°)
- Avoid: Flat bench press unless necessary

**Rule 2: Order by CNS demand (highest to lowest)**
1st: Category A (hip-dominant)
2nd: Category B (knee-dominant)
3rd: Category C (upper body)

**PERIODIZED PROGRESSION SCHEME (applies to ALL 3 compound lifts):**

Use 4 sets with periodized rep ranges that shift from higher volume to higher intensity as the training block progresses.

**PERIODIZATION APPROACH:**

**Phase 1: Early Block Weeks (Higher Rep Range - Volume Phase)**
- Timing: Roughly first half of the training block
- Rep range: 4 sets × 6-8 reps
- Rep targets within session: 8-7-7-6 or 8-8-7-7
- Load: Approximately 70-75% estimated 1RM
- Rest: 2 min between sets (lower body), 90s (upper body)
- Target RPE: 7-8 on most sets
- Focus: Build work capacity, reinforce technique, accumulate training volume

**Phase 2: Later Block Weeks (Lower Rep Range - Intensity Phase)**
- Timing: Roughly second half of the training block
- Rep range: 4 sets × 4-5 reps
- Rep targets within session: 5-5-4-4 or 5-5-5-4
- Load: Approximately 80-85% estimated 1RM
- Rest: 2 min between sets (lower body), 90s (upper body)
- Target RPE: 8-9 on most sets
- Focus: Peak strength, higher intensity loads, maintain volume through heavier weight

**Transition Timing (Use These Guidelines):**

The transition from higher to lower rep ranges should occur roughly at the midpoint of the training block:

- 4-week block: Weeks 1-2 use 6-8 reps, Week 3 use 4-5 reps, Week 4 deload
- 6-week block: Weeks 1-3 use 6-8 reps, Weeks 4-5 use 4-5 reps, Week 6 deload
- 8-week block: Weeks 1-4 use 6-8 reps, Weeks 5-7 use 4-5 reps, Week 8 deload
- 12-week block: Weeks 1-6 use 6-8 reps, Weeks 7-11 use 4-5 reps, Week 12 deload

**Rep Targets Within Each Session:**

The rep targets decrease across sets due to natural fatigue accumulation. With only 90-120s rest, maintaining max reps across all sets isn't realistic.

For 6-8 rep range sessions (Phase 1):
- Set 1: Target 8 reps (you're fresh)
- Set 2: Target 7-8 reps (slight fatigue)
- Set 3: Target 7 reps (more fatigue)
- Set 4: Target 6-7 reps (accumulated fatigue)

For 4-5 rep range sessions (Phase 2):
- Set 1: Target 5 reps (you're fresh)
- Set 2: Target 5 reps (slight fatigue)
- Set 3: Target 4-5 reps (more fatigue)
- Set 4: Target 4 reps (accumulated fatigue)

**Load Selection Guidelines:**

For 6-8 rep range (Phase 1):
- Choose approximately 70-75% estimated 1RM
- Starting a new load: Should achieve roughly 8-7-7-6 or 8-8-7-6 reps across 4 sets
- If you hit 8-8-8-8 easily on first session, load is too light
- If you hit 6-6-5-5 on first session, load is too heavy
- Target RPE 7-8 on most sets

For 4-5 rep range (Phase 2):
- Choose approximately 80-85% estimated 1RM
- Starting a new load: Should achieve roughly 5-5-4-4 or 5-4-4-4 reps across 4 sets
- If you hit 5-5-5-5 comfortably on first session, load is too light
- If you hit 4-3-3-3 on first session, load is too heavy
- Target RPE 8-9 on most sets (this is the higher intensity phase)

**Rest Intervals (same for both phases):**
- Lower body compounds (Categories A & B): 2 min between sets
- Upper body compound (Category C): 90s between sets

**PROGRESSION PRINCIPLES:**

**During 6-8 Rep Range Sessions (Phase 1):**

Building reps at same load:
- Start each new load conservatively (should hit 8-7-7-6 or 8-8-7-6)
- Keep load constant for 2-3 sessions
- Each session, try to add 1-3 total reps across all 4 sets
- Example progression: Session 1: 8-7-7-6 (28 reps) → Session 2: 8-8-7-7 (30 reps) → Session 3: 8-8-8-7 (31 reps)

Progression trigger (when to add weight):
- When you achieve: Set 1: 8 reps, Set 2: 8 reps, Set 3: 8 reps
- Then next session add: Lower body +5kg, Upper body +2.5kg
- After adding weight, reps drop back (e.g., to 8-7-7-6). This is normal and expected.

**During 4-5 Rep Range Sessions (Phase 2):**

Building reps at same load:
- Start each new load conservatively (should hit 5-5-4-4 or 5-4-4-4)
- Keep load constant for 2-3 sessions
- Each session, try to add 1-2 total reps across all 4 sets
- Example progression: Session 1: 5-5-4-4 (18 reps) → Session 2: 5-5-5-4 (19 reps) → Session 3: 5-5-5-5 (20 reps)

Progression trigger (when to add weight):
- When you achieve: Set 1: 5 reps, Set 2: 5 reps, Set 3: 5 reps
- Then next session add: Lower body +5kg, Upper body +2.5kg
- After adding weight, reps may drop back (e.g., to 5-4-4-4). This is normal and expected.

**Transitioning Between Phases:**

When moving from Phase 1 (6-8 reps) to Phase 2 (4-5 reps):
- Increase load by approximately 5-10% for lower body or 2.5-5kg for upper body
- This accounts for the shift from 70-75% loads (Phase 1) to 80-85% loads (Phase 2)
- First session at lower rep range should feel manageable (hit 5-5-4-4 or 5-4-4-4)
- Then build reps from there using normal progression principles

Example transition:
- End of Phase 1: Trap Bar Deadlift 140kg achieving 8-8-8-7
- Start of Phase 2: Trap Bar Deadlift 150kg achieving 5-5-4-4
- Continue building: 150kg → 5-5-5-4 → 5-5-5-5 → 155kg → 5-5-4-4 (cycle repeats)

**Deload Sessions (when programmed in training block):**
- Reduce load to 65-70% of current working weight
- 4 sets × 8 reps (all sets should hit 8 comfortably)
- Target RPE 5-6, focus on movement quality and technique
- Use 8 reps regardless of whether you were in Phase 1 (6-8) or Phase 2 (4-5)
- After deload, return to the appropriate rep range for that point in the block

**Quality Standards (both phases):**
- Explosive concentric, controlled eccentric (2-3s lowering)
- Full range of motion on all reps
- 2-second pause at bottom of squats and bench variations
- Stop set if bar speed slows significantly or form breaks down
- It's okay to hit the low end of rep range on final sets

**ACCESSORY CIRCUIT (CRITICAL FOR BALANCED COVERAGE):**

Format: 4 exercises, 3-4 rounds, 60-90s rest between rounds

**IMPORTANT: Slots 1 and 3 must be OPPOSITE of Compound 3 for balanced upper body work**

**IF Compound 3 = PUSH-dominant (Push Press, Incline Bench, Bench Press, Strict OHP):**
Then BOTH Slot 1 and Slot 3 should be PULL exercises:

Slot 1 - Vertical Pull (pick one):
- Ring/TRX Rows: 12-15 reps @ RPE 7
- Weighted Chin-Up Negatives: 5-8 reps @ RPE 7-8 (3-5s eccentric)
- Lat Pulldown: 10-12 reps @ RPE 7
- Face Pulls: 15-20 reps @ RPE 6-7

Slot 3 - Horizontal Pull (pick one):
- Single-arm DB Row: 8-10 reps per side @ RPE 7-8
- Bent-over DB Rows: 10-12 reps @ RPE 7
- Chest-Supported Row: 10-12 reps @ RPE 7
- Inverted Rows: 10-15 reps @ RPE 7

Result: 1 push compound + 2 pull accessories = BALANCED upper body

**IF Compound 3 = PULL-dominant (Weighted Chin-Ups, Weighted Pull-Ups, Barbell Rows):**
Then BOTH Slot 1 and Slot 3 should be PUSH exercises:

Slot 1 - Horizontal Push/Chest Focus (pick one):
- Incline DB Press: 10-12 reps @ RPE 7 (30-45° angle)
- Flat DB Press: 10-12 reps @ RPE 7
- Weighted Dips: 8-12 reps @ RPE 7
- Push-ups: 15-20 reps @ RPE 7

Slot 3 - Vertical Push/Shoulder Focus (pick one):
- DB Shoulder Press: 10-12 reps @ RPE 7
- Landmine Press: 10-12 reps per side @ RPE 7
- Pike Push-ups: 10-15 reps @ RPE 7
- DB Pec Fly: 12-15 reps @ RPE 6-7

Result: 1 pull compound + 2 push accessories = BALANCED upper body

**Slot 2: Unilateral Lower Body (pick one, always the same regardless of Compound 3):**
- Bulgarian Split Squat: 8-10 reps per leg @ RPE 7-8
- Single-leg RDL: 8-10 reps per leg @ RPE 7
- Reverse Lunges: 10 reps per leg @ RPE 7 (can hold DBs)
- Step-ups: 8-10 reps per leg @ RPE 7 (on 20" box)

**Slot 4: Core/Anti-Rotation (pick one, always the same regardless of Compound 3):**
- Pallof Press: 10-12 reps per side @ RPE 7
- Weighted Plank Hold: 45-60s @ RPE 7
- Dead Bugs: 10-12 reps per side (controlled tempo)
- Russian Twists: 20 total reps with weight @ RPE 7
- Hanging Knee Raises: 10-15 reps @ RPE 7

**Circuit Execution:**
- "Walking pace" between exercises (control each rep, minimal rest <30s between exercises)
- No exercise should go to failure - leave 2-3 reps in reserve
- Rest 60-90s between complete rounds

**Round Progression:**
- Phase 1 (6-8 reps): Start with 3 rounds, build to 4 rounds over 2-3 sessions
- Phase 2 (4-5 reps): Maintain 3-4 rounds OR add 2.5-5kg to accessory loads
- Deload sessions: 2-3 rounds at same weight, focus on quality

**OUTPUT FORMAT:**

For each Max Strength session, provide:

1. **Session Header:**
   - Day scheduled (typically Tuesday or Wednesday)
   - Total duration (75-85 min)
   - Equipment needed
   - Placement note (e.g., "Schedule 24h+ away from threshold running")
   - Current phase note (e.g., "Phase 1: 6-8 rep range - volume accumulation")

2. **Complete Warm-up:**
   - All 3 phases with specific exercises and durations
   - Exact ramp set protocol for first compound lift

3. **All 3 Compound Lifts:**
   - Exercise name
   - Current phase rep range (either 6-8 or 4-5)
   - 4 sets with specific rep targets (e.g., "8-7-7-6" or "5-5-4-4")
   - Load recommendation based on estimated 1RM
   - RPE targets for each set
   - Rest intervals
   - One-sentence technical cue

4. **Complete Accessory Circuit:**
   - All 4 exercises with sets, reps, RPE
   - Clear note explaining which Compound 3 type was chosen (push vs pull) and how Slots 1 & 3 balance it
   - Circuit format and rest periods

5. **Cooldown:**
   - Specific stretches with durations
   - Breathing protocol

6. **Session Notes:**
   - Current phase explanation (Phase 1 volume or Phase 2 intensity)
   - Why these exercises were chosen (2-3 sentences)
   - Progression plan for next session (1-2 sentences explaining rep building)
   - If transitioning phases soon, note when transition will occur

**CRITICAL REMINDERS:**

DO:
- Identify which phase of the block this session falls in (early = 6-8 reps, later = 4-5 reps)
- Choose exactly 3 compound lifts (one from each category)
- Make Slots 1 & 3 OPPOSITE of Compound 3 (if push → both pull, if pull → both push)
- Use appropriate rep range for the phase (6-8 early, 4-5 later)
- Rest 2 min (lower), 90s (upper) between compound sets
- Build reps for 2-3 sessions before adding weight
- Prioritize HYROX-specific lifts (Trap Bar DL, Front Squat, Push Press)

DON'T:
- Use more than 3 compound lifts
- Use more than 4 accessory exercises
- Go to failure on accessories
- Schedule within 24h of hard running
- Mix rep ranges within a session (all 3 compounds use same phase)
- Skip the periodization (always use 6-8 early, 4-5 later)

**Why Periodized Rep Ranges for HYROX:**

Phase 1 (6-8 reps): Builds work capacity, technique mastery, and muscular endurance base. Higher volume prepares the body for the training block while managing fatigue with moderate loads.

Phase 2 (4-5 reps): Peaks strength and power output with heavier loads. This phase develops the raw strength that translates to faster sled times and explosive power for stations.

This periodization optimizes the balance between volume accumulation and intensity for athletes training 1x/week with 40-50km running volume.

Present sessions as: **Max Strength Session 1** or **Max Strength Session 2** (as per Week 1 skeleton)."""

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
        week_skeleton: str,
        week_number: int = 1,
        block_duration_weeks: int = 4
    ) -> tuple[str, str]:
        """
        Design both max strength and strength endurance sessions.

        Args:
            global_context: Global training context from Planning Agent
            week_skeleton: Week skeleton from Planning Agent
            week_number: Current week number (default 1)
            block_duration_weeks: Total block duration (default 4)

        Returns:
            Tuple of (max_strength_sessions, strength_endurance_sessions)
        """
        # Design max strength sessions with periodization
        max_strength = await self.design_strength_sessions(
            global_context,
            week_skeleton,
            week_number,
            block_duration_weeks
        )

        # Design strength endurance sessions
        strength_endurance = await self.design_strength_endurance_sessions(
            global_context,
            week_skeleton
        )

        return max_strength, strength_endurance
