#!/bin/bash
# YouTube Comment Monitor wrapper for cron

WORKSPACE="/Users/abundance/.openclaw/workspace"
SCRIPT="$WORKSPACE/.scripts/youtube-monitor.py"
LOG="$WORKSPACE/.cache/youtube-monitor.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG")"

# Run the monitor and log output
python3 "$SCRIPT" >> "$LOG" 2>&1

exit 0
