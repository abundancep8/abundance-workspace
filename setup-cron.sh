#!/bin/bash
# Setup YouTube Comment Monitor Cron Job

WORKSPACE="/Users/abundance/.openclaw/workspace"
SCRIPT="${WORKSPACE}/scripts/youtube-monitor-cron.sh"
LOG="${WORKSPACE}/.cache/youtube-cron-exec.log"

echo "📋 Setting up YouTube Comment Monitor cron job..."
echo ""

# Create a temporary crontab file
TEMP_CRON=$(mktemp)

# Get existing crontab (if any)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Check if job already exists
if grep -q "youtube-monitor-cron.sh" "$TEMP_CRON"; then
    echo "✅ Cron job already exists"
    cat "$TEMP_CRON" | grep youtube-monitor-cron.sh
else
    # Add the new job
    echo "" >> "$TEMP_CRON"
    echo "# YouTube Comment Monitor - runs every 30 minutes" >> "$TEMP_CRON"
    echo "*/30 * * * * $SCRIPT >> $LOG 2>&1" >> "$TEMP_CRON"
    
    # Install the new crontab
    crontab "$TEMP_CRON"
    echo "✅ Cron job installed!"
    echo ""
    echo "Schedule: Every 30 minutes"
    echo "Script: $SCRIPT"
    echo "Log: $LOG"
fi

# Cleanup
rm -f "$TEMP_CRON"

echo ""
echo "To view installed cron jobs:"
echo "  crontab -l"
echo ""
echo "To run monitor manually:"
echo "  cd $WORKSPACE && python3 scripts/youtube-comment-monitor.py"
