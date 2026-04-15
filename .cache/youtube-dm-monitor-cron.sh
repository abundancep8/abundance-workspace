#!/bin/bash
# YouTube DM Monitor - Hourly Cron Job
# Runs the DM monitor every hour
# Logs output to youtube-dms-cron.log

WORKSPACE="/Users/abundance/.openclaw/workspace"
LOG_FILE="$WORKSPACE/.cache/youtube-dms-cron.log"
PID_FILE="$WORKSPACE/.cache/youtube-dm-monitor.pid"

# Prevent concurrent runs
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[$(date)] Monitor already running (PID: $OLD_PID). Skipping this run." >> "$LOG_FILE"
        exit 0
    fi
fi

# Write current PID
echo $$ > "$PID_FILE"

# Run the monitor
cd "$WORKSPACE"
python3 .cache/youtube-dm-monitor-standalone.py >> "$LOG_FILE" 2>&1

# Clean up PID file
rm -f "$PID_FILE"
