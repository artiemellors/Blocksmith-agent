# Blocksmith Setup Guide for Beginners

This guide will walk you through setting up Blocksmith on your laptop, step by step. No technical experience needed!

## What You'll Need

1. A laptop (Windows, Mac, or Linux)
2. An Anthropic API key (instructions below)
3. About 15 minutes

---

## Step 1: Install Python

Blocksmith is written in Python, so you need Python installed on your laptop.

### For Mac:

1. Open **Terminal** (search for "Terminal" in Spotlight)
2. Type this command and press Enter:
   ```bash
   python3 --version
   ```
3. If you see something like `Python 3.8.x` or higher, you're good! Skip to Step 2.
4. If not, install Python:
   - Go to https://www.python.org/downloads/
   - Click the yellow "Download Python" button
   - Open the downloaded file and follow the installer
   - Restart Terminal and try `python3 --version` again

### For Windows:

1. Open **Command Prompt** (search for "cmd" in the Start menu)
2. Type this command and press Enter:
   ```bash
   python --version
   ```
3. If you see something like `Python 3.8.x` or higher, you're good! Skip to Step 2.
4. If not, install Python:
   - Go to https://www.python.org/downloads/
   - Click the yellow "Download Python" button
   - **IMPORTANT**: When the installer opens, check the box that says "Add Python to PATH"
   - Click "Install Now"
   - Restart Command Prompt and try `python --version` again

---

## Step 2: Get an Anthropic API Key

Blocksmith uses Claude AI to generate your training blocks. You need an API key from Anthropic.

1. Go to https://console.anthropic.com/
2. Sign up for an account (or log in if you have one)
3. Go to "API Keys" in the menu
4. Click "Create Key"
5. Give it a name like "Blocksmith"
6. **Copy the key** - it looks like `sk-ant-...` - and save it somewhere safe
   - You'll need this in Step 4
   - **Important**: This key is like a password - don't share it!

**Cost**: Each training block costs about $2-4 to generate. Make sure you have credit in your Anthropic account.

---

## Step 3: Download Blocksmith

### Option A: Download as ZIP (Easiest)

1. Go to https://github.com/artiemellors/Blocksmith
2. Click the green "Code" button
3. Click "Download ZIP"
4. Find the downloaded ZIP file (probably in your Downloads folder)
5. Double-click to unzip it
6. Move the "Blocksmith" folder to somewhere easy to find (like your Documents folder)

### Option B: Use Git (If you know how)

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Navigate to where you want to put Blocksmith
3. Run:
   ```bash
   git clone https://github.com/artiemellors/Blocksmith.git
   cd Blocksmith
   ```

---

## Step 4: Set Up Blocksmith

### Mac Instructions:

1. Open **Terminal**
2. Navigate to the Blocksmith folder. If it's in Documents:
   ```bash
   cd ~/Documents/Blocksmith
   ```
   (Adjust the path if you put it somewhere else)

