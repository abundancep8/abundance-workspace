#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Usage: Add to crontab: */30 * * * * bash ~/.openclaw/workspace/.cache/youtube-comment-monitor.sh

WORKSPACE="$HOME/.openclaw/workspace"
SCRIPT="$WORKSPACE/.cache/youtube-comment-monitor.py"
LOG="$WORKSPACE/.cache/youtube-monitor.log"

# Ensure Python is found
PYTHON=$(which python3)
if [ -z "$PYTHON" ]; then
    PYTHON="/usr/bin/python3"
fi

# Change to workspace (important for relative paths)
cd "$WORKSPACE" || exit 1

# Run the monitor with logging
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting YouTube Comment Monitor"
    $PYTHON "$SCRIPT" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Completed"
} >> "$LOG"

exit 0
