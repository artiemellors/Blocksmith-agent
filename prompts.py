"""
Prompt templates for each layer of training block generation.
"""

def get_layer_0_prompt(athlete_profile, block_objectives, injury_context=""):
    """Layer 0 - Context & Global Rules"""
    hr_max = athlete_profile.physiological_params.hr_max
    t1_pace = athlete_profile.physiological_params.threshold_t1_pace
    t2_pace = athlete_profile.physiological_params.threshold_t2_pace

    injury_section = ""
    if injury_context:
        injury_section = f"\n**Current Injury Context:**\n{injury_context}\n"

    return f"""You are an elite HYROX coach and strict scheduler. You are designing training for {athlete_profile.name}, a {athlete_profile.age}-year-old hybrid athlete in a {block_objectives.primary_goal} phase.
{injury_section}
**Physiological Parameters:**

- HRmax: {hr_max} bpm
- Zones: Z1 = 60–70%, Z2 = 70–80%, Z3 = 80–88%, Z4 = 88–94%, Z5 = 94–100%
- Threshold paces: T1 = {t1_pace}/km, T2 = {t2_pace}/km

**Training Week Structure:**

- Training days: {athlete_profile.week_structure.training_days} ({athlete_profile.week_structure.rest_day} = rest)
- Main sessions: {athlete_profile.week_structure.main_sessions_per_week} total per week (2 double-days where both are "main sessions," not minis)
- Minis: exactly {athlete_profile.week_structure.mini_sessions_per_week} per week (home-only, 15–35 min, pre-assigned to specific days)
- Session time budgets: {athlete_profile.week_structure.weekday_session_time_min}–{athlete_profile.week_structure.weekday_session_time_max} min weekdays; {athlete_profile.week_structure.weekend_session_time_min}–{athlete_profile.week_structure.weekend_session_time_max} min weekends
- Equipment: Gym ({', '.join(athlete_profile.equipment.gym_equipment)}); Home ({', '.join(athlete_profile.equipment.home_equipment)})

**Run Mileage Rule:**

- Weekly run mileage = {block_objectives.running_mileage_week1}km in Week 1, then +{block_objectives.weekly_progression_percent}% per week through Week {block_objectives.block_duration_weeks}.

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
- **Mini Sessions** (home-only; use EMOM, AMRAP, Tabata, Ladder, bike steady-state)

**Design Rules (apply to every session):**

- Each main session must include: Purpose, Warm-up, 2–3 Main Blocks, Cooldown, Substitutions, Transfer Explanation, Progression Dials.
- Each mini session must include: Purpose, Structure, Assigned Day, Progression Knob.
- Occasional overload allowed only in Week {block_objectives.block_duration_weeks}.
- Strength Endurance sessions must **always include cardio modalities (run, SkiErg, RowErg, Echo bike, or bike)** within the session.
- Maintain strict alternation of hard/easy days to avoid burnout.

**Output Convention:** Follow subsequent layer prompts (Layers 1–11). Do not jump ahead."""


def get_layer_1_prompt(block_objectives):
    """Layer 1 - Week 1 Skeleton Overview"""
    return f"""Using Layer 0 rules, design the Week 1 skeleton.

**Objectives:**

- Establish baseline weekly running volume ({block_objectives.running_mileage_week1}km total mileage).
- Balance intensity: alternate hard/easy days, prevent overload.
- Cover all session archetypes (Running Quality, Running Endurance, Max Strength, Strength Endurance, HYROX Combo, Aerobic Engine/Recovery, Minis).
- Ensure **2 double-days** (both "main" sessions), plus **3 home-based mini sessions** assigned to days.

**Structure required in output:**

- Show **Tuesday → Sunday** schedule as a table with columns: *Day | Main AM | Main PM | Mini*.
- Indicate run mileage distribution to total {block_objectives.running_mileage_week1}km.
- Label each session by **archetype** only (e.g., "Run Quality – Threshold Intervals," "Strength Endurance – EMOM w/ SkiErg").
- Flag which sessions are high intensity (Z4–5) and which are low/moderate (Z1–3).

**Important constraints:**

- Avoid consecutive high-intensity days.
- Long run should anchor the weekend (90–105 min, Zone 2).
- HYROX Combo (Zone 4–5) occurs once this week.
- Minis must be **specific**: tied to actual days, home-only, 15–35 min.

**Output convention:** Just provide the **skeleton schedule** — no full session details yet. Full designs come in later layers."""