3. Install the required packages:
   ```bash
   pip3 install -r requirements.txt
   ```
   (This might take a minute - it's downloading some software Blocksmith needs)

4. Create your API key file:
   ```bash
   cp .env.example .env
   ```

5. Open the `.env` file in a text editor:
   ```bash
   open -e .env
   ```

6. You'll see this:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

7. Replace `your_api_key_here` with your actual API key from Step 2:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-abc123...
   ```

8. Save and close the file

### Windows Instructions:

1. Open **Command Prompt**
2. Navigate to the Blocksmith folder. If it's in Documents:
   ```bash
   cd %USERPROFILE%\Documents\Blocksmith
   ```
   (Adjust the path if you put it somewhere else)

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   (This might take a minute - it's downloading some software Blocksmith needs)

4. Create your API key file:
   ```bash
   copy .env.example .env
   ```

5. Open the `.env` file in Notepad:
   ```bash
   notepad .env
   ```

6. You'll see this:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

7. Replace `your_api_key_here` with your actual API key from Step 2:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-abc123...
   ```

8. Save and close Notepad

---

## Step 5: Test That Everything Works

Still in Terminal/Command Prompt, run:

**Mac:**
```bash
python3 main.py version
```

**Windows:**
```bash
python main.py version
```

You should see:
```
Blocksmith v1.0.0
Automated HYROX Training Block Generator
```

If you see that, congratulations! Blocksmith is ready to use! 🎉

---

## Step 6: Create Your First Training Block

### 6A: Create a Configuration File

**Mac:**
```bash
python3 main.py create-config my_training_block.yaml
```

**Windows:**
```bash
python main.py create-config my_training_block.yaml
```

You'll see: `✓ Sample configuration created: my_training_block.yaml`

### 6B: Edit the Configuration File

Open the file in a text editor:

**Mac:**
```bash
open -e my_training_block.yaml
```

**Windows:**
```bash
notepad my_training_block.yaml
```

You'll see a file that looks like this:

```yaml
athlete:
  name: "Arthur Mellors"  # ← Change this to YOUR name
  age: 41                 # ← Change this to YOUR age

physiological_parameters:
  hr_max: 188                    # ← YOUR max heart rate
  threshold_t1_pace: "4:37"      # ← YOUR T1 pace (minutes:seconds per km)
  threshold_t2_pace: "4:17"      # ← YOUR T2 pace

injury_information:
  active_injuries: []            # ← List any injuries, like ["knee pain"]
  pain_threshold_during: 2
  pain_threshold_next_day: 3

block_objectives:
  primary_goal: "BUILD"          # ← What's your goal? (BUILD, PEAK, Base building, etc.)
  running_mileage_week1: 40      # ← Starting weekly km
  weekly_progression_percent: 10 # ← % increase each week
  block_duration_weeks: 4        # ← How many weeks before deload?
  deload_week: true
  specific_focus_areas:
    - "threshold running"        # ← What do you want to focus on?
    - "sled work"
    - "wall balls"

previous_training_block_file: null  # ← Path to previous block (optional)
additional_context: null            # ← Any special instructions (optional)
```

**Edit the values** to match YOUR details:
- Your name and age
- Your heart rate max
- Your threshold paces (if you don't know these, use a recent race pace or make a conservative guess)
- Your current fitness level (starting mileage)
- What you want to work on

**Save the file** when you're done.

**Tip**: If you don't know your threshold paces, here are some rough guidelines:
- T1 (Tempo pace): Pace you could hold for about 45-60 minutes
- T2 (Threshold pace): Pace you could hold for about 20-30 minutes
- Format: "minutes:seconds" per kilometer, like "4:30" for 4 minutes 30 seconds per km

### 6C: Generate Your Training Block!

**Mac:**
```bash
python3 main.py generate --config my_training_block.yaml
```

**Windows:**
```bash
python main.py generate --config my_training_block.yaml
```

You'll see:
1. A summary of your configuration
2. A prompt asking if you want to proceed - type `y` and press Enter
3. The system will start generating each layer (this takes 5-10 minutes)
4. Progress messages as each layer is created

When it's done, you'll see:
```
SUCCESS!
Your complete training block is ready at:
  output/complete_training_block.md
```

### 6D: View Your Training Block

**Mac:**
```bash
open output/complete_training_block.md
```

**Windows:**
```bash
notepad output\complete_training_block.md
```

This is your complete training block! You can also find it by:
- Opening your file browser (Finder on Mac, File Explorer on Windows)
- Going to the Blocksmith folder
- Opening the "output" folder
- Double-clicking `complete_training_block.md`

---

## Common Issues & Solutions

### "Command not found" or "python is not recognized"

**Solution**: Python isn't installed correctly. Go back to Step 1 and make sure Python is installed.

### "API key not provided"

**Solution**: The `.env` file isn't set up correctly. Go back to Step 4 and make sure you:
1. Created the `.env` file
2. Put your actual API key in it (not the example text)
3. Saved the file

### "Error loading configuration"

**Solution**: There's a typo in your YAML file. Common issues:
- Make sure the format is exactly right (spacing matters in YAML files)
- Paces should be in quotes: `"4:37"` not `4:37`
- Lists need a dash: `- "threshold running"` not just `"threshold running"`

### "Rate limit error"

**Solution**: You're making too many requests. Wait 1 minute and try again.

### The training block seems generic

**Solution**: Add more context:
- Include your previous training block (save it as a file and reference it)
- Fill in the `additional_context` field with specific instructions
- Be detailed in your `specific_focus_areas`

---

## Next Time You Want to Generate a Block

1. Open Terminal (Mac) or Command Prompt (Windows)
2. Navigate to Blocksmith:
   - **Mac**: `cd ~/Documents/Blocksmith`
   - **Windows**: `cd %USERPROFILE%\Documents\Blocksmith`
3. Edit your config file:
   - Update your threshold paces if they've improved
   - Change the `primary_goal` for your new phase
   - Update `running_mileage_week1` based on where you are now
   - Update the `previous_training_block_file` to point to your last block
4. Generate:
   - **Mac**: `python3 main.py generate --config my_training_block.yaml`
   - **Windows**: `python main.py generate --config my_training_block.yaml`

---

## Tips for Best Results

1. **Save your blocks**: After each block, save the markdown file with a meaningful name like `2025_Jan_Build.md`

2. **Use previous blocks**: Always include your previous block in the config - this helps maintain progression

3. **Be conservative**: Better to start with lower mileage and progress safely

4. **Update paces regularly**: As you get fitter, update your threshold paces every 4-6 weeks

5. **Track injuries**: If you have any niggles, add them to `active_injuries` - the system will adapt

---

## Need Help?

If you get stuck:
1. Read the error message carefully - it usually tells you what's wrong
2. Check the main README.md file in the Blocksmith folder for more details
3. Open an issue on GitHub: https://github.com/artiemellors/Blocksmith/issues

---

**You're all set! Enjoy your automated training blocks! 🏃‍♂️**
