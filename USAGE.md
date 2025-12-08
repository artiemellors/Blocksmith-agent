# Blocksmith Usage Guide

## Step-by-Step Workflow

### First Time Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

3. **Verify installation**
   ```bash
   python main.py version
   ```

### Creating Your First Training Block

#### Step 1: Create Configuration File

**Option A: Simple Text Format (Recommended)**

```bash
python main.py create-config-simple my_first_block.txt
```

**Option B: YAML Format**

```bash
python main.py create-config my_first_block.yaml
```

Both create a template configuration file. The text format uses simple `key=value` pairs and is easier to edit.

#### Step 2: Customize Your Configuration

Edit your config file (`.txt` or `.yaml`) with your details:

**Required Fields:**
- **Athlete**: Name, age
- **Physiological Parameters**: HR max, T1 threshold pace, T2 threshold pace (mm:ss format)
- **Block Objectives**: Primary goal (BUILD, PEAK, Base building, etc.), starting weekly mileage

**Training Week Structure (All Optional - Defaults Provided):**
- `rest_days`: Which day(s) to rest (default: Monday) - can specify multiple: "Monday, Wednesday"
- `total_sessions_per_week`: Total sessions per week (default: 8)
- `double_days`: Days with AM + PM sessions (default: Wednesday, Saturday)
- `runs_per_week`: How many sessions are runs (default: 4)
- `long_run_day`: Which day has the long run (default: Sunday)

**Other Optional But Recommended:**
- `active_injuries`: List any current injuries
- `specific_focus_areas`: 2-4 areas to emphasize
- `previous_training_block_file`: Path to your last block for continuity
- `additional_context`: Any special instructions

#### Step 3: Generate Your Block

```bash
python main.py generate --config my_first_block.txt
```
(or `.yaml` if you chose YAML format)

The system will:
1. Load and **validate** your configuration (checks for logical errors)
2. Show a summary and ask for confirmation
3. Generate each layer sequentially (takes 5-10 minutes)
4. Save the complete block and intermediate layers

**If validation fails**, you'll see a clear error message explaining what's wrong and how to fix it.

#### Step 4: Review Your Block

Find your results in the `output/` directory:
- `complete_training_block.md` - Your full training block
- `layer_*.md` - Individual layer outputs (for reference)
- `generation_summary.md` - Generation log

## Common Use Cases

### Use Case 1: Starting Fresh (No Previous Block)

**Simple Text Format (.txt):**

```text
# my_config.txt
name=John Doe
age=35

hr_max=185
threshold_t1_pace=4:45
threshold_t2_pace=4:25

active_injuries=

# Training Week Structure (using defaults, can customize)
rest_days=Monday
total_sessions_per_week=8
double_days=Wednesday, Saturday
runs_per_week=4
long_run_day=Sunday

primary_goal=BUILD
running_mileage_week1=35
weekly_progression_percent=10
block_duration_weeks=4
deload_week=yes

previous_training_block_file=
```

**YAML Format (.yaml):**

```yaml
# my_config.yaml
athlete:
  name: "John Doe"
  age: 35

physiological_parameters:
  hr_max: 185
  threshold_t1_pace: "4:45"
  threshold_t2_pace: "4:25"

injury_information:
  active_injuries: []

training_week_structure:
  rest_days: "Monday"
  total_sessions_per_week: 8
  double_days: "Wednesday, Saturday"
  runs_per_week: 4
  long_run_day: "Sunday"

block_objectives:
  primary_goal: "BUILD"
  running_mileage_week1: 35
  weekly_progression_percent: 10
  block_duration_weeks: 4
  deload_week: true

previous_training_block_file: null
```

Generate:
```bash
python main.py generate --config my_config.txt
```
(or `.yaml` if using YAML)

### Use Case 2: Building on Previous Block

1. Save your previous block as `previous_block.md`

