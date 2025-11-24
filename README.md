# Blocksmith

**Automated HYROX Training Block Generator**

Blocksmith automates the creation of comprehensive, multi-week HYROX training blocks using a layered prompt engineering approach with Claude AI.

> **New to coding?** Check out the [beginner-friendly setup guide](SETUP_GUIDE.md) for step-by-step installation instructions!

## What It Does

Instead of manually applying 11+ prompts one by one to build a training block, Blocksmith allows you to:

1. Provide your **previous training block** (optional)
2. Set your **objectives** for the new block
3. Update **performance metrics** (threshold pace, HR max, etc.)
4. Note any **injury information**

Then run a single command to generate a complete, detailed training block that includes:

- Week-by-week progression (typically 4 build weeks + 1 deload week)
- Full session details (running, strength, strength endurance, HYROX combos, mini sessions)
- Warm-ups, cooldowns, progression knobs, and substitutions
- Intensity audits and mileage tracking
- HYROX race-specific training with proper fatigue management

## Features

- **Layered Generation**: Uses 11+ interconnected prompts to build progressively detailed training plans
- **Configurable**: Simple YAML configuration for athlete profile, objectives, and constraints
- **Previous Block Context**: Builds on your last training block for continuity
- **Injury Management**: Respects pain thresholds and provides substitutions
- **Full Traceability**: Saves intermediate layer outputs for review
- **Professional Output**: Generates markdown-formatted training blocks ready for use

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Blocksmith
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Quick Start

### 1. Create a configuration file

**Option A: Simple Text Format (Recommended - Easier to Edit)**

```bash
python main.py create-config-simple my_block_config.txt
```

**Option B: YAML Format**

```bash
python main.py create-config my_block_config.yaml
```

Both create a sample configuration file with all necessary fields. The text format uses simple `key=value` pairs and is less error-prone than YAML.

### 2. Edit the configuration

Open your config file and customize:

- **Athlete information**: Name, age
- **Physiological parameters**: HR max, threshold paces
- **Injury information**: Active injuries, pain thresholds
- **Training week structure**: Rest days, sessions per week, double days, runs per week
- **Block objectives**: Goal (BUILD/PEAK/Base building), mileage, duration
- **Previous block** (optional): Path to your last training block markdown file

### 3. Generate your training block

```bash
python main.py generate --config my_block_config.txt
```
(or `.yaml` if you chose YAML format)

The tool will:
1. Load and validate your configuration
2. Display a summary and ask for confirmation
3. Generate each layer sequentially (Layer 0 → Layer 11)
4. Save intermediate outputs and the final complete block

### 4. Find your results

Your complete training block will be at:
- `output/complete_training_block.md` - Final assembled block
- `output/layer_*.md` - Individual layer outputs (if enabled)
- `output/generation_summary.md` - Summary of generation

## Configuration File Structure

### Simple Text Format (.txt)

```text
# Athlete Information
name=Arthur Mellors
age=42

# Physiological Parameters
hr_max=188
threshold_t1_pace=4:37  # mm:ss per km
threshold_t2_pace=4:17

# Injury Information
active_injuries=  # Leave empty or list: quad pain, shoulder soreness
pain_threshold_during=2
pain_threshold_next_day=3
soreness_cutoff_hours=36
volume_reduction_percent=25

# Training Week Structure
rest_days=Monday  # Can be multiple: Monday, Wednesday
total_sessions_per_week=8
double_days=Wednesday, Saturday  # Days with AM + PM sessions
runs_per_week=4  # How many sessions are runs
long_run_day=Sunday  # Which day has the long run

# Block Objectives
primary_goal=BUILD  # Examples: BUILD, PEAK, Base building
running_mileage_week1=40  # km
weekly_progression_percent=10
block_duration_weeks=4
deload_week=yes
specific_focus_areas=threshold running, sled work, wall balls

# Optional
previous_training_block_file=  # Path to previous block
additional_context=  # Special instructions
```

### YAML Format (.yaml)

```yaml
athlete:
  name: "Your Name"
  age: 41

physiological_parameters:
  hr_max: 188
  threshold_t1_pace: "4:37"  # mm:ss per km
  threshold_t2_pace: "4:17"

injury_information:
  active_injuries: []  # e.g., ["quad pain"]
  pain_threshold_during: 2
  pain_threshold_next_day: 3
  soreness_cutoff_hours: 36
  volume_reduction_percent: 25

training_week_structure:
  rest_days: "Monday"  # Can be multiple: "Monday, Wednesday"
  total_sessions_per_week: 8
  double_days: "Wednesday, Saturday"  # Days with AM + PM sessions
  runs_per_week: 4  # How many sessions are runs
  long_run_day: "Sunday"  # Which day has the long run

block_objectives:
  primary_goal: "BUILD"  # Examples: BUILD, PEAK, Base building
  running_mileage_week1: 40  # km
  weekly_progression_percent: 10
  block_duration_weeks: 4
  deload_week: true
  specific_focus_areas:
    - "threshold running"
    - "sled work"

# Optional: Path to previous block
previous_training_block_file: "previous_block.md"

# Optional: Additional context
additional_context: "Focus on shoulder health this block"
```

