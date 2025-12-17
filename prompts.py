"""
Prompt templates for each layer of training block generation.
Version 2: Philosophy-guided with realistic work capacity constraints.
"""
from models import TrainingPhase


def get_volume_schedule_text(block_objectives):
    """Generate a formatted text description of the weekly volume schedule."""
    volumes = block_objectives.get_weekly_volumes()
    progression_pct = block_objectives.get_progression_percent()

    # Build the schedule text
    lines = []
    lines.append(f"Training phase: {block_objectives.primary_goal.value.upper()} (progression: {progression_pct:+.1f}% per week)")
    lines.append("")

    for i, volume in enumerate(volumes, 1):
        week_type = "DELOAD" if i == len(volumes) and block_objectives.deload_week else "BUILD"
        lines.append(f"- Week {i}: {volume}km ({week_type})")

    return "\n".join(lines)


def get_layer_0_prompt(athlete_profile, block_objectives, injury_context=""):
    """Layer 0 - Context & Global Rules"""
    from models import HyroxWeights

    # Determine phase-specific instructions
    phase_instructions = ""
    if block_objectives.primary_goal == TrainingPhase.BASE:
        phase_instructions = "CURRENT PHASE: GENERAL PREPARATION (BASE). High Volume / Low Specificity. Goal: Build engine and structural strength. Running: Mostly Zone 2. Strength: Phase 1 (Volume). HYROX: Heavy overload, low heart rate."
    elif block_objectives.primary_goal == TrainingPhase.BUILD:
        phase_instructions = "CURRENT PHASE: SPECIFIC PREPARATION (BUILD). Moderate Volume / Moderate-High Intensity. Goal: Threshold development. Running: Threshold (T1/T2) focus. Strength: Transition Phase 1 to 2. HYROX: Race weights, compromised running."
    elif block_objectives.primary_goal == TrainingPhase.PEAK:
        phase_instructions = "CURRENT PHASE: COMPETITION (PEAK). Low Volume / Very High Intensity. Goal: Race specificity. Running: Race pace or faster. Strength: Phase 2 (Intensity). HYROX: Full race simulation intensity."
    elif block_objectives.primary_goal == TrainingPhase.TAPER:
        phase_instructions = "CURRENT PHASE: TAPER. Very Low Volume / High Intensity / Maximum Freshness. Goal: Shed fatigue to reveal fitness. Rule: Leave the gym feeling better than you entered. Cut volume by 40-60% but keep intensity sharp."
    elif block_objectives.primary_goal == TrainingPhase.TRANSITION:
        phase_instructions = """CURRENT PHASE: TRANSITION (Active Recovery). VERY Low Volume / VERY Low Intensity / Maximum Recovery.

**Purpose:** Allow physical and mental recovery after a competition or hard training block. Prepare the body for the next training phase.

**Training Prescription:**
- Running: Easy Zone 1-2 ONLY. Short duration (20-40 min max). No threshold work, no intervals, no tempo.
- Strength: Skip max strength sessions OR do light technique work only (50-60% loads, RPE 4-5, no progression).
- HYROX Combo: SKIP ENTIRELY. No race-weight work. No compromised running. This phase is about recovery, not race specificity.
- Strength Endurance: Skip or convert to light aerobic work (easy bike/erg).
- Primary Focus: Aerobic recovery sessions (30-50 min easy bike/erg/swim at Z1-Z2), mobility work, and rest.

**Volume Targets:**
- Total weekly running: 50-60% of normal volume, ALL easy pace
- Total sessions: 3-5 light sessions maximum (down from normal 6-9 sessions)
- Session duration: 30-50 min maximum
- Intensity distribution: 100% Zone 1-2 (NO Zone 3+)

**Key Principle:** Every session should leave you feeling BETTER than when you started. If in doubt, do less."""

    hr_max = athlete_profile.physiological_params.hr_max
    t1_pace = athlete_profile.physiological_params.threshold_t1_pace
    t2_pace = athlete_profile.physiological_params.threshold_t2_pace
    vo2_max = athlete_profile.physiological_params.vo2_max

    # Get official HYROX weights for the race category
    hyrox_weights = HyroxWeights.get_weights(block_objectives.race_type) if block_objectives.race_type else None

    injury_section = ""
    if injury_context:
        injury_section = f"\n**Current Injury Context:**\n{injury_context}\n"

    # Build VO2 max line if present
    vo2_line = f"\n- VO2 max: {vo2_max} ml/kg/min" if vo2_max else ""

    # Build race context section
    race_section = ""
    has_race_data = (block_objectives.target_race_date or block_objectives.race_type)

    if has_race_data:
        race_lines = []
        if block_objectives.target_race_date:
            race_lines.append(f"- Target race: {block_objectives.target_race_date}")
            if block_objectives.weeks_to_race:
                race_lines.append(f"- Weeks to race: {block_objectives.weeks_to_race}")
        if block_objectives.race_type:
            race_lines.append(f"- Race category: {block_objectives.race_type.replace('_', ' ').title()}")

        race_section = "\n**Race Context:**\n\n" + "\n".join(race_lines) + "\n"

    # Build equipment section
    equipment_list = ", ".join(athlete_profile.equipment.available_equipment)

    substitution_rules = []
    available = set(athlete_profile.equipment.available_equipment)

    if "Sled" not in available and "Sleds (push & pull)" not in available:
        substitution_rules.append("- No sleds → use heavy farmers carries, weighted step-ups, or resistance band pushes")
    if "SkiErg" not in available:
        substitution_rules.append("- No SkiErg → substitute RowErg or Echo/Assault Bike")
    if "Echo Bike" not in available and "Echo/Assault Bike" not in available:
        substitution_rules.append("- No Echo Bike → use RowErg or exercise bike at higher resistance")
    if "Wall Balls" not in available:
        substitution_rules.append("- No wall balls → use thrusters or goblet squat to press")

    substitution_section = ""
    if substitution_rules:
        substitution_section = "\n\n**Equipment Substitutions:**\n\n" + "\n".join(substitution_rules)

    # Build HYROX race specifications section
    hyrox_spec_section = ""
    if hyrox_weights:
        hyrox_spec_section = f"""
**Competition Category:**

- Category: {block_objectives.race_type.replace('_', ' ').title()}

**Official HYROX Race Specifications:**

All station loads are OFFICIAL RACE SPECIFICATIONS and must be prescribed EXACTLY:

1. **SkiErg**: 1000m
2. **Sled Push**: {hyrox_weights.sled_push_kg}kg over 50m
3. **Sled Pull**: {hyrox_weights.sled_pull_kg}kg over 50m
4. **Burpee Broad Jumps**: 80m total
5. **RowErg**: 1000m
6. **Farmers Carry**: {hyrox_weights.farmers_carry_kg[0]}kg per hand over 200m (2x{hyrox_weights.farmers_carry_kg[0]}kg total)
7. **Sandbag Lunges**: {hyrox_weights.sandbag_kg}kg over 100m
8. **Wall Balls**: {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m target, 100 reps

**Station Load Prescription Rules:**

- **ALWAYS use race weight** for station training
- Do NOT calculate percentages (e.g., "70% of race weight")
- If athlete cannot complete full volume, reduce REPS or DISTANCE, not load
- Example: Sled push = {hyrox_weights.sled_push_kg}kg for 4x25m (reduced distance), NOT 100kg for 4x50m (reduced weight)

**Progression Methods (in order of preference):**

1. **Volume**: Increase reps or distance at race weight (e.g., 4x25m → 6x25m → 4x50m)
2. **Density**: Reduce rest between sets while maintaining race weight and volume
3. **Strength**: Only in max strength sessions, use >race weight for lower volume (e.g., {hyrox_weights.sled_push_kg + 50}kg sled push 3x25m for overload)

**Station Duration Estimates (average race times by division):**

| Station | Pro Men | Pro Women | Open Men | Open Women |
|---------|---------|-----------|----------|------------|
| SkiErg 1000m | 4:09 | 4:56 | 4:24 | 5:21 |
| Sled Push 50m | 3:23 | 4:23 | 3:03 | 2:40 |
| Sled Pull 50m | 6:07 | 6:42 | 5:09 | 5:42 |
| Burpee Broad Jumps 80m | 4:20 | 5:16 | 4:57 | 4:56 |
| RowErg 1000m | 4:21 | 4:54 | 4:51 | 5:35 |
| Farmers Carry 200m | 2:24 | 2:41 | 2:49 | 2:16 |
| Sandbag Lunges 100m | 4:34 | 4:41 | 5:35 | 4:18 |
| Wall Balls 100 reps | 6:14 | 5:31 | 6:30 | 4:45 |
| Rox Zone (transitions) | 6:43 | 5:50 | 6:34 | 6:29 |
| Total Running 8km | 40:34 | 42:15 | 42:55 | 48:33 |

**Week 1 Calibration Principle:**

Week 1 is a BASELINE week - sessions should be challenging but clearly achievable. Better to undershoot and add volume in Week 2 than overshoot and force deload.

**Critical Prescription Format:**

- Sled push/pull: ALWAYS specify "{hyrox_weights.sled_push_kg}kg" or "{hyrox_weights.sled_pull_kg}kg" explicitly
- Farmers carry: ALWAYS specify "{hyrox_weights.farmers_carry_kg[0]}kg per hand" or "2x{hyrox_weights.farmers_carry_kg[0]}kg"
- Sandbag: ALWAYS specify "{hyrox_weights.sandbag_kg}kg"
- Wall balls: ALWAYS specify "{hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m target"

"""

    return f"""You are an elite HYROX coach and strict scheduler. You are designing training for {athlete_profile.name}, a {athlete_profile.age}-year-old hybrid athlete in a {block_objectives.primary_goal.value} phase.

**PERIODIZATION CONTEXT:**

{phase_instructions}

{injury_section}{race_section}{hyrox_spec_section}
**Physiological Parameters:**

- HRmax: {hr_max} bpm
- Zones: Z1 = 60–70%, Z2 = 70–80%, Z3 = 80–88%, Z4 = 88–94%, Z5 = 94–100%
- Threshold paces: T1 = {t1_pace}/km, T2 = {t2_pace}/km{vo2_line}

**Training Week Structure:**

- Training days: {athlete_profile.week_structure.get_training_days_range()} ({athlete_profile.week_structure.rest_days} = rest)
- Main sessions: {athlete_profile.week_structure.main_sessions_per_week} total per week (includes {athlete_profile.week_structure.get_num_double_days()} double-days)
- Running sessions: {athlete_profile.week_structure.runs_per_week} runs per week
- Session time budgets: {athlete_profile.week_structure.weekday_session_time_min}–{athlete_profile.week_structure.weekday_session_time_max} min weekdays; {athlete_profile.week_structure.weekend_session_time_min}–{athlete_profile.week_structure.weekend_session_time_max} min weekends

**Equipment:**

- Primary location: {athlete_profile.equipment.primary_location}
- Available: {equipment_list}{substitution_section}

**Weekly Volume Schedule:**

{get_volume_schedule_text(block_objectives)}

**Guardrails:**

- Pain ≤{athlete_profile.injury_info.pain_threshold_during}/10 during & ≤{athlete_profile.injury_info.pain_threshold_next_day}/10 next-day → cut volume or swap run→bike
- Soreness >{athlete_profile.injury_info.soreness_cutoff_hours}h → reduce next run volume {athlete_profile.injury_info.volume_reduction_percent}–40%
- Manage plyometric load based on athlete readiness and injury status

**Macrocycle Logic:**

- {block_objectives.block_duration_weeks}-week progressive build + 1-week deload (cut volume 40–50%, intensity 20%)

**Session Archetypes (must appear each microcycle):**

- **Running Quality** (threshold, VO₂, progression, fartlek)
- **Running Endurance** (Z2, long run)
- **Strength (Maximal)** (compound lifts, %1RM)
- **Strength Endurance** (circuits/EMOM/AMRAP including cardio engines)
- **HYROX Combo/Brick** (run + station, compromised running, Zone 4–5)
- **Aerobic Engine/Recovery** (bike/erg steady Z2, technique, mobility)

**CRITICAL TRAINING PRINCIPLES:**

**1. SPECIFICITY ≠ SIMULATION**
- Training for HYROX means developing the adaptations needed to excel at HYROX
- Not every session replicates race demands
- Progressive exposure to race-specific stress across the block
- Build the engine first, then apply it to race-specific contexts

**2. BRICK SESSIONS ≠ THRESHOLD DEVELOPMENT**
- Brick sessions use threshold paces (T1/T2) but are NOT the same as dedicated threshold running
- HR is spiking from stations, running form is compromised, can't sustain pure threshold physiological stimulus
- Purpose: Learn to run on tired legs, practice race-specific skills
- Dedicated threshold sessions (Layer 2) provide actual physiological development

**3. EXERCISE SELECTION PRIORITY**
For strength endurance and brick sessions:
1. Target muscle groups effectively
2. Use HYROX stations when they're the best tool for the job
3. Freely substitute superior alternatives when appropriate
4. Quality of training stimulus > literal race simulation
Example: A trap bar deadlift might build sled-pulling strength better than doing sleds twice a week

**Design Rules (apply to every session):**

- Each session must include: Purpose, Warm-up, 2–3 Main Blocks, Cooldown, Transfer Explanation, Progression Dials
- Occasional overload allowed only in Week {block_objectives.block_duration_weeks}
- Strength Endurance sessions must **always include cardio modalities (run, SkiErg, RowErg, Echo bike, or bike)** within the session
- Maintain strict alternation of hard/easy days to avoid burnout

**Output Convention:** Follow subsequent layer prompts. Do not jump ahead."""


