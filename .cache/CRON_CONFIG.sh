#!/bin/bash
# YouTube Comment Monitor - Cron Configuration
# Install this to run the monitor every 30 minutes

# Setup Instructions:
# 1. Copy the command below
# 2. Run: crontab -e
# 3. Paste the line at the bottom
# 4. Save and exit

# Option A: Every 30 minutes (all day)
# */30 * * * * /usr/bin/python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1

# Option B: Every 30 minutes, business hours only (9 AM - 6 PM)
# */30 9-17 * * * /usr/bin/python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1

# Option C: Every 30 minutes on weekdays only
# */30 * * * 1-5 /usr/bin/python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1

# To install on macOS/Linux:
SCRIPT_PATH="$HOME/.openclaw/workspace/.cache/youtube_monitor.py"
LOG_PATH="$HOME/.openclaw/workspace/.cache/cron.log"

# Make script executable
chmod +x "$SCRIPT_PATH"

# Add to crontab (every 30 minutes)
(crontab -l 2>/dev/null | grep -v youtube_monitor; echo "*/30 * * * * /usr/bin/python3 $SCRIPT_PATH >> $LOG_PATH 2>&1") | crontab -

echo "✅ Cron job installed: Every 30 minutes"
echo "📝 Monitor logs: $LOG_PATH"
echo ""
echo "To verify: crontab -l"
echo "To remove: crontab -e (then delete the youtube_monitor line)"
