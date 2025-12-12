"""
Revised Layer 5 Prompt - HYROX Combo / Brick Session Expansion
Complete version with all improvements integrated
"""

def get_layer_5_prompt(hyrox_weights, block_objectives):
    """Layer 5 - HYROX Combo / Brick Session Expansion"""

    # Determine focus instructions based on phase
    if block_objectives.primary_goal == TrainingPhase.BASE:
        focus_instructions = (
            "Focus: BASE STATION STRENGTH & LIGHT COMPROMISE.\n"
            "- Primary purpose is to build base strength on key HYROX stations with some exposure to compromised running, "
            "not a full race simulation.\n"
            "- Station loads may be overloaded 5–15% above race weight for one or two focus stations, while keeping volumes moderate.\n"
            "- Run segments should sit easier than T1 pace (e.g. T1+20 to T1+45 sec/km) so the limiter is the station work, not the running.\n"
            "- Total compromised running (runs immediately after stations) should be modest, around 2–3 km using 400–600 m segments.\n"
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
            "Focus: DECOMPRESSION OR OPTIONAL PRACTICE.\n"
            "- This session can be skipped or kept very light.\n"
            "- If included, use very low station volumes and short runs (≤400 m) at T1+30 to T1+60 sec/km.\n"
        )

    return f"""Using Layer 0 rules, the current TrainingPhase, and the weekly skeleton from Layer 1, expand only the HYROX Combo / Brick session into a fully detailed workout.

You are designing a single HYROX combo / brick session that trains compromised running and HYROX station execution.

**Official HYROX Race Specifications:**

- Sled Push: {hyrox_weights.sled_push_kg}kg
- Sled Pull: {hyrox_weights.sled_pull_kg}kg
- Farmers Carry: {hyrox_weights.farmers_carry_kg}kg (total, split across both hands)
- Sandbag Lunges: {hyrox_weights.sandbag_lunge_kg}kg
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

- BASE: Use patterns 1-3 (simpler, focus on 1-2 stations)
- BUILD: Use patterns 2-5 (adding complexity and race patterns)
- PEAK: Use patterns 4-6 (full race simulation)
- TAPER: Use patterns 1-2 (keep it simple and clean)

For all patterns:
- At least half of all run segments in the main set must come **after** station work (compromised running).
- Do not design the entire workout as Run → Station only; the key adaptation is running after stations.
- When using patterns 5 or 6, ensure wall balls always appear as the final station in each round.

**Run distance and volume guidelines:**

- BASE:
  - Use 400–600 m run segments.
  - Total compromised running (runs immediately after stations) ≈ 2–3 km.
  - Runs usually prescribed as T1+20 to T1+45s/km.

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

- BASE: 2:00-3:00 between rounds (allow full recovery)
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
