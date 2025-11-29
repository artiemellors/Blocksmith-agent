"""
Prompt templates for each layer of training block generation.
Version 2: Philosophy-guided with realistic work capacity constraints.
"""

def get_layer_0_prompt(athlete_profile, block_objectives, injury_context=""):
    """Layer 0 - Context & Global Rules"""
    from models import HyroxWeights

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
    perf = athlete_profile.performance_benchmarks
    has_race_data = (block_objectives.target_race_date or block_objectives.race_type or
                     perf.last_hyrox_date or perf.last_hyrox_time or
                     perf.goal_hyrox_time or perf.races_completed > 0)

    if has_race_data:
        race_lines = []
        if block_objectives.target_race_date:
            race_lines.append(f"- Target race: {block_objectives.target_race_date}")
            if block_objectives.weeks_to_race:
                race_lines.append(f"- Weeks to race: {block_objectives.weeks_to_race}")
        if block_objectives.race_type:
            race_lines.append(f"- Race type: {block_objectives.race_type}")
        if perf.last_hyrox_date and perf.last_hyrox_time:
            race_lines.append(f"- Recent best: {perf.last_hyrox_time} ({perf.last_hyrox_date})")
        elif perf.last_hyrox_time:
            race_lines.append(f"- Recent best: {perf.last_hyrox_time}")
        if perf.goal_hyrox_time:
            race_lines.append(f"- Goal time: {perf.goal_hyrox_time}")
        if perf.races_completed > 0:
            race_lines.append(f"- Races completed: {perf.races_completed}")

        race_section = "\n**Race Context:**\n\n" + "\n".join(race_lines) + "\n"

    # Build performance profile section
    performance_profile = ""
    if perf.strong_stations or perf.weak_stations:
        profile_lines = []
        if perf.strong_stations:
            stations_str = ", ".join(perf.strong_stations)
            profile_lines.append(f"- Strong stations: {stations_str}")
        if perf.weak_stations:
            stations_str = ", ".join(perf.weak_stations)
            profile_lines.append(f"- Limiter stations: {stations_str}")

        performance_profile = "\n**Performance Profile:**\n\n" + "\n".join(profile_lines) + "\n"

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

**Movement Duration Estimates (for realistic programming):**

At race weight, typical durations for intermediate HYROX athlete:
- Sled Push {hyrox_weights.sled_push_kg}kg, 50m: 60-120 seconds
- Sled Pull {hyrox_weights.sled_pull_kg}kg, 50m: 45-90 seconds
- Wall Balls {hyrox_weights.wall_ball_kg}kg: ~2-3 reps/second (100 reps = 30-50s)
- RowErg 200m max effort: 40-50 seconds
- RowErg 1000m: 3:15-4:00
- Run 800m (post-station): 3:30-4:30
- Run 1km (post-station): 4:30-5:30

**Week 1 Calibration Principle:**

Week 1 is a BASELINE week - sessions should be challenging but clearly achievable. Better to undershoot and add volume in Week 2 than overshoot and force deload.

**Critical Prescription Format:**

- Sled push/pull: ALWAYS specify "{hyrox_weights.sled_push_kg}kg" or "{hyrox_weights.sled_pull_kg}kg" explicitly
- Farmers carry: ALWAYS specify "{hyrox_weights.farmers_carry_kg[0]}kg per hand" or "2x{hyrox_weights.farmers_carry_kg[0]}kg"
- Sandbag: ALWAYS specify "{hyrox_weights.sandbag_kg}kg"
- Wall balls: ALWAYS specify "{hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m target"

"""

    return f"""You are an elite HYROX coach and strict scheduler. You are designing training for {athlete_profile.name}, a {athlete_profile.age}-year-old hybrid athlete in a {block_objectives.primary_goal} phase.
{injury_section}{race_section}{performance_profile}{hyrox_spec_section}
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

**Run Mileage Rule:**

- Weekly run mileage = {block_objectives.running_mileage_week1}km in Week 1, then +{block_objectives.weekly_progression_percent}% per week through Week {block_objectives.block_duration_weeks}

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

    return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the running sessions into full detail.