2. Update your configuration (showing text format):
```text
# my_config.txt
name=John Doe
age=35

hr_max=185
threshold_t1_pace=4:40  # Updated - faster!
threshold_t2_pace=4:20  # Updated

active_injuries=

# Adjust training structure for peak phase
rest_days=Monday
total_sessions_per_week=7  # Reduced from 8
double_days=Saturday  # Only 1 double day (7 sessions - 6 training days = 1)
runs_per_week=4
long_run_day=Sunday

primary_goal=PEAK  # Changed from BUILD to PEAK
running_mileage_week1=45  # Increased from 35
weekly_progression_percent=8  # Slower progression for peak phase
block_duration_weeks=3  # Shorter block
deload_week=yes

previous_training_block_file=previous_block.md  # Added!
additional_context=This is a race-specific block leading into competition
```

Generate:
```bash
python main.py generate --config my_config.txt --output-dir output/peak_block
```

### Use Case 3: Returning After Injury

```text
# my_config.txt
name=Jane Smith
age=40

hr_max=182
threshold_t1_pace=5:00  # Conservative estimate
threshold_t2_pace=4:40

# Injury management
active_injuries=right quad strain
pain_threshold_during=2
pain_threshold_next_day=3
soreness_cutoff_hours=36
volume_reduction_percent=30  # More conservative

# Conservative training structure - more rest days
rest_days=Monday, Wednesday, Friday  # 3 rest days for recovery
total_sessions_per_week=4  # Low volume (4 training days, 4 sessions, no doubles)
double_days=  # No double days during injury recovery
runs_per_week=2  # Only 2 runs, rest are strength/cross-training
long_run_day=Sunday

primary_goal=Return to training
running_mileage_week1=25  # Low starting volume
weekly_progression_percent=8  # Slower progression
block_duration_weeks=4
deload_week=yes
specific_focus_areas=gradual return to running, maintain upper body strength

additional_context=Prioritize injury recovery. Be very conservative with running volume. Include more bike/erg substitutions.
```

**Note the conservative training structure:**
- 3 rest days (Mon, Wed, Fri) = only 4 training days
- 4 sessions total = 1 per training day (no double days)
- Only 2 runs per week (others are strength/cross-training)
- Validation will confirm: 4 sessions ÷ 4 training days = 0 double days needed ✅

Generate:
```bash
python main.py generate --config my_config.txt
```

## Advanced Options

### Custom Output Directory

Organize blocks by date or phase:
```bash
python main.py generate --config my_config.yaml --output-dir blocks/2025_01_rebuild
```

### Use Different Model

For faster/cheaper generation (less detailed):
```bash
python main.py generate --config my_config.yaml --model claude-haiku-4-20250514
```

For highest quality (more expensive):
```bash
python main.py generate --config my_config.yaml --model claude-opus-4-20250514
```

### Skip Intermediate Layer Saves

If you only want the final block:
```bash
python main.py generate --config my_config.yaml --no-save-layers
```

## Understanding the Output

### Complete Training Block Structure

```
HYROX 4+1 Training Block – BUILD Phase (Arthur Mellors)

├── Athlete Profile
│   ├── Physiological Parameters
│   ├── Training Week Structure
│   ├── Equipment
│   └── Guardrails
│
├── Week 1 (40 km)
│   ├── Tuesday: Main AM + Mini
│   ├── Wednesday: Main AM
│   ├── Thursday: Main AM + Main PM (double day)
│   ├── Friday: Mini
│   ├── Saturday: Main AM + Main PM (double day)
│   └── Sunday: Mini
│   └── Intensity Audit ✅
│
├── Week 2 (44 km)
│   └── [Progressive build...]
│
├── Week 3 (48 km)
│   └── [Peak week...]
│
├── Week 4 (48 km)
│   └── [Overload week...]
│
├── Week 5 (29 km - Deload)
│   └── [Recovery week...]
│
└── Block Summary
    ├── Mileage Progression
    ├── Intensity Splits
    └── Adaptations Targeted
```

### Each Session Includes