### Configuration Validation

Blocksmith validates your configuration before generation and provides helpful error messages:

**Example validation:**
- ✅ Sessions fit within training days (can't have 12 sessions in 5 training days)
- ✅ Double days math is correct (8 sessions - 6 training days = 2 double days needed)
- ✅ Runs don't exceed total sessions
- ✅ Long run day is a training day (not a rest day)

If validation fails, you'll see a clear error message with suggestions for fixing the issue.

## Command Reference

### Generate a training block

```bash
python main.py generate --config CONFIG_FILE [OPTIONS]
```

**Options:**
- `--config, -c`: Path to configuration file (.txt or .yaml) (required)
- `--output-dir, -o`: Output directory (default: `output`)
- `--api-key, -k`: Anthropic API key (or use ANTHROPIC_API_KEY env var)
- `--model, -m`: Claude model to use (default: claude-sonnet-4-5-20250929)
- `--save-layers / --no-save-layers`: Save intermediate layers (default: true)

### Create a sample configuration

**Simple text format (recommended):**
```bash
python main.py create-config-simple OUTPUT_FILE.txt
```

**YAML format:**
```bash
python main.py create-config OUTPUT_FILE.yaml
```

### Show version

```bash
python main.py version
```

## How It Works

Blocksmith uses a **layered prompt engineering** approach:

1. **Layer 0**: Establishes global context, rules, and constraints
2. **Layer 1**: Creates Week 1 skeleton (session archetypes only)
3. **Layers 2-6**: Expand each session type in detail:
   - Running sessions
   - Max strength sessions
   - Strength endurance sessions
   - HYROX combo/brick sessions
   - Aerobic engine/recovery & mini sessions
4. **Layer 7**: Assembles complete Week 1 with all details
5. **Layers 8-10**: Generates Weeks 2-4 with progressive overload
6. **Deload Layer**: Creates recovery week (if enabled)
7. **Layer 11**: Assembles final block artifact with all weeks

Each layer builds on previous outputs, creating a coherent, detailed training plan.

## Examples

### Basic usage

```bash
python main.py generate --config my_config.yaml
```

### Specify custom output directory

```bash
python main.py generate --config my_config.yaml --output-dir my_blocks/block_001
```

### Use different model

```bash
python main.py generate --config my_config.yaml --model claude-opus-4-20250514
```

## Tips

1. **Previous Block**: Including your previous training block helps maintain continuity and progressive overload
2. **Specific Focus Areas**: List 2-3 key areas to emphasize in `specific_focus_areas`
3. **Injury Management**: Be honest about active injuries - the system will adapt sessions accordingly
4. **Review Layers**: Check intermediate layer outputs to understand how the plan was built
5. **Iteration**: You can regenerate with tweaked parameters to compare different approaches

## Cost Estimation

Each complete block generation typically uses:
- 10-15 API calls (one per layer)
- ~150,000-250,000 tokens total
- Estimated cost: $2-4 per block (as of 2025, using Sonnet 4.5)

## Troubleshooting

### API Key Error
```
Error: API key not provided
```
**Solution**: Ensure `.env` file exists with valid `ANTHROPIC_API_KEY`

### Configuration Parse Error
```
Error loading configuration: ...
```
**Solution**:
- For `.txt` files: Check `key=value` format, ensure no extra spaces before `=`
- For `.yaml` files: Check YAML syntax (indentation matters!), ensure all required fields are present

### Configuration Validation Error
```
❌ Invalid training week structure
```
**Solution**: Read the error message carefully - it explains exactly what's wrong and suggests a fix. Common issues:
- Double days don't match math (e.g., 8 sessions with 6 training days needs 2 double days)
- Too many sessions for available training days
- Long run scheduled on a rest day
- More runs than total sessions

### Rate Limit Error
**Solution**: The generator includes 1-second delays between API calls. If still rate-limited, wait a few minutes and retry.

## Project Structure

```
Blocksmith/
├── main.py              # CLI interface
├── generator.py         # Core generation engine
├── prompts.py           # Layer prompt templates
├── models.py            # Data models (Pydantic)
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── output/             # Generated training blocks (created at runtime)
```

## Requirements

- Python 3.8+
- Anthropic API key (Claude access)
- Internet connection

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

For issues, questions, or feature requests, please open a GitHub issue.

## Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/) - AI generation
- [Pydantic](https://pydantic.dev/) - Data validation
- [Click](https://click.palletsprojects.com/) - CLI framework

---

**Blocksmith** - Train smarter, not harder.