def get_layer_1_prompt(block_objectives, athlete_profile):
    """Layer 1 - Week 1 Skeleton Overview"""
    sessions = athlete_profile.week_structure.main_sessions_per_week
    training_days = athlete_profile.week_structure.get_training_days_range()
    long_run_day = athlete_profile.week_structure.long_run_day
    double_days = athlete_profile.week_structure.double_days
    weekend_min = athlete_profile.week_structure.weekend_session_time_min
    weekend_max = athlete_profile.week_structure.weekend_session_time_max

    return f"""Using Layer 0 rules, design the Week 1 skeleton.

**Objectives:**

- Establish baseline weekly running volume ({block_objectives.running_mileage_week1}km total mileage)
- Balance intensity: alternate hard/easy days, prevent overload
- Cover all session archetypes (Running Quality, Running Endurance, Max Strength, Strength Endurance, HYROX Combo, Aerobic Engine/Recovery)
- Ensure the week includes a total of {sessions} main sessions across the training days

**Structure required in output:**

- Show **{training_days}** schedule as a table with columns: *Day | Main AM | Main PM*
- Indicate run mileage distribution to total {block_objectives.running_mileage_week1}km
- Label each session by **archetype** only (e.g., "Run Quality – Threshold Intervals," "Strength Endurance – EMOM w/ SkiErg")
- Flag which sessions are high intensity (Z4–5) and which are low/moderate (Z1–3)

**Important constraints:**

- Avoid consecutive high-intensity days
- **CRITICAL: The long run MUST be scheduled on {long_run_day}** ({weekend_min}–{weekend_max} min, Zone 2). This is a hard requirement.
- **CRITICAL: Double days (AM + PM sessions) MUST be on {double_days}**. These are the only days that should have both Main AM and Main PM sessions. This is non-negotiable.
- HYROX Combo (Zone 4–5) occurs once this week

**Output convention:** Just provide the **skeleton schedule** — no full session details yet. Full designs come in later layers."""


