#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Runs every 30 minutes
# Schedule: */30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-cron-complete.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MONITOR_SCRIPT="$SCRIPT_DIR/youtube-comment-monitor-complete.py"
LOG_FILE="$SCRIPT_DIR/youtube-comment-monitor-cron.log"
ERROR_LOG="$SCRIPT_DIR/youtube-comment-monitor-cron-error.log"

# Ensure script is executable
chmod +x "$MONITOR_SCRIPT"

# Run monitor (defaults to demo mode if no credentials)
python3 "$MONITOR_SCRIPT" >> "$LOG_FILE" 2>> "$ERROR_LOG"

# If we got here successfully, log the run
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Monitor run completed" >> "$LOG_FILE"