- **Purpose**: Why this session is in the program
- **Warm-up**: Detailed warm-up protocol
- **Main Work**: Complete sets, reps, paces, HR zones, rest periods
- **Cooldown**: Recovery and mobility work
- **Substitutions**: Alternative exercises if needed
- **Progression Knobs**: How to advance in future weeks

## Tips for Best Results

### 1. Accurate Physiological Data

- Test your threshold paces recently (within 2-4 weeks)
- Know your HR max (or use 220 - age as estimate)
- Be honest about current fitness level

### 2. Conservative Starting Mileage

Better to start too low than too high:
- Returning from injury: -30-40% of previous peak
- Deconditioning (2-4 weeks off): -20-30%
- Maintenance break (1-2 weeks off): -10-15%

### 3. Iteration

Don't be afraid to regenerate:
- Try different starting mileages
- Adjust progression rates
- Compare 3-week vs 4-week blocks

### 4. Injury Management

The system will adapt, but be proactive:
- List ALL current niggles in `active_injuries`
- Set conservative pain thresholds
- Use `additional_context` to emphasize caution

### 5. Previous Block Context

Always include your previous block when available:
- Ensures progressive overload
- Maintains training continuity
- Adapts to your recent adaptations

## Troubleshooting

### "No module named 'click'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "API key not provided"
**Solution**: Set up .env file
```bash
cp .env.example .env
# Edit .env and add your key
```

### Configuration parse errors
**Solution**: Check file format
- **For `.txt` files**: Use `key=value` format, no spaces before `=`
- **For `.yaml` files**: Check indentation (use spaces, not tabs), ensure proper YAML syntax
- Check all required fields are present
- Validate pace format: "mm:ss" (e.g., "4:37" not "4-37")

### Configuration validation errors
**Solution**: Read the error message - it explains what's wrong!

**Example error:**
```
❌ Invalid training week structure
   Training days: 5
   Total sessions: 8
   Double days needed: 3
   Double days specified: 0
   Problem: You need 3 double days to fit 8 sessions in 5 training days
   Suggestion: Specify 3 days for double_days (e.g., double_days=Wednesday, Friday, Saturday)
```

**Common validation issues:**
- **Double days mismatch**: Sessions don't match training days math
  - Fix: Adjust `total_sessions_per_week` or `double_days`
- **Too many sessions**: Can't fit sessions in available training days
  - Fix: Reduce sessions or reduce rest days
- **Long run on rest day**: Long run scheduled when you're resting
  - Fix: Change `long_run_day` to a training day
- **Too many runs**: More runs than total sessions
  - Fix: Reduce `runs_per_week` to ≤ `total_sessions_per_week`

### Generation takes too long
**Normal**: Each block takes 5-10 minutes to generate
- 11-15 API calls are made
- Each layer builds on previous ones
- Large amount of text is generated

If it takes >15 minutes, check your internet connection.

### Output seems generic
**Solution**: Add more context
- Include previous training block
- Add specific focus areas
- Use `additional_context` field
- Be specific about goals and constraints

## Workflow Examples

### Monthly Block Generation

```bash
# January - Base building
python main.py generate --config configs/2025_01_base.yaml \
  --output-dir blocks/2025_01

# February - BUILD
python main.py generate --config configs/2025_02_build.yaml \
  --output-dir blocks/2025_02

# March - PEAK
python main.py generate --config configs/2025_03_peak.yaml \
  --output-dir blocks/2025_03
```

### A/B Testing Different Approaches

```bash
# Approach A: Higher volume, slower progression
python main.py generate --config config_high_volume.yaml \
  --output-dir blocks/approach_a

# Approach B: Lower volume, faster progression
python main.py generate --config config_fast_progression.yaml \
  --output-dir blocks/approach_b

# Compare the two blocks and choose
```

## Next Steps

1. **Execute the plan**: Follow your generated block
2. **Track performance**: Note which sessions feel good/hard
3. **Save the block**: Keep it as `previous_training_block_file` for next time
4. **Iterate**: Use learnings to inform next block's configuration

---

**Questions?** Check the README.md or open a GitHub issue.
