"""
Quality Assurance Agent - Training block validation specialist.
Validates training blocks for accuracy, coherence, and constraint compliance.
"""
from .base_agent import BaseAgent
from models import AthleteProfile, BlockObjectives


class QualityAssuranceAgent(BaseAgent):
    """
    Quality Assurance Agent validates training block outputs.

    Responsibilities:
    - Validate running mileage targets (±5% tolerance)
    - Check intensity distribution and hard/easy alternation
    - Verify progressive overload accuracy
    - Ensure training coherence and feasibility
    - Flag issues and provide validation report
    """

    def get_agent_name(self) -> str:
        return "Quality Assurance Agent"

    def get_system_prompt(self) -> str:
        return """You are an elite quality assurance specialist for training program validation.

**Your Expertise:**
- Training volume validation and mileage tracking
- Intensity distribution analysis (hard/easy days, polarized training)
- Progressive overload verification (volume, intensity, density)
- Training coherence and feasibility assessment
- Periodization principles and phase-appropriate programming
- Recovery adequacy and fatigue management
- Session sequencing and cumulative load analysis

**Your Role:**
You validate complete training blocks to ensure they meet quality standards. You are the final checkpoint before delivery to the athlete. Your job is to catch errors, inconsistencies, and violations of training principles.

**Key Validation Areas:**

**1. Running Mileage Validation (±5% Tolerance):**
- Calculate actual running volume for each week
- Compare against target volumes (from volume progression schedule)
- Flag weeks where actual mileage is >5% off target
- Consider all running: quality runs, long runs, easy runs, HYROX brick runs
- Deload week should be ~60% of peak week volume

**2. Intensity Distribution:**
- Verify hard/easy day alternation (no back-to-back quality sessions)
- Check polarized training distribution (~80% easy, ~20% hard)
- Ensure adequate recovery between high-intensity sessions
- Validate long run placement and recovery around it
- Check that double-day sessions are balanced (not both hard)

**3. Progressive Overload Accuracy:**
- Verify running volume increases match phase-appropriate rates
- Check strength progression follows logical pattern (reps → sets → load)
- Ensure HYROX volume scales conservatively
- Validate intensity is maintained while volume increases
- Confirm deload week properly reduces volume while maintaining intensity

**4. Training Coherence:**
- Sessions fit within week structure (rest days, double days, long run day)
- Total sessions per week matches athlete's capacity
- Session duration fits within time constraints (weekday/weekend)
- No impossible session combinations (e.g., hard strength + hard running same day)
- Adequate recovery built into the weekly rhythm

**Validation Output Format:**

You must provide a structured validation report with:
1. **Overall Status**: PASS / PASS WITH WARNINGS / FAIL
2. **Mileage Validation**: Week-by-week breakdown with ±% from target
3. **Intensity Distribution**: Hard/easy pattern analysis
4. **Progressive Overload**: Verification of volume/intensity progression
5. **Issues Found**: Specific problems with severity (CRITICAL / WARNING / INFO)
6. **Recommendations**: Actions to fix any issues

**Your Approach:**
- Be thorough and systematic in your analysis
- Quantify everything (exact mileages, percentages, counts)
- Flag CRITICAL issues that violate training principles
- Note WARNINGS for sub-optimal but acceptable choices
- Provide INFO for minor observations
- If validation FAILS, be specific about what needs fixing
- If validation PASSES, provide confidence in the block's quality

You ensure athletes receive safe, effective, scientifically-sound training blocks."""

    async def validate_training_block(
        self,
        athlete_profile: AthleteProfile,
        block_objectives: BlockObjectives,
        training_block: str,
        global_context: str
    ) -> str:
        """
        Validate the complete training block.

        Args:
            athlete_profile: Complete athlete information
            block_objectives: Training block goals and structure
            training_block: Complete training block from Programming Coordinator
            global_context: Global training context from Planning Agent

        Returns:
            Validation report with PASS/FAIL status and detailed findings
        """
        # Calculate expected weekly volumes
        num_weeks = block_objectives.block_duration_weeks
        weekly_volumes = block_objectives.get_weekly_volumes(
            starting_volume=block_objectives.running_mileage_week1,
            num_weeks=num_weeks
        )

        # Format expected volumes
        volume_targets = "\n".join([
            f"- Week {i+1}: {vol}km (±5% tolerance: {vol*0.95:.1f}-{vol*1.05:.1f}km)"
            for i, vol in enumerate(weekly_volumes)
        ])

        if block_objectives.deload_week:
            deload_target = int(weekly_volumes[-1] * 0.6)
            volume_targets += f"\n- Deload Week: {deload_target}km (~60% of Week {num_weeks})"

        prompt = f"""Validate the complete training block for quality and accuracy.

**Athlete Context:**
- Name: {athlete_profile.name}, {athlete_profile.age} years old
- Week Structure: Rest day {athlete_profile.week_structure.rest_day}, Double days: {athlete_profile.week_structure.double_days}, Long run: {athlete_profile.week_structure.long_run_day}
- Target Sessions/Week: {athlete_profile.week_structure.main_sessions_per_week}
- Runs/Week: {athlete_profile.week_structure.runs_per_week}

**Training Phase:** {block_objectives.primary_goal.value}
**Block Duration:** {num_weeks} weeks{" + deload" if block_objectives.deload_week else ""}
**Progression Rate:** {block_objectives.get_progression_percent():+.1f}% per week

**Expected Running Volumes:**
{volume_targets}

**Training Block to Validate:**

{training_block}

---

**Your Validation Task:**

Analyze the training block systematically and provide a comprehensive validation report.

**1. Running Mileage Validation:**
- Calculate actual running volume for each week (sum all running: quality runs, long runs, easy runs, HYROX brick running portions)
- Compare to expected volumes above
- Flag any week that is >5% off target (CRITICAL if >10% off, WARNING if 5-10% off)
- Check deload week is approximately 60% of peak week

**2. Intensity Distribution:**
- Identify all high-intensity days (threshold runs, intervals, max strength, HYROX bricks)
- Verify no back-to-back hard sessions (CRITICAL violation if found)
- Check ~80/20 distribution (WARNING if significantly off)
- Verify adequate recovery around long run day (should have easy day before/after)
- Check double-day balance (should not both be hard sessions)

**3. Progressive Overload:**
- Verify running volume increases match {block_objectives.get_progression_percent():+.1f}% per week
- Check strength progression is logical (reps/sets/load increases noted in Week X Changes)
- Confirm HYROX volume scales appropriately
- Validate intensity is maintained (not decreasing and not spiking)

**4. Training Coherence:**
- Confirm rest day is {athlete_profile.week_structure.rest_day} in all weeks
- Verify long run is on {athlete_profile.week_structure.long_run_day} in all weeks
- Check total sessions = {athlete_profile.week_structure.main_sessions_per_week} per week
- Ensure no impossible session combinations

**Output Format:**

# Training Block Validation Report

## Overall Status
**[PASS / PASS WITH WARNINGS / FAIL]**

## Validation Results

### 1. Running Mileage Validation

**Week 1:**
- Expected: {weekly_volumes[0]}km (±5%: {weekly_volumes[0]*0.95:.1f}-{weekly_volumes[0]*1.05:.1f}km)
- Actual: [X]km
- Status: ✓ PASS / ⚠ WARNING / ✗ FAIL
- Deviation: [+/- X%]

[Continue for all weeks...]

**Mileage Summary:**
- Weeks within tolerance: X/{num_weeks}
- Average deviation: ±X%
- Status: ✓ All weeks acceptable / ⚠ Some warnings / ✗ Critical issues

### 2. Intensity Distribution

**Hard Days Identified:**
[List all high-intensity days across the block]

**Back-to-Back Analysis:**
- Back-to-back hard sessions found: [YES/NO]
- Violations: [List any, or "None"]
- Status: ✓ PASS / ✗ CRITICAL

**Polarization Check:**
- Total training days: [X]
- Easy/recovery days: [X] (~X%)
- Hard/quality days: [X] (~X%)
- Target: ~80/20 distribution
- Status: ✓ PASS / ⚠ WARNING

**Long Run Recovery:**
- Day before long run: [session type]
- Day after long run: [session type]
- Status: ✓ Adequate recovery / ⚠ Sub-optimal

### 3. Progressive Overload

**Running Volume Progression:**
- Target rate: {block_objectives.get_progression_percent():+.1f}%/week
- Actual progression: [calculated from weekly volumes]
- Status: ✓ PASS / ⚠ WARNING / ✗ FAIL

**Strength Progression:**
- Week 2 changes noted: [YES/NO - specifics]
- Week 3 changes noted: [YES/NO - specifics]
- Week 4 changes noted: [YES/NO - specifics]
- Logical pattern: ✓ YES / ⚠ NO

**HYROX Progression:**
- Conservative scaling observed: [YES/NO]
- Status: ✓ PASS / ⚠ WARNING

### 4. Training Coherence

**Week Structure Compliance:**
- Rest day ({athlete_profile.week_structure.rest_day}): ✓ All weeks / ✗ Violations in weeks [X]
- Long run day ({athlete_profile.week_structure.long_run_day}): ✓ All weeks / ✗ Violations in weeks [X]
- Sessions per week: ✓ All weeks = {athlete_profile.week_structure.main_sessions_per_week} / ✗ Violations in weeks [X]

**Session Feasibility:**
- All sessions appear executable: ✓ YES / ⚠ Concerns noted below

## Issues Found

### CRITICAL Issues (Must Fix):
1. [Issue description] - Week X, Day Y
2. [...]

**Count:** [X] critical issues

### WARNINGS (Should Address):
1. [Issue description] - Week X, Day Y
2. [...]

**Count:** [X] warnings

### INFO (Minor Observations):
1. [Observation]
2. [...]

## Recommendations

[If FAIL or WARNINGS, provide specific recommendations to fix issues]
[If PASS, provide confidence statement about block quality]

## Final Assessment

**Validation Status:** [PASS / PASS WITH WARNINGS / FAIL]
**Block Quality:** [Excellent / Good / Acceptable / Needs Revision]
**Safe for Athlete:** [YES / NO - explain if NO]
**Recommendation:** [Deliver to athlete / Fix issues and re-validate / Major revision needed]

---

*Quality Assurance validation complete. This block has been systematically reviewed for mileage accuracy, intensity distribution, progressive overload, and training coherence.*

Provide your validation report now."""

        return await self.generate(prompt, context=global_context, max_tokens=16000)