def get_layer_2_prompt(block_objectives, t1_pace, t2_pace, athlete_profile):
    """Layer 2 - Running Sessions Expansion"""
    runs = athlete_profile.week_structure.runs_per_week
    long_run_day = athlete_profile.week_structure.long_run_day
    weekend_min = athlete_profile.week_structure.weekend_session_time_min
    weekend_max = athlete_profile.week_structure.weekend_session_time_max

    # TRANSITION phase gets completely different running prescription
    if block_objectives.primary_goal == TrainingPhase.TRANSITION:
        return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the running sessions into full detail.

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

Provide 2-4 easy running sessions (based on skeleton from Layer 1) with the structure above. Each should be clearly labeled as "Easy Recovery Run" with duration, pace guidance (as T1+Xs/km), and HR zones. Make it abundantly clear that these are OPTIONAL and should be skipped if the athlete isn't feeling fully recovered."""

    return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the running sessions into full detail.

**CRITICAL CONTEXT:**

Brick sessions (Layer 5) provide race-specific running practice but do NOT replace dedicated threshold development. Design true running quality sessions here - these are CLEAN running sessions with proper warm-up, focused effort at target zones, and adequate recovery. Not compromised running. Not fatigued running. Pure physiological development.

**Objectives:**

- Total weekly volume: **{block_objectives.running_mileage_week1}km** (Week 1), distributed across {runs} runs
- Phase-appropriate progression: {block_objectives.get_progression_percent():+.1f}% per week ({block_objectives.primary_goal.value} phase)
- Cover 2x Quality sessions (threshold / intervals), 1x Long Z2 run, 1x Easy Z2 run
- Alternate hard and easy days; avoid stacking high intensity
- Assign each run clear **purpose** (e.g., Threshold Intervals for clearance, Long Run for base)

**Threshold Development (Primary Focus):**

**Duration:** 8-36 minutes of quality threshold work per session

**Available Formats:**
- Continuous Tempo: 20-28 min @ T1 pace (builds aerobic foundation)
- Cruise Intervals: 2-4 × 8-15 min @ T1, 2-4 min recovery (high volume with brief breaks)
- Threshold Intervals: 4-8 × 3-6 min @ T2, 90-120s recovery (practice race pace)
- Progressive Tempo: Start @ T1, progress toward T2 (simulate fatigue)

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


def get_layer_3_prompt(block_objectives):
    """Layer 3 - Max Strength Sessions Expansion"""

    # Determine rep range instructions based on phase
    rep_instructions = ""
    if block_objectives.primary_goal == TrainingPhase.BASE:
        rep_instructions = "Use PHASE 1 Rep Ranges (6-8 reps) exclusively for volume accumulation."
    elif block_objectives.primary_goal == TrainingPhase.BUILD:
        rep_instructions = "Start with Phase 1, progressing toward Phase 2 (heavier loads)."
    elif block_objectives.primary_goal == TrainingPhase.PEAK:
        rep_instructions = "Use PHASE 2 Rep Ranges (4-5 reps) exclusively for peak strength."
    elif block_objectives.primary_goal == TrainingPhase.TAPER:
        rep_instructions = "PRIMING SESSION ONLY. Reduce volume to 2 sets max. Maintain heavy loads (75-80%) to keep CNS primed, but low reps (RPE 6-7). NO FAILURE. Goal is tension without fatigue."
    elif block_objectives.primary_goal == TrainingPhase.TRANSITION:
        rep_instructions = "Unstructured or skip."

    return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the Max Strength sessions into full detail.

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


