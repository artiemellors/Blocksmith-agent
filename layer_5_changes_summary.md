# Layer 5 Prompt Revision - Summary of Changes

## Overview
This document outlines all additions and improvements made to the `get_layer_5_prompt` function for HYROX Combo/Brick session design.

## Major Additions

### 1. **100% Race Volume Reference Table** (NEW)
Added clear reference for what "race volume" means for each station:
- Sled Push: 50m
- Sled Pull: 50m
- Wall Balls: 100 reps
- Farmers Carry: 200m
- Sandbag Lunges: 100m
- SkiErg: 1000m
- RowErg: 1000m

**Why:** Eliminates ambiguity when prescribing station volumes as percentages.

---

### 2. **Enhanced Intensity Guidance** (IMPROVED)
Clarified "between T1 and T2 pace" to be more specific:
- Changed from vague "between T1 and T2"
- To explicit "5-10s/km faster than T1 pace" or "T1-5 to T1-10s/km"

**Why:** Gives AI (and athletes) concrete pace targets instead of ambiguous ranges.

---

### 3. **Pattern Selection by Phase** (NEW)
Added explicit guidance on which patterns to use in which phases:
- BASE: Use patterns 1-3 (simpler)
- BUILD: Use patterns 2-5 (adding complexity)
- PEAK: Use patterns 4-6 (full race simulation)
- TAPER: Use patterns 1-2 (simple and clean)

**Why:** Helps AI select appropriately complex patterns for the training phase.

---

### 4. **Wall Ball Volume Guidance for Patterns 5-6** (NEW)
Since patterns 5-6 always finish with wall balls, added specific rep ranges:
- BASE: 20-30 wall balls per round
- BUILD: 30-50 wall balls per round
- PEAK: 50-100 wall balls per round
- TAPER: 15-25 wall balls per round

**Why:** Ensures wall ball finishers are appropriately dosed for the phase.

---

### 5. **Rest Period Guidelines** (NEW)
Added systematic rest guidance by phase:
- BASE: 2:00-3:00 between rounds (full recovery)
- BUILD: 90s-2:00 (partial recovery)
- PEAK: 60s-90s (race-like rest)
- TAPER: 2:00-3:00 (keep it fresh)

**Why:** Critical for phase differentiation—rest periods affect work capacity development vs race simulation.

---

### 6. **Expected Total Session Duration** (NEW)
Added duration targets by phase:
- BASE: 45-60 min
- BUILD: 50-70 min
- PEAK: 60-80 min
- TAPER: 30-45 min

**Why:** Helps AI design appropriately sized sessions and prevents overly long/short workouts.

---

### 7. **Warmup Structure** (NEW)
Added explicit warmup guidance:
- 5-10 min easy running (T1+60s/km or easier)
- Dynamic mobility (hips, shoulders, thoracic spine)
- 1-2 rehearsals of primary stations at 50% effort/load
- 1-2 short run strides (100m at T1 pace)

**Why:** Ensures proper preparation for the demanding combo/brick work.

---

### 8. **Cooldown Structure** (NEW)
Added explicit cooldown guidance:
- 5-10 min easy jog/walk (T1+60s/km or slower)
- Light stretching for hips, quads, shoulders, lats

**Why:** Specifies recovery work and addresses muscle groups stressed by stations.

---

### 9. **Deload Week Guidance** (NEW)
Added complete deload week protocol:
- Reduce compromised running by ~40%
- Use patterns 1-2 only
- Station volumes at 30-40% of race volume
- Rest periods extended to 2:30-3:00
- Emphasis on movement quality and ending fresh

**Why:** Previously missing entirely—critical for proper block periodization.

---

### 10. **Pattern 6 Restriction** (STRENGTHENED)
Changed from "best reserved for PEAK blocks" to:
- "**Use this pattern ONLY in PEAK phase or late BUILD phase (weeks 3-4).**"

**Why:** Pattern 6 (Erg → Station → Run → Station → Run → Wall Balls) is extremely demanding and should be reserved for high-fitness phases only.

---

## Refinements to Existing Content

### Phase-Specific Focus Instructions (REFINED)
- **BASE:** Clarified focus is "base strength with light compromise," not full race simulation
- **BUILD:** Emphasized "threshold integration" connecting clean threshold work to HYROX specificity
- **PEAK:** Clarified as "race simulation" with mini HYROX blocks
- **TAPER:** Emphasized "sharpness & confidence" without heavy fatigue

### Compromised Running Emphasis (STRENGTHENED)
Added stronger constraint:
- "At least half of all run segments in the main set must come **after** station work"
- "Do not design the entire workout as Run → Station only"

**Why:** The key adaptation is running on fatigued legs—ensures sessions actually train this.

---

## What Was Removed/Simplified

### Removed from Original Prompt:
- Zone-based HR prescriptions (replaced with T1/T2 framework)
- "Z3-Z4" and "Z4-Z5" language (replaced with pace-based guidance)
- Vague "race-like stress" language (replaced with concrete volume/intensity targets)
- Generic "progressive exposure" statements (replaced with specific phase guidance)

**Why:** The revised prompt is more specific and actionable.

---

## Integration Notes

To integrate this into `prompts.py`:

1. Replace the existing `get_layer_5_prompt` function (lines 907-1038) with the revised version
2. Ensure `TrainingPhase` is imported at the top of the file
3. Test with a sample block generation to verify AI output quality

---

## Expected Impact

**Before:** Generic combo/brick sessions that varied mostly by load and distance
**After:** Phase-differentiated sessions with clear progression from BASE → BUILD → PEAK → TAPER

**Key Improvements:**
- ✓ Clearer pattern selection logic
- ✓ More specific rest period guidance
- ✓ Better warmup/cooldown structure
- ✓ Deload week protocol now included
- ✓ Wall ball finisher volumes specified
- ✓ Race volume reference eliminates ambiguity
- ✓ Total session duration targets prevent bloat