def get_layer_2_prompt(block_objectives, t1_pace, t2_pace):
    """Layer 2 - Running Sessions Expansion"""
    return f"""Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the running sessions into full detail.

**Objectives:**

- Total weekly volume: **{block_objectives.running_mileage_week1}km** (Week 1), distributed across 4 runs.
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

- Long run anchored on weekend (90–105 min, Z2).
- Easy run ≤60 min, Z2, recovery emphasis.
- Threshold/interval runs must reference both **pace zones (T1, T2)** and **HR zones** as dials.
- Where distance and time could be used, provide both (e.g., "6x1km at T1, ~{t1_pace}/km pace, HR Z3–4, 3 min jog rest").
- Include substitutions if quad pain flares (swap run → bike with matching HR zone & duration).

**Output convention:**

- Present as a **list of 4 running sessions** (not the whole week).
- Label them clearly by session type: *Run Quality 1 (Threshold Intervals)*, *Run Quality 2 (Progression Run)*, *Endurance Run (Long Z2)*, *Endurance Run (Easy Z2)*."""


def get_layer_3_prompt():
    """Layer 3 - Max Strength Sessions Expansion"""
    return """Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the Max Strength sessions into full detail.

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
- Substitute option if quad pain returns: reduce squat/deadlift intensity, swap to single-leg stability + posterior chain work.

**Output convention:**

- Present as a **list of 1–2 Max Strength sessions** (as per Week 1 skeleton).
- Label them clearly: *Strength Session 1 (Lower Body Max)*, *Strength Session 2 (Upper/Full Body Max)*."""


def get_layer_4_prompt():
    """Layer 4 - Strength Endurance Sessions Expansion"""
    return """Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand only the Strength Endurance sessions into full detail.

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
- Label clearly: *Strength Endurance Session 1 (Erg + Functional Strength)*, *Strength Endurance Session 2 (Run + HYROX Circuit)*."""


def get_layer_5_prompt():
    """Layer 5 - HYROX Combo / Brick Session Expansion"""
    return """Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand the HYROX Combo / Brick session into full detail.

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
- Label clearly: *HYROX Combo / Brick Session – Week 1*."""


def get_layer_6_prompt():
    """Layer 6 - Aerobic Engine/Recovery & Mini Sessions"""
    return """Using Layer 0 rules and the Week 1 skeleton from Layer 1, expand the Aerobic Engine/Recovery session and all 3 Mini sessions into full detail.

**Objectives:**

- **Aerobic Engine/Recovery**: Build aerobic base without running stress; promote recovery; maintain movement quality.
- **Mini Sessions**: Provide additional training stimulus at home; support specific skills (station technique, core, mobility, light aerobic); fit within 15–35 min; no equipment limitations.

**Structure required in output:**

**For Aerobic Engine/Recovery session:**

- **Purpose** (why low-intensity bike/erg work supports HYROX training).
- **Warm-up** (5–10 min ramp-up).
- **Main work** (30–50 min steady Z2 on bike or erg; technique cues; HR targets).
- **Cooldown** (mobility, stretch, breathwork).
- **Progression knob** (extend duration, add short tempo surges in later weeks).

**For each Mini session (3 total):**

- **Assigned Day** (which day of the week it falls on).
- **Purpose** (what adaptation or skill it targets).
- **Structure** (format: EMOM, AMRAP, Tabata, Ladder, steady bike, etc.; explicit exercises/reps/duration).
- **Equipment** (must be home-only: bike, wall balls, KB, bodyweight).
- **Progression knob** (how to advance in later weeks).

**Rules:**

- Minis must be **low to moderate intensity** (Z1–Z3, RPE ≤6).
- At least one mini should focus on **aerobic base** (bike, easy movement).
- At least one mini should target **HYROX station skills** (wall balls, sandbag, KB).
- At least one mini should emphasize **core/durability/mobility**.

**Output convention:**

- Present as:
  - **1 Aerobic Engine/Recovery session** (full detail).
  - **3 Mini sessions** (each with assigned day, purpose, structure, progression)."""