def get_layer_4_prompt(hyrox_weights, block_objectives):
    """Layer 4 - Strength Endurance Sessions Expansion"""

    # TRANSITION phase gets completely different guidance
    if block_objectives.primary_goal == TrainingPhase.TRANSITION:
        return """Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the Strength Endurance sessions into full detail.

**TRANSITION PHASE - STRENGTH ENDURANCE PRESCRIPTION:**

**RECOMMENDED: SKIP STRENGTH ENDURANCE SESSIONS ENTIRELY during TRANSITION phase.**

If the skeleton from Layer 1 includes a Strength Endurance session, REPLACE it with one of these light recovery alternatives:

**Option 1: Easy Aerobic Session (PREFERRED)**
- 30-40 min easy bike, RowErg, or SkiErg at Zone 1-2
- HR: 60-75% max
- RPE: 3-4 out of 10 (very comfortable)
- Purpose: Active recovery, gentle movement
- Include 5 min easy warm-up and 5 min easy cooldown
- Can add 10-15 min of mobility work after

**Option 2: Movement & Mobility Session**
- 30-40 minutes total
- Light dynamic stretching (10 min)
- Yoga flow or Pilates (20 min)
- Breathing work (5-10 min)
- NO strength work, NO high heart rate
- Purpose: Restore range of motion, mental recovery

**Option 3: VERY Light Movement Circuit (only if athlete insists on some resistance work)**
- Duration: 20-30 min max
- Format: 3-4 rounds, walk pace between exercises, 2-3 min rest between rounds
- RPE: 4-5 max (very light, conversational throughout)
- Exercises: 4-5 bodyweight or very light movements
  - Example: 10 air squats, 8 push-ups (or incline push-ups), 20m easy walk, 10 glute bridges, 30s plank
- NO cardio machines, NO HYROX stations, NO race weights
- Heart rate should stay in Zone 1-2 throughout

**CRITICAL RULES:**

- This is RECOVERY, not training
- If in doubt, skip the session entirely
- Better to do easy bike than any strength work
- NO metabolic fatigue, NO high heart rate, NO heavy loads
- Athletes should leave feeling refreshed, not tired

**Output format:**

If a Strength Endurance session appears in the skeleton, replace it with Option 1 (Easy Aerobic Session) or clearly state "SKIP - Use rest day or light 30-min bike at Z1-2 instead." """

    return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the Strength Endurance sessions into full detail.

**CRITICAL DEFINITION:**

Strength endurance sessions build the ability to sustain power output under metabolic fatigue. These are NOT traditional strength sessions.

**What They Are NOT:**
❌ Traditional strength with 5/3/1 progressions
❌ Heavy singles or triples (>85% 1RM)
❌ 2-3 minute rest periods between sets
❌ Maximal load focus
❌ "NFT" (Not For Time) accessory work at walking pace

**What They ARE:**
✅ Time-constrained work formats
✅ Under 2 minutes rest maximum
✅ Moderate loads (40-70% 1RM)
✅ High heart rate / lactate focus
✅ Sustained output across multiple rounds

**FOUR VALID FORMATS:**

Choose ONE to TWO formats per session. Total work time across all formats in the session must add up to 35-50 minutes.

**Format 1: CIRCUIT**
- 3-6 rounds with 1-3 min rest between rounds
- 5-7 exercises per round
- MUST include cardio machine (Row/Ski/Bike)
- Structured, repeatable progression

**Format 2: AMRAP (As Many Rounds As Possible)**
- 20-40 minute time cap
- 5-7 exercises per round
- MUST include cardio machine (Row/Ski/Bike)
- No rest - continuous work
- Self-regulated pacing, mental toughness focus

**Format 3: EMOM (Every Minute on the Minute)**
- 15-30 minute duration
- 5-6 exercises rotating
- MUST include cardio machine (Row/Ski/Bike)
- 10-20s built-in rest per minute

**Format 4: IWT (Interval Weight Training)**
- 5-6 rounds, 90s-3 min work per round
- 60-90s rest between rounds
- MUST include cardio machine (Row/Ski/Bike)
- ALWAYS: Cardio machine FIRST, then strength movement
- High-intensity lactate training

**CRITICAL:** All four formats MUST include cardio machines (Row, Ski Erg, or Air Bike). This is non-negotiable.

**Official HYROX Station Weights (Use These Exactly):**

