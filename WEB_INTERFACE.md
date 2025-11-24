# Blocksmith Web Interface

A user-friendly web interface for generating HYROX training blocks without using the command line.

## Quick Start

### 1. Install Dependencies

Make sure you have Flask installed:

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Ensure your `.env` file has your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Start the Web Server

**Mac/Linux:**
```bash
python3 app.py
```

**Windows:**
```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`

### 4. Open Your Browser

Navigate to:
```
http://127.0.0.1:5000
```

## Using the Web Interface

### Form Fields

The web interface provides an easy-to-use form with the following sections:

#### **Athlete Information**
- **Name**: Your full name
- **Age**: Your age in years

#### **Physiological Parameters**
- **Max Heart Rate (HR Max)**: Your maximum heart rate in beats per minute
- **T1 Threshold Pace**: Pace you can hold for 45-60 minutes (format: `mm:ss` per km, e.g., `4:37`)
- **T2 Threshold Pace**: Pace you can hold for 20-30 minutes (format: `mm:ss` per km, e.g., `4:17`)

#### **Injury Information** (Optional)
- **Active Injuries**: List current injuries (comma-separated)
- **Pain Thresholds**: Set acceptable pain levels during and after sessions
- **Soreness Cutoff**: Hours before soreness should resolve
- **Volume Reduction**: Percentage to reduce volume if injured

#### **Training Week Structure**
- **Rest Days**: Which day(s) you rest (e.g., `Monday` or `Monday, Wednesday`)
- **Total Sessions Per Week**: How many training sessions per week (e.g., `8`)
- **Double Days**: Days with AM + PM sessions (e.g., `Wednesday, Saturday`)
- **Runs Per Week**: How many sessions are runs (e.g., `4`)
- **Long Run Day**: Which day has your long run (e.g., `Sunday`)

**The form automatically validates your training week structure to ensure it's mathematically possible!**

#### **Block Objectives**
- **Primary Goal**: Your training goal (e.g., `BUILD`, `PEAK`, `Base building`)
- **Starting Weekly Mileage**: Starting running kilometers per week
- **Weekly Progression**: Percentage increase each week (e.g., `10`)
- **Block Duration**: Number of build weeks (e.g., `4`)
- **Deload Week**: Whether to include a deload week after build weeks
- **Specific Focus Areas**: 2-4 areas to emphasize (comma-separated)

#### **Additional Context** (Optional)
- **Special Instructions**: Any special instructions for this block
- **Previous Training Block**: Paste your previous block here for continuity

### Generating Your Training Block

1. **Fill out the form** with your details
   - Required fields are marked with `*`
   - The form validates as you type

2. **Click "Generate Training Block"**
   - The form will disappear
   - A progress bar appears showing generation status

3. **Wait for generation** (typically 5-10 minutes)
   - Watch the progress bar advance through each layer
   - Real-time status updates show which layer is being generated

4. **Download your block**
   - When complete, a success message appears
   - Click "Download Training Block" to get your markdown file
   - Click "Generate Another Block" to create a new one

## Features

### Real-Time Progress Tracking

The interface polls the server every second to show:
- Progress percentage (0-100%)
- Current layer being generated
- Estimated completion status

### Automatic Validation

The form validates your input in real-time:

- **Pace format**: Ensures `mm:ss` format (e.g., `4:37`)
- **Training week math**: Checks that sessions fit within training days
- **Double days calculation**: Ensures you specify enough double days for your sessions
- **Runs validation**: Ensures runs don't exceed total sessions

**Example validation:**
- Rest days: `Monday` (6 training days)
- Total sessions: `8`
- Required double days: `2` (8 sessions - 6 training days)
- The form will warn you if double days don't match!

### Error Handling

If generation fails:
- Clear error message is displayed
- You can fix the issue and try again
- No need to restart the server

## Technical Details

### API Endpoints

The web interface uses these endpoints:

- `GET /` - Main form page
- `POST /api/generate` - Start generation
- `GET /api/status/<session_id>` - Get generation progress
- `GET /api/download/<session_id>` - Download completed block

### Output Files

Generated blocks are saved to:
```
output/web_generations/<session_id>/complete_training_block.md
```

Each generation gets a unique session ID based on timestamp.

### Session Management

- Sessions are stored in memory (not persistent across server restarts)
- Each generation has a unique session ID
- Multiple users can generate blocks simultaneously

## Troubleshooting

### "API key not configured"

**Problem**: The server can't find your Anthropic API key.

**Solution**:
1. Create or edit `.env` file in the Blocksmith directory
2. Add: `ANTHROPIC_API_KEY=your_actual_api_key_here`
3. Restart the web server

### "Validation error" when submitting form

**Problem**: Your training week structure has logical errors.

**Solution**: Read the error message carefully - it tells you exactly what's wrong:
- Too many sessions for training days
- Double days don't match math
- Runs exceed total sessions
- Long run scheduled on rest day

### Generation takes too long

**Normal behavior**: Each block takes 5-10 minutes to generate.

If it takes longer than 15 minutes:
1. Check your internet connection
2. Check the server console for errors
3. Refresh the page and try again

### Download button not working

**Problem**: The file wasn't generated or can't be found.

**Solution**:
1. Wait until progress shows 100% complete
2. Check server console for errors
3. Try downloading again

### Port already in use

**Problem**: Another application is using port 5000.

**Solution**:
```bash
# Kill the process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port by editing app.py:
# Change: app.run(debug=True, host='127.0.0.1', port=5000)
# To: app.run(debug=True, host='127.0.0.1', port=5001)
```

## Comparison with CLI

### Web Interface
- ✅ No command line needed
- ✅ Visual form with validation
- ✅ Real-time progress bar
- ✅ Easy download button
- ❌ Requires server running

### CLI (Command Line)
- ✅ No server needed
- ✅ Works offline (after dependencies installed)
- ✅ Easy to automate
- ❌ Requires command line knowledge
- ❌ Text-based configuration files

**Choose based on your preference!** Both methods produce identical training blocks.

## Advanced: Running in Production

For production deployment (not just local use):

1. **Set secure secret key** in `.env`:
   ```
   FLASK_SECRET_KEY=your-random-secure-key-here
   ```

2. **Disable debug mode** in `app.py`:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

3. **Use a production server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Set up HTTPS** using a reverse proxy like Nginx

5. **Use Redis** for session storage instead of in-memory

## Tips

1. **Save your form data**: The form doesn't save automatically. If you close the browser, you'll need to re-enter everything.

2. **Copy previous blocks**: Instead of uploading files, you can copy/paste your previous block directly into the form.

3. **Test validation**: Try entering invalid data to see the validation messages. This helps you understand the constraints.

4. **Use the CLI for automation**: If you're generating blocks regularly with the same config, the CLI might be more efficient.

---

**Need Help?**
- Check the main [README.md](README.md) for general Blocksmith information
- See [USAGE.md](USAGE.md) for detailed configuration guidance
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for beginner setup instructions