**CRITICAL CONTEXT:**

Brick sessions (Layer 5) provide race-specific running practice but do NOT replace dedicated threshold development. Design true running quality sessions here - these are CLEAN running sessions with proper warm-up, focused effort at target zones, and adequate recovery. Not compromised running. Not fatigued running. Pure physiological development.

**Objectives:**

- Total weekly volume: **{block_objectives.running_mileage_week1}km** (Week 1), distributed across {runs} runs
- Gradual build: +{block_objectives.weekly_progression_percent}% mileage per week in following weeks
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


def get_layer_3_prompt():
    """Layer 3 - Max Strength Sessions Expansion"""
    return """Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the Max Strength sessions into full detail.

**Objectives:**

- Build absolute strength in compound lifts → improved economy, resilience, and transfer into HYROX strength endurance
- Focus on low rep, high quality lifts
- Keep sessions ≤75 min
- No overlapping same-day fatigue with hard run sessions

**Structure required in output:**

For each strength session, include:

- **Purpose** (why it's in the program)
- **Warm-up** (mobility, activation, ramp-up sets)
- **Main lifts** (2–3 compound lifts: squat, deadlift, bench/press, pull-up variants). Explicit sets × reps × %1RM or RPE
- **Accessory work** (1–2 short blocks targeting weak links or HYROX transfer — e.g., core stability, unilateral strength, grip)
- **Cooldown** (mobility, breathing reset, stretch priority areas)
- **Progression knob** (e.g., increase load by 2.5–5%, add 1 set, tighten rest)

**Rules:**

- Use rep schemes in the **3–6 rep** range for compounds
- Accessories may include unilateral lifts (lunges, RDLs), core, or posterior chain balance
- No more than 4 total main compound lifts per session
- Keep rest long (2–3 min for heavy compounds, 60–90s for accessories)

**Output convention:**

- Present as a **list of 1–2 Max Strength sessions** (as per Week 1 skeleton)
- Label them clearly: *Strength Session 1 (Lower Body Max)*, *Strength Session 2 (Upper/Full Body Max)*"""


def get_layer_4_prompt(hyrox_weights):
    """Layer 4 - Strength Endurance Sessions Expansion"""
    return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the Strength Endurance sessions into full detail.

**Official HYROX Station Weights (Use These Exactly):**

