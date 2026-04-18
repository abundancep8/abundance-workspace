#!/bin/bash
# YouTube Comment Monitor - Cron Job
# Runs every 30 minutes to monitor Concessa Obvius channel

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
SCRIPT="$WORKSPACE/.cache/youtube_monitor.py"
LOG="$WORKSPACE/.cache/youtube-monitor.log"

# Ensure API key is set
if [ -z "$YOUTUBE_API_KEY" ]; then
    if [ -f "$WORKSPACE/.env" ]; then
        export $(grep YOUTUBE_API_KEY $WORKSPACE/.env)
    else
        echo "[$(date)] ERROR: YOUTUBE_API_KEY not set. Configure in .env or environment." >> "$LOG"
        exit 1
    fi
fi

# Run the monitor
cd "$WORKSPACE"
python3 "$SCRIPT" >> "$LOG" 2>&1

# Keep log file from growing too large (keep last 5000 lines)
if [ -f "$LOG" ]; then
    LINES=$(wc -l < "$LOG")
    if [ "$LINES" -gt 10000 ]; then
        tail -5000 "$LOG" > "$LOG.tmp"
        mv "$LOG.tmp" "$LOG"
    fi
fi

exit 0