def get_layer_7_prompt(block_objectives):
    """Layer 7 - Assemble Full Week 1"""
    return f"""Using Layers 0–6, assemble the complete Week 1 training program.

**Objectives:**

- Produce a **day-by-day Week 1 program** with **all session detail intact** (do not shorten or summarize what was generated in Layers 2–6).
- Maintain **consistency with the skeleton plan from Layer 1**.
- Ensure **weekly running volume totals ~{block_objectives.running_mileage_week1} km**.

**Structure required in output:**

- Present as a **chronological plan (Tuesday → Sunday)**.
- For each day:
    - List **Main AM**, **Main PM (if double day)**, and **Mini (if assigned)**.
    - Under each session, include the **full detail** from its relevant layer:
        - **Purpose** (how it supports HYROX + {block_objectives.primary_goal} phase).
        - **Warm-up** (carry over from layer).
        - **Main Work** (all sets/reps/km/HR/paces/rest from layer).
        - **Cooldown**.
        - **Progression knobs** (how to evolve in later weeks).
- Do not condense. Use the original depth of detail provided in Layers 2–6.

**Rules:**

- **No detail loss** → do not replace with summaries.
- **Explicitly calculate and show total running mileage** at the end.
- Highlight session intensity (Z1–Z5) clearly.
- Keep formatting clean (headings, bullet points, spacing).

**Output convention:**

- Label clearly: *Week 1 – {block_objectives.primary_goal} Phase*.
- End with a summary line:
    - "Total run mileage = XX km (target ~{block_objectives.running_mileage_week1} km)"
    - "Total sessions = 8 main + 3 minis."

**After the full week, provide an intensity audit:**

Calculate the approximate time spent in each intensity zone across all sessions:
- Easy (Z1–Z2): % of total time
- Moderate (Z3): % of total time
- Hard (Z4–Z5): % of total time

Target: Easy = 60–70%, Moderate = ~20%, Hard = ~10%

Mark the intensity balance as ✅ (on target), ⚠️ (slightly off), or ❌ (needs adjustment)."""


def get_week_progression_prompt(week_number, previous_week_content, block_objectives):
    """Generic prompt for Week 2, 3, or 4 progression"""
    week_km = block_objectives.running_mileage_week1 * (1 + (block_objectives.weekly_progression_percent / 100)) ** (week_number - 1)

    phase_description = {
        2: "modest progression",
        3: "peak / overload (hardest week before deload)",
        4: "peak / overload (final hard week)"
    }.get(week_number, "progression")

    return f"""Using the completed Week {week_number - 1} program as the foundation, design a Week {week_number} {phase_description} that builds load in a structured and safe way.

**Previous Week Content:**
{previous_week_content[:2000]}... (see full context above)

**Progression Rules:**

1. **Running Volume**
    - Increase **total weekly mileage by ~{block_objectives.weekly_progression_percent}%** (target ≈ {week_km:.0f} km).
    - Distribute volume proportionally across sessions (do not overload a single run).

2. **Intensity Balance**
    - Week 2: Maintain **Easy = 60–70%**, **Moderate = ~20%**, **Hard = ~10%** of total time.
    - Week 3+: Allow **Easy = 55–65%**, **Moderate = 20–25%**, **Hard = 10–15%** (slightly more hard work).
    - Preserve strict alternation: no back-to-back Z4–Z5 sessions.

3. **Progression Types**
    - **Running quality sessions**: Progress by slightly longer intervals, OR additional reps, OR slightly reduced rest. **Do not progress all three at once.**
    - **Strength sessions**: Progress either load, volume, or movement complexity — **not all at once**.
    - **Strength endurance**: Increase **time-under-tension or conditioning element** (e.g., longer EMOMs, extended bike/row/run blocks).

4. **Guardrails**
    - Pain ≤2/10 during and ≤3/10 next day → if exceeded, cut or swap.
    - No back-to-back **hard (Z4–Z5)** sessions.
    - Running surfaces = flat/soft or track where possible.

**Output Requirements:**

- Provide a **full Week {week_number} schedule (Tue → Sun)**.
- Include all **main sessions + minis** with explicit structure (sets, reps, paces, HR zones, rests).
- Indicate expected **km per run session** so weekly total = ~{week_km:.0f} km.
- Tag each session as **Easy / Moderate / Hard**.
- Provide a short **note on progression rationale** for each session (e.g., "increased intervals from 4x6min → 5x6min").
- End with an **intensity distribution check (percentages)** and a ✅/⚠️/❌ rating."""