- Sled Push: {hyrox_weights.sled_push_kg}kg
- Sled Pull: {hyrox_weights.sled_pull_kg}kg
- Wall Balls: {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m
- Sandbag: {hyrox_weights.sandbag_kg}kg
- Farmers Carry: 2×{hyrox_weights.farmers_carry_kg[0]}kg

**EXERCISE SELECTION (Must Include 3 Categories):**

**A. HYROX-Specific (2-3 exercises):**
- SkiErg: 250-500m
- Rowing: 250-500m
- Sled Push/Pull: 12.5-25m
- Farmer's Carry: 40-100m
- Wall Balls: 20-35 reps
- Burpees: 10-20 reps or 20-60m
- Lunges (weighted): 15-40 reps or 25-80m

**B. Functional Movements (2-3 exercises):**
- DB Thrusters: 15-25 reps
- KB Swings: 15-25 reps
- Devil Press: 10-20 reps
- Box Step-ups: 15-25 reps
- Burpee box jumps: 10-20 reps
- Air Squat jumps: 15-25 reps
- Push-ups: 10-20 reps
- DB Snatch (alternating): 15-25 reps

**C. Traditional Strength (0-2 exercises, OPTIONAL):**
- ONLY moderate loads (RPE 5-7)
- KB/DB Deadlifts: 15-25 reps
- DB Press variations: 12-20 reps
- Pull-up variations: 8-15 reps
- NOT heavy barbell work

**Exercise Selection Philosophy:**

**Priority Order:**
1. Target muscle groups effectively
2. Use HYROX stations when they're the best tool for the job
3. Freely substitute superior alternatives when appropriate
4. Quality of training stimulus > literal race simulation

Example: A trap bar deadlift might build sled-pulling capacity better than doing sleds twice a week. Bulgarian split squats might develop quad endurance more effectively than sandbag lunges in certain contexts.

**FORMAT-SPECIFIC RULES:**

**CIRCUIT Format:**
- Rest: 1-3 minutes between rounds
- MUST include cardio machine (Row/Ski/Bike) - NOT optional
- Progression: Weeks 1-4 (2-3' rest), Weeks 5-8 (1-2' rest), Weeks 9-12 (1' rest or race pace)
- Load: Sustainable across all rounds, RPE 5-7
- Example structure: 5 rounds, 2' rest: 500m Row @2k+10" → 20 KB Deadlifts → 20 Air Squats → 15 Push-ups → 10 Burpees

**AMRAP Format:**
- Time cap: 15-30 minutes
- NO rest - continuous work
- MUST include cardio machine (Row/Ski/Bike) - NOT optional
- Conservative loads for sustained effort, RPE 6-7
- Emphasizes pacing strategy and mental game
- Example: 20-min AMRAP: 250m Row → 15 Wall Balls → 25m Sled Push → 10 Devil Press → 80m Farmer's Carry

**EMOM Format:**
- Duration: 15-30 minutes
- MANDATORY: Must include cardio machine in rotation
- 5-6 exercises rotating (NOT just 2)
- Work fills 40-50 seconds, 10-20s rest per minute

**5-Exercise Rotation:**
Minute 1: Cardio Machine 1 (e.g., Row 15 cal)
Minute 2: Functional Movement (e.g., Push-ups 15-20)
Minute 3: HYROX Movement (e.g., Wall Balls 20)
Minute 4: Functional Movement (e.g., KB Swings 15)
Minute 5: Cardio Machine 2 (e.g., Ski 15 cal)
Repeat 3-6 rounds

**6-Exercise Rotation:**
Minute 1: Cardio Machine 1 (e.g., Row 15 cal)
Minute 2: Functional Movement (e.g., DB Thrusters 15)
Minute 3: HYROX Movement (e.g., Sled Push 12.5m)
Minute 4: Functional Movement (e.g., Box Step-ups 20)
Minute 5: Cardio Machine 2 (e.g., Ski 15 cal)
Minute 6: HYROX Movement (e.g., Burpees 12)
Repeat 3-5 rounds

**IWT Format:**
- Structure: ALWAYS Cardio Machine → Strength Movement
- 5-6 rounds, 90s-3 min work per round
- 60-90s rest between rounds
- Cardio: 85-90% effort (NOT max)
- Strength: Max reps with good form until time cap

**Cardio Options (60-90s):**
- Row: 20-30 calories or 500m
- Ski Erg: 500m @ 85-90%
- Air Bike: 20-30 calories @ 85-90%

**Strength Options (remaining time until 2:00):**
- Shoulder to Overhead (95-135lb): max reps
- Thrusters (95-135lb): max reps
- Devil Press (35-70lb): max reps
- Power Snatch (95-135lb): max reps
- Wall Balls: max reps
- Burpee Pull-ups: max reps

Example: 6 rounds every 3:00: 500m Ski @ 85-90% → Max Thrusters 95lb until 2:00 → Rest remaining time

**LOAD GUIDELINES:**

**General:**
- Barbell: 95-165lb (typically 95-135lb)
- Kettlebell: 35-70lb
- Dumbbell: 35-70lb
- Should allow "finish each set with some left in the tank"

**Progression (choose 1-2, NOT all):**
1. Density: Reduce rest between efforts
2. Volume: More rounds/reps at same intensity
3. Load: Heavier resistance at same volume

**INTENSITY MARKERS:**

- Circuit/AMRAP: RPE 6-7, HR Z2-Z4
- EMOM: RPE 6-8, should have 10-15s rest each minute
- IWT: "Lactate explosion," 85-90% on cardio, described as "very hard to make the shift"

**Objectives:**

- Build the ability to sustain submaximal strength under fatigue
- Develop work capacity and lactate tolerance
- Force adaptation by pairing strength movements with cardio intervals
- Time cap: 60–75 min total session

**Structure required in output:**

For EACH strength endurance session, include:

- **Purpose** (clear link to HYROX transfer and why this format was chosen)
- **Format** (Circuit / AMRAP / EMOM / IWT)
- **Warm-up** (mobility, activation, light machine work, 5-10 min)
- **Main Blocks** (full session prescription using chosen format)

  For EVERY exercise, specify:
  - Movement name
  - Exact weight in kg (race weight for HYROX stations)
  - Target height for wall balls
  - Distance, reps, or duration
  - Rest periods (for Circuit/IWT) or work structure (for EMOM/AMRAP)
  - Intensity targets (HR zone, RPE, pace reference like @2k+10")

  Example formats:
  - Circuit: "5 rounds, 2' rest: 400m Row @2k+5" → 15 Thrusters 2x15kg DB → 25m Sled Push {hyrox_weights.sled_push_kg}kg → 15 Wall Balls {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m"
  - AMRAP: "20-min AMRAP: 250m Row → 15 KB Swings 24kg → 10 Box Step-ups 20" → 10 Push-ups → 50m Sled Push {hyrox_weights.sled_push_kg}kg"
  - EMOM: "21-min EMOM (7 rounds): Min 1: 15 cal Row | Min 2: 15-20 Push-ups | Min 3: 12-15 KB Cleans 2x24kg"
  - IWT: "6 rounds every 3:00: 25 cal Row (target sub-60s) → Max Thrusters 95lb until 2:00 → Rest remaining time"

- **Cooldown** (walk, flush, mobility, breathing, 10-15 min)
- **Transfer Explanation** (how this builds toward HYROX race demands)
- **Progression Knob** (how to scale in later weeks - volume, density, load, or machine interval adjustments)

**Rules:**

- ALL formats MUST include cardio machines - NOT optional
- EMOM must use 5-6 exercises rotating, NOT just 2
- Keep heart rate between upper Zone 2 → mid Zone 4 depending on format
- Each main block should last 12–25 minutes
- Balance sessions across the week: one more sled/carry focused; one more erg/wall ball focused
- Explicit substitutions if needed (bike for run, alternatives for missing equipment)

**Format Selection Guidance:**

- Circuit: Structured practice, clear rounds, good for learning stations
- AMRAP: Continuous work, teaches pacing, mental toughness
- EMOM: Variety with time constraints, lactate tolerance, 5-6 movement rotation
- IWT: Maximum intensity intervals, explicit cardio-strength pairing

Choose formats that match athlete experience level and training phase objectives.

**Output convention:**

- Present as a **list of 2 Strength Endurance sessions** (as per Week 1 skeleton)
- Label clearly with format: *Strength Endurance Session 1 (EMOM - Row/Ski/Strength)*, *Strength Endurance Session 2 (Circuit - HYROX Stations)*
- Each session should be fully detailed with all numbers, loads, paces, and rest periods"""


def get_layer_5_prompt(hyrox_weights, block_objectives):
    """Layer 5 - HYROX Combo / Brick Session Expansion"""

    # Determine focus instructions based on phase
    if block_objectives.primary_goal == TrainingPhase.BASE:
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
    elif block_objectives.primary_goal == TrainingPhase.BUILD:
        focus_instructions = (
            "Focus: THRESHOLD INTEGRATION.\n"
            "- Purpose is to connect your clean threshold work to HYROX specificity: running strongly at or just below T1 after hard stations.\n"
            "- Use 400–800 m run segments at around T1 pace (occasionally T1+10 sec/km if fatigue builds).\n"
            "- Total compromised running should be ~3–5 km.\n"
            "- Station loads are typically at race weight; mild overload (5–10%) is allowed for one key station.\n"
        )
    elif block_objectives.primary_goal == TrainingPhase.PEAK:
        focus_instructions = (
            "Focus: RACE SIMULATION.\n"
            "- Purpose is to rehearse race-day demands with mini HYROX blocks.\n"
            "- Use 600–1000 m run segments between stations, mostly at T1 pace with occasional segments nudging toward T2 "
            "(e.g. 5-10s/km faster than T1 pace).\n"
            "- Total compromised running should be ~4–6 km.\n"
            "- Station volumes should be 70–100% of race volume for selected stations; at most one station may be slightly overloaded.\n"
        )
    elif block_objectives.primary_goal == TrainingPhase.TAPER:
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

    return f"""Using Layer 0 rules, the current TrainingPhase, and the weekly skeleton from Layer 1, expand only the HYROX Combo / Brick session into a fully detailed workout.

You are designing a single HYROX combo / brick session that trains compromised running and HYROX station execution.

**Official HYROX Race Specifications:**

- Sled Push: {hyrox_weights.sled_push_kg}kg
- Sled Pull: {hyrox_weights.sled_pull_kg}kg
- Farmers Carry: {hyrox_weights.farmers_carry_kg}kg (total, split across both hands)
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


def get_layer_6_prompt():
    """Layer 6 - Aerobic Engine/Recovery Session"""
    return """Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand the Aerobic Engine/Recovery session into full detail.

**Objectives:**

- Build aerobic base without running stress
- Promote recovery between high-intensity sessions
- Maintain movement quality and cardiovascular training stimulus

**Structure required in output:**

- **Purpose** (why low-intensity bike/erg work supports HYROX training)
- **Warm-up** (5–10 min ramp-up)
- **Main work** (30–50 min steady Z2 on bike or erg; technique cues; HR targets)
- **Cooldown** (mobility, stretch, breathwork)
- **Substitutions** (alternative modalities if needed)
- **HYROX Transfer** (how this supports race performance)
- **Progression knob** (extend duration, add short tempo surges in later weeks)

**Output convention:**

- Present as **1 complete Aerobic Engine/Recovery session** with full detail"""


def get_layer_7_prompt(block_objectives, athlete_profile):
    """Layer 7 - Assemble Full Week 1"""
    sessions = athlete_profile.week_structure.main_sessions_per_week
    training_days = athlete_profile.week_structure.get_training_days_range()

    return f"""Using Layers 0–6, assemble the complete Week 1 training program.

**CRITICAL: Token Budget Constraint**
You MUST complete the ENTIRE week within 7,500 tokens. Prioritize essential actionable detail over verbose explanations. Be comprehensive but efficient.

**Objectives:**

- Produce a **day-by-day Week 1 program** with **all essential session detail**
- Maintain **consistency with the skeleton plan from Layer 1**
- Ensure **weekly running volume totals ~{block_objectives.running_mileage_week1} km**
- **CRITICAL: The long run MUST be scheduled on {athlete_profile.week_structure.long_run_day}**. Verify this in your output.
- **CRITICAL: Double days (AM + PM) MUST be on {athlete_profile.week_structure.double_days}**. No other days should have double sessions. Verify this in your output.

**Structure required in output:**

- **IMPORTANT: Always start weeks on Monday** (even if Monday is a rest day). Present the week as Monday → Sunday.
- For each day (Monday through Sunday):
    - If it's a rest day, simply state: "**Monday: Rest Day**"
    - If it's a training day, list **Main AM** and **Main PM (if double day)**
    - Under each session, include:
        - **Purpose** (1-2 sentences: how it supports HYROX + {block_objectives.primary_goal} phase)
        - **Warm-up** (brief structure: duration, key movements)
        - **Main Work** (all sets/reps/km/HR/paces/rest - this is the critical detail)
        - **Cooldown** (brief structure)
        - **Progression** (1-2 sentences on how to evolve in later weeks)

**Efficiency Guidelines to Stay Within Token Budget:**

- **Purpose sections:** 1-2 concise sentences (not paragraphs)
- **Warm-ups:** Structure and duration only (not step-by-step coaching cues)
- **Main Work:** Full prescription (this is non-negotiable) but remove redundant explanations
- **Cooldowns:** Structure only (movements + duration)
- **Remove:** Verbose coaching narratives, philosophical explanations, redundant examples, pain protocol adjustment sections
- **Keep:** All numbers (sets, reps, paces, distances, HR zones, rest periods, progressions)

**Rules:**

- **Essential detail preserved** → all workout prescriptions must be complete and actionable
- **Explicitly calculate and show total running mileage** at the end
- Highlight session intensity (Z1–Z5) clearly
- Use clean formatting (headings, tables where appropriate for efficiency)

**CRITICAL: Max Strength Session Requirements (Layer 3 - NON-NEGOTIABLE):**

When including Max Strength sessions in Week 1, you MUST follow these structural rules from Layer 3:

1. **Exactly 3 compound lifts** - ONE from each category:
   - Category A (Hip-Dominant): Trap Bar Deadlift, Conventional Deadlift, OR RDL
   - Category B (Knee-Dominant): Front Squat, Goblet Squat, OR High Bar Back Squat
   - Category C (Upper Body): Push Press, Weighted Chin-Ups, OR Incline Bench Press
   - **DO NOT substitute sleds, carries, or other movements for these categories**

2. **Specific rep targets** based on phase:
   - Phase 1 (early weeks): Use "8-7-7-6" or "8-8-7-7" (NOT "6-8 reps")
   - Phase 2 (later weeks): Use "5-5-4-4" or "5-5-5-4" (NOT "4-5 reps")
   - Week 1 is ALWAYS Phase 1, so use 8-7-7-6 pattern

3. **Exactly 4 accessory exercises** in circuit format (NOT 3):
   - Slot 1: Vertical push OR pull (opposite of Compound 3)
   - Slot 2: Unilateral lower body
   - Slot 3: Horizontal push OR pull (opposite of Compound 3, same as Slot 1)
   - Slot 4: Core/anti-rotation
   - **IF Compound 3 is push → Slots 1 & 3 are both PULL**
   - **IF Compound 3 is pull → Slots 1 & 3 are both PUSH**

**If these rules are violated, the Max Strength session is INVALID and must be corrected.**

**Output convention:**

- Label clearly: *Week 1 – {block_objectives.primary_goal} Phase*
- End with a summary:
    - "Total run mileage = XX km (target ~{block_objectives.running_mileage_week1} km)"
    - "Total sessions = {sessions} main sessions"

**After the full week, provide an intensity audit:**

Calculate the approximate time spent in each intensity zone across all sessions:
- Easy (Z1–Z2): % of total time
- Moderate (Z3): % of total time
- Hard (Z4–Z5): % of total time

Target: Easy = 60–70%, Moderate = ~20%, Hard = ~10%

Mark the intensity balance as ✅ (on target), ⚠️ (slightly off), or ❌ (needs adjustment).

**Remember: You MUST complete the full week (all 7 days) within your response. Prioritize workout prescriptions over explanatory text.**"""


def get_week_progression_prompt(week_number, previous_week_content, block_objectives, athlete_profile):
    """Generic prompt for Week 2, 3, or 4 progression"""
    from models import HyroxWeights

    # Get the pre-calculated weekly volumes
    weekly_volumes = block_objectives.get_weekly_volumes()
    week_km = weekly_volumes[week_number - 1] if week_number <= len(weekly_volumes) else weekly_volumes[-1]
    progression_pct = block_objectives.get_progression_percent()

    sessions = athlete_profile.week_structure.main_sessions_per_week
    training_days = athlete_profile.week_structure.get_training_days_range()
    runs = athlete_profile.week_structure.runs_per_week
    hyrox_weights = HyroxWeights.get_weights(block_objectives.race_type) if block_objectives.race_type else None

    # Dynamic phase description based on actual block duration
    total_weeks = block_objectives.block_duration_weeks
    weeks_remaining = total_weeks - week_number

    if week_number == 2:
        phase_description = "modest progression"
    elif week_number == total_weeks:
        # Final week of the block
        if block_objectives.deload_week:
            phase_description = f"peak / overload (final hard week - deload follows in Week {total_weeks + 1})"
        else:
            phase_description = "peak / overload (final week)"
    elif week_number == total_weeks - 1:
        # Second-to-last week
        phase_description = f"peak / overload (second hardest week - one more build week remains)"
    elif weeks_remaining <= 2:
        # Within 2 weeks of the end
        phase_description = f"continued progression ({weeks_remaining} week{'s' if weeks_remaining > 1 else ''} until peak)"
    else:
        # Middle weeks
        phase_description = "continued progression"

    # Build HYROX weights section if race category is provided
    hyrox_section = ""
    if hyrox_weights:
        hyrox_section = f"""
**Week {week_number} Station Weights (Race Weight - No Changes):**

- Sled Push: {hyrox_weights.sled_push_kg}kg
- Sled Pull: {hyrox_weights.sled_pull_kg}kg
- Wall Balls: {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m
- Sandbag: {hyrox_weights.sandbag_kg}kg
- Farmers Carry: 2×{hyrox_weights.farmers_carry_kg[0]}kg

**Progression Strategy:**

- Keep all station weights at race weight
- Progress via VOLUME (more rounds, more reps, longer distances)
- Progress via DENSITY (less rest, longer work periods, more rounds per EMOM)
- Do NOT reduce loads or use percentages

"""

    return f"""Using the completed Week {week_number - 1} program as the foundation, design a Week {week_number} {phase_description} that builds load in a structured and safe way.

**CRITICAL: Token Budget Constraint**
You MUST complete the ENTIRE week within 7,500 tokens. Prioritize essential workout prescriptions over verbose explanations. Be comprehensive but efficient.

**Previous Week Content:**
{previous_week_content[:2000]}... (see full context above)
{hyrox_section}
**Progression Rules:**

1. **Running Volume**
    - Target **total weekly mileage: {week_km:.0f} km** (phase-appropriate {progression_pct:+.1f}% progression)
    - Distribute volume proportionally across sessions (do not overload a single run)

2. **Intensity Balance**
    - Week 2: Maintain **Easy = 60–70%**, **Moderate = ~20%**, **Hard = ~10%** of total time
    - Week 3+: Allow **Easy = 55–65%**, **Moderate = 20–25%**, **Hard = 10–15%** (slightly more hard work)
    - Preserve strict alternation: no back-to-back Z4–Z5 sessions

3. **Progression Types**
    - **Running quality sessions**: Progress by slightly longer intervals, OR additional reps, OR slightly reduced rest. **Do not progress all three at once.**
    - **Strength sessions**: Progress either load, volume, or movement complexity — **not all at once**
    - **Strength endurance**: Increase **time-under-tension or conditioning element** (e.g., longer EMOMs, extended bike/row/run blocks)

4. **Guardrails**
    - Pain ≤2/10 during and ≤3/10 next day → if exceeded, cut or swap
    - No back-to-back **hard (Z4–Z5)** sessions
    - Running surfaces = flat/soft or track where possible
    - **CRITICAL: Long run MUST remain on {athlete_profile.week_structure.long_run_day}**. Do not move it to a different day.
    - **CRITICAL: Double days (AM + PM) MUST remain on {athlete_profile.week_structure.double_days}**. Do not move them or add double days on other days.

**Output Requirements:**

- **IMPORTANT: Always start weeks on Monday** (even if Monday is a rest day). Present the week as Monday → Sunday.
- Provide a **full Week {week_number} schedule** - all 7 days (Monday through Sunday) MUST be included.
- For rest days, simply state: "**Monday: Rest Day**" (or whichever day is the rest day).
- Include all **{sessions} main sessions** ({runs} runs + other sessions) with explicit structure (sets, reps, paces, HR zones, rests).
- Indicate expected **km per run session** so weekly total = ~{week_km:.0f} km.
- Tag each session as **Easy / Moderate / Hard**.
- Provide a short **note on progression rationale** for each session (e.g., "increased intervals from 4x6min → 5x6min").
- End with an **intensity distribution check (percentages)** and a ✅/⚠️/❌ rating.

**Efficiency Guidelines:**
- **Keep it concise:** Brief purpose statements (1-2 sentences), workout prescriptions with all numbers, short cooldowns.
- **Remove:** Lengthy coaching narratives, philosophical explanations, redundant examples, pain protocol adjustment sections.
- **Preserve:** All workout numbers, progression notes, key technical cues.

**Remember: You MUST complete the full week (all 7 days) within your response. Prioritize workout prescriptions over explanatory text.**"""


def get_deload_prompt(week_number, peak_week_content, block_objectives, athlete_profile):
    """Layer 10 - Deload Week"""
    from models import HyroxWeights

    # Get the pre-calculated weekly volumes (deload is last week)
    weekly_volumes = block_objectives.get_weekly_volumes()
    deload_km = weekly_volumes[-1] if weekly_volumes else block_objectives.running_mileage_week1
    peak_km = weekly_volumes[-2] if len(weekly_volumes) > 1 else block_objectives.running_mileage_week1

    sessions = athlete_profile.week_structure.main_sessions_per_week
    training_days = athlete_profile.week_structure.get_training_days_range()
    runs = athlete_profile.week_structure.runs_per_week
    hyrox_weights = HyroxWeights.get_weights(block_objectives.race_type) if block_objectives.race_type else None

    # Build HYROX deload section if race category is provided
    hyrox_deload_section = ""
    if hyrox_weights:
        hyrox_deload_section = f"""
**Deload Week Station Loads:**

- Keep race weight: Sled Push {hyrox_weights.sled_push_kg}kg, Sled Pull {hyrox_weights.sled_pull_kg}kg, Wall Balls {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m, Sandbag {hyrox_weights.sandbag_kg}kg, Farmers Carry 2×{hyrox_weights.farmers_carry_kg[0]}kg
- Reduce VOLUME by ~40-50% (fewer rounds, fewer reps, shorter distances)
- Increase REST periods significantly (double or triple rest from peak week)
- Focus on quality movement and race weight familiarity, not maximal effort
- Example: If peak week had "4 rounds: Sled Push {hyrox_weights.sled_push_kg}kg 50m", deload might be "2 rounds: Sled Push {hyrox_weights.sled_push_kg}kg 25m, 3 min rest"

"""

    return f"""Using the Week {block_objectives.block_duration_weeks} Peak / Overload week as the foundation, design a Deload Week (Week {week_number}) that reduces training stress to promote recovery and adaptation, while maintaining movement quality and rhythm.

**CRITICAL: Token Budget Constraint**
You MUST complete the ENTIRE week within 7,500 tokens. Prioritize essential workout prescriptions over verbose explanations. Be comprehensive but efficient.

**Peak Week Content:**
{peak_week_content[:2000]}... (see full context above)
{hyrox_deload_section}
**Deload Rules:**

1. **Running Volume**
    - Reduce **weekly mileage by ~30–40%** compared to Week {block_objectives.block_duration_weeks} (target ≈ {deload_km:.0f} km)
    - Keep **all {runs} runs**, but shorten distances and/or reduce interval reps

2. **Intensity Distribution**
    - Global target:
        - **Easy = 70–80%**
        - **Moderate = 15–20%**
        - **Hard = ≤5%** (keep touches of intensity sharp but very short)

3. **Strength & Strength Endurance**
    - **Strength**: Reduce load to ~60–70% of Week {block_objectives.block_duration_weeks}; fewer sets; no grind
    - **Strength endurance**: Simplify to 1–2 lighter density circuits (≤12 mins); keep technique sharp
    - **No new overloads** — this week is **about recovery, not gains**

4. **Guardrails**
    - No back-to-back intensity days
    - Keep pain ≤1–2/10 during, ≤2–3/10 next day
    - Prioritize **sleep, nutrition, and recovery habits**
    - **CRITICAL: Long run MUST remain on {athlete_profile.week_structure.long_run_day}** (just make it shorter/easier)
    - **CRITICAL: Double days (AM + PM) MUST remain on {athlete_profile.week_structure.double_days}** (just make sessions lighter/shorter)

**Output Requirements:**

- **IMPORTANT: Always start weeks on Monday** (even if Monday is a rest day). Present the week as Monday → Sunday.
- Provide a **full Week {week_number} schedule** with all {sessions} main sessions - all 7 days (Monday through Sunday) MUST be included.
- For rest days, simply state: "**Monday: Rest Day**" (or whichever day is the rest day).
- Give **explicit detail**: sets, reps, distances, paces, HR zones, and rests.
- Mark each session as **Easy / Moderate / Hard**.
- Specify **expected km per run session** so weekly total ≈ {deload_km:.0f} km.
- Add a **short rationale** for how this week allows recovery while preserving sharpness.
- End with a **weekly intensity distribution breakdown** and confirm it ✅ fits the deload balance.

**Efficiency Guidelines:**
- **Keep it concise:** Brief purpose statements (1-2 sentences), workout prescriptions with all numbers, short cooldowns.
- **Remove:** Lengthy coaching narratives, philosophical explanations, redundant examples, pain protocol adjustment sections.
- **Preserve:** All workout numbers, deload reductions, key technical cues.

**Remember: You MUST complete the full week (all 7 days) within your response. Prioritize workout prescriptions over explanatory text.**"""
