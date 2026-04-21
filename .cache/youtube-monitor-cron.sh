#!/bin/bash
# YouTube Comment Monitor - Cron Job Wrapper
# Runs every 30 minutes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/youtube-monitor.py"
LOG_DIR="$SCRIPT_DIR"
LOG_FILE="$LOG_DIR/monitor.log"

# Ensure directories exist
mkdir -p "$LOG_DIR"

# Run monitor and capture output
{
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Running YouTube Comment Monitor"
    python3 "$MONITOR_SCRIPT" 2>&1
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Completed"
} >> "$LOG_FILE" 2>&1

# Optional: Send summary to Discord or email
# Uncomment if you have notification set up:
# tail -20 "$LOG_FILE" | curl -X POST -d @- https://hooks.slack.com/services/YOUR/WEBHOOK