def get_deload_prompt(week_number, peak_week_content, block_objectives):
    """Layer 10 - Deload Week"""
    peak_km = block_objectives.running_mileage_week1 * (1 + (block_objectives.weekly_progression_percent / 100)) ** (block_objectives.block_duration_weeks - 1)
    deload_km = peak_km * 0.65  # 30-40% reduction

    return f"""Using the Week {block_objectives.block_duration_weeks} Peak / Overload week as the foundation, design a Deload Week (Week {week_number}) that reduces training stress to promote recovery and adaptation, while maintaining movement quality and rhythm.

**Peak Week Content:**
{peak_week_content[:2000]}... (see full context above)

**Deload Rules:**

1. **Running Volume**
    - Reduce **weekly mileage by ~30–40%** compared to Week {block_objectives.block_duration_weeks} (target ≈ {deload_km:.0f} km).
    - Keep **all 4 runs**, but shorten distances and/or reduce interval reps.

2. **Intensity Distribution**
    - Global target:
        - **Easy = 70–80%**
        - **Moderate = 15–20%**
        - **Hard = ≤5%** (keep touches of intensity sharp but very short).

3. **Strength & Strength Endurance**
    - **Strength**: Reduce load to ~60–70% of Week {block_objectives.block_duration_weeks}; fewer sets; no grind.
    - **Strength endurance**: Simplify to 1–2 lighter density circuits (≤12 mins); keep technique sharp.
    - **No new overloads** — this week is **about recovery, not gains**.

4. **Mini Sessions**
    - Maintain **2–3 minis (12–20 mins)**, but all should be **easy Z2 or technique-focused** (bike spin, mobility, light KB flow, easy wall balls).

5. **Guardrails**
    - No back-to-back intensity days.
    - Keep pain ≤1–2/10 during, ≤2–3/10 next day.
    - Prioritize **sleep, nutrition, and recovery habits**.

**Output Requirements:**

- Provide a **full Week {week_number} schedule (Tue → Sun)** with all main + mini sessions.
- Give **explicit detail**: sets, reps, distances, paces, HR zones, and rests.
- Mark each session as **Easy / Moderate / Hard**.
- Specify **expected km per run session** so weekly total ≈ {deload_km:.0f} km.
- Add a **short rationale** for how this week allows recovery while preserving sharpness.
- End with a **weekly intensity distribution breakdown** and confirm it ✅ fits the deload balance."""


def get_layer_11_prompt(all_weeks_content, athlete_profile, block_objectives):
    """Layer 11 - Full Block Artefact Assembly"""
    return f"""Using all previous layers (0–10), assemble a single artefact titled:

*HYROX {block_objectives.block_duration_weeks}+1 Training Block – {block_objectives.primary_goal} Phase ({athlete_profile.name})*

**Rules:**

- Include Athlete Profile, Parameters, Guardrails, Block Logic.
- Present Weeks 1–{block_objectives.block_duration_weeks + 1} chronologically, with every session fully detailed.
- Append audits after each week (mileage, intensity distribution, ✅/⚠️/❌).
- End with block summary: mileage progression, intensity splits, adaptations targeted.
- Do not summarise, reword, or omit detail.
- Copy verbatim from previous layer outputs.

**Full Week Content to Include:**
{all_weeks_content[:3000]}... (see all weeks in full context)

**Output:** Complete *{block_objectives.block_duration_weeks}+1 Week Training Block Artefact*."""