- Sled Push: {hyrox_weights.sled_push_kg}kg
- Sled Pull: {hyrox_weights.sled_pull_kg}kg
- Wall Balls: {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m
- Sandbag: {hyrox_weights.sandbag_kg}kg
- Farmers Carry: 2×{hyrox_weights.farmers_carry_kg[0]}kg

**Exercise Selection Philosophy:**

**Priority Order:**
1. Target muscle groups effectively
2. Use HYROX stations when they're the best tool for the job
3. Freely substitute superior alternatives when appropriate
4. Quality of training stimulus > literal race simulation

**Example:** A trap bar deadlift or KB swing might build sled-pulling capacity better than doing sleds twice a week. Bulgarian split squats might develop quad endurance more effectively than sandbag lunges in certain contexts.

**Target muscle groups and movement patterns, not a predetermined exercise list.**

**Realistic Work Capacity Prescription:**

**EMOM Guidelines:**
- Work windows: 45-90 seconds for realistic completion
- Don't combine max-effort cardio + heavy strength in short windows

✅ **REALISTIC:**
- "Sled push {hyrox_weights.sled_push_kg}kg 25m, rest remainder of 90s"
- "RowErg 250m moderate effort, rest remainder of 2 min"
- "Wall balls {hyrox_weights.wall_ball_kg}kg, 20 reps, rest remainder of 90s"

❌ **UNREALISTIC:**
- "Sled push {hyrox_weights.sled_push_kg}kg 40m + RowErg 200m max effort in 2 min"
- "Wall balls 50 reps + 400m run in 3 min"

**EMOM Structure Options:**
- Single movement, rotating loads/distances
- Alternating movements every other minute
- Density blocks (e.g., EMOM 12: odd minutes sled, even minutes row)

**Circuit/Chipper Guidelines:**
- Emphasize quality over speed
- Mix complementary movement patterns
- Use time caps to prevent grinding
- Include strategic rest periods between rounds

**Progression Vectors (choose 1-2, not all three):**
1. **Density:** Reduce rest between efforts
2. **Volume:** More rounds/reps at same intensity
3. **Load:** Heavier resistance at same volume

**Objectives:**

- Build the ability to sustain submaximal strength under fatigue
- Improve work capacity and efficiency in HYROX-specific stations (sleds, carries, wall balls, lunges, burpees)
- Force adaptation by pairing **strength movements with cardio intervals** to simulate race demands
- Time cap: 60–75 min

**Structure required in output:**

For each strength endurance session, include:

- **Purpose** (clear link to HYROX transfer)
- **Warm-up** (mobility, activation, light machine work)
- **Main Blocks** (2–3 blocks using EMOMs, AMRAPs, circuits, or interval pairings of cardio + functional strength). Must include at least one machine (run, ski, row, echo/bike) per block. Explicit reps/sets/duration, intensity targets (HR zone, RPE, or pace)

  For EVERY station exercise, specify:
  - Exact weight in kg (race weight if using HYROX stations)
  - Target height for wall balls
  - Distance or reps
  - Rest periods

  Example: "Sled Push: {hyrox_weights.sled_push_kg}kg, 40m, 90s rest"
  Example: "Wall Balls: {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m, 20 reps"

- **Cooldown** (walk, flush, mobility, breathing)
- **Progression knob** (volume, density, load, or machine interval length)

**Rules:**

- Keep heart rate between **upper Zone 2 → mid Zone 4**, depending on block
- Alternate knee-dominant vs. hip-dominant strength movements to manage fatigue
- Each block should last **8–20 minutes**
- Sessions should balance load: one more *sled/carry/burpee focused*; one more *wall ball/lunge/erg focused*
- Explicit substitutions if running volume needs capping (swap to bike/erg)

**Week 1 Context:**
This is Week 1 - design sessions that build work capacity foundation, allow athlete to learn movement patterns, and don't overreach with volume or intensity.

**Output convention:**

- Present as a **list of 2 Strength Endurance sessions** (as per Week 1 skeleton)
- Label clearly: *Strength Endurance Session 1 (Erg + Functional Strength)*, *Strength Endurance Session 2 (Run + HYROX Circuit)*"""


def get_layer_5_prompt(hyrox_weights):
    """Layer 5 - HYROX Combo / Brick Session Expansion"""
    return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand the HYROX Combo / Brick session into full detail.

**Official HYROX Race Specifications:**

- Sled Push: {hyrox_weights.sled_push_kg}kg, 50m in race
- Sled Pull: {hyrox_weights.sled_pull_kg}kg, 50m in race
- Wall Balls: {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m, 100 reps in race
- Sandbag: {hyrox_weights.sandbag_kg}kg, 100m in race
- Farmers Carry: 2×{hyrox_weights.farmers_carry_kg[0]}kg, 200m in race

**Purpose:**

Build race-specific adaptations WITHOUT replicating full race stimulus every week.

**Target Adaptations:**
- Running on compromised/fatigued legs
- Managing HR spikes from station work
- Transition efficiency and mental resilience
- Race-specific skill development

**Key Principle:** Progressive exposure to race-like stress, not maximum stimulus weekly.

**CRITICAL DISTINCTION:**

Brick sessions ≠ Threshold development

These sessions use threshold paces (T1/T2) but are NOT the same as dedicated threshold running:
- HR is spiking from stations
- Running form is compromised
- Can't sustain pure threshold physiological stimulus
- Purpose: Learn to run on tired legs, not develop lactate threshold

Dedicated threshold sessions (Layer 2) provide the actual physiological development.

**Variation Tools:**

**Run Distances:**
- 400-600m: Emphasizes station density, shorter runs allow more station volume
- 800m: Balanced run/station split, moderate fatigue management
- 1km: Race-specific distance, higher running emphasis

**Station Volumes:**
- 25-50% of race work: Technique focus, building movement patterns
- 50-75% of race work: Quality with moderate volume
- 75-100% of race work: Near race-level demands, high fatigue

**Round Structure:**
- Single station + run: Classic brick format, can repeat 4-6 rounds
- Paired stations + run: Two stations back-to-back, then run (higher density)
- Sequential station blocks: 3-4 stations, then longer run (very high density)

**Rest/Transitions:**
- Timed rest (90s-2min): Builds work capacity, allows HR recovery
- Active rest (20-30s): Moderate density, some recovery
- Minimal transitions (<10s): Race-specific, very high demand

**Week 1 Guidance:**
- Shorter runs (400-600m) OR moderate (800m)
- 50-75% of race work allows quality focus without excessive fatigue
- Timed rest (90-120s) appropriate for building foundation

**Realistic Effort Distribution:**

**Most rounds:** Z3-Z4 (controlled hard effort)
- HR: 155-170 bpm
- Sustainable pace on runs
- Quality movement on stations

**1-2 rounds (optional):** Z4-Z5 (race-pace intensity)
- HR: 168-182 bpm
- Near-maximal effort
- Tests mental resilience

**Week 1 Consideration:** Emphasize Z3-Z4 effort. Z5 work can be introduced later in block.

**Objectives:**

- Replicate HYROX race demands (compromised running, station transitions, Zone 4–5 intensity)
- Train lactate tolerance and clearance while fatigued
- Practice pacing, breathing, and station efficiency under pressure

**Structure required in output:**

For the HYROX Combo / Brick session, include:

- **Purpose** (link to specific HYROX race demands)
- **Warm-up** (run prep, machine primer, dynamic mobility)
- **Main Blocks** (2–3 blocks combining running intervals with HYROX stations; examples: Run → Sled Push/Pull, Run → Burpee Broad Jumps, Run → Wall Balls). Explicit distances, reps, paces, heart rate targets (Zone 4–5), RPE guidance, and rest.

  For EVERY station exercise, specify:
  - Exact race weight in kg
  - Exact race distance or reps
  - Target height for wall balls

  Example: "Run 800m → Sled Push {hyrox_weights.sled_push_kg}kg for 2×25m → 2 min rest"
  Example: "Run 1km → Wall Balls {hyrox_weights.wall_ball_kg}kg to {hyrox_weights.wall_ball_target_m}m, 50 reps"

- **Cooldown** (HR drop, mobility, walking, breathing drills)
- **Progression knob** (increase run distance per station, reduce rest, add rounds, or increase station volume)

**Rules:**

- Always include **running + at least 2 HYROX stations per block**
- Target total work time **45–60 minutes**
- Sessions should simulate cumulative fatigue: **shorter runs, higher station volume** in early blocks; **longer runs, reduced volume** in later blocks
- Keep intensity high (Zone 4–5) but with recoverable sets — do not "redline" early
- Provide substitutions if running load needs managing (swap to bike/erg)

**Output convention:**

- Deliver as a **single HYROX Combo / Brick session** (for Week 1)
- Label clearly: *HYROX Combo / Brick Session – Week 1*"""


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

    week_km = block_objectives.running_mileage_week1 * (1 + (block_objectives.weekly_progression_percent / 100)) ** (week_number - 1)
    sessions = athlete_profile.week_structure.main_sessions_per_week
    training_days = athlete_profile.week_structure.get_training_days_range()
    runs = athlete_profile.week_structure.runs_per_week
    hyrox_weights = HyroxWeights.get_weights(block_objectives.race_type) if block_objectives.race_type else None

    phase_description = {
        2: "modest progression",
        3: "peak / overload (hardest week before deload)",
        4: "peak / overload (final hard week)"
    }.get(week_number, "progression")

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
    - Increase **total weekly mileage by ~{block_objectives.weekly_progression_percent}%** (target ≈ {week_km:.0f} km)
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

    peak_km = block_objectives.running_mileage_week1 * (1 + (block_objectives.weekly_progression_percent / 100)) ** (block_objectives.block_duration_weeks - 1)
    deload_km = peak_km * 0.65  # 30-40% reduction
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
