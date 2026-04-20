#!/bin/bash
# YouTube DM Monitor - Cron Wrapper Script
# Runs every hour to monitor YouTube Creator Studio DMs

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
MONITOR_SCRIPT="$WORKSPACE/.cache/youtube-dm-monitor.py"
LOG_DIR="$WORKSPACE/.cache"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Run the monitor
python3 "$MONITOR_SCRIPT" >> "$LOG_DIR/youtube-dm-monitor.log" 2>&1

# Optional: Send summary to Discord or email if configured
if [ -f "$LOG_DIR/youtube-dm-report.json" ]; then
    # Parse report and send notification
    # This would integrate with a notification system
    :
fi

exit 0
