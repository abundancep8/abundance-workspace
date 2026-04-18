#!/bin/bash

# YouTube Comment Monitor Cron Script (30-minute intervals)
# This script runs the Python monitor and logs output

SCRIPT_DIR="$HOME/.openclaw/workspace/.cache"
MONITOR_SCRIPT="$SCRIPT_DIR/youtube-comment-monitor.py"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/youtube-comment-monitor-$(date +%Y%m%d).log"

# Create log directory if needed
mkdir -p "$LOG_DIR"

# Run the monitor with error handling
{
    echo "=== YouTube Comment Monitor Cron Run ==="
    echo "Start Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo ""
    
    cd "$SCRIPT_DIR"
    python3 "$MONITOR_SCRIPT" 2>&1
    
    EXIT_CODE=$?
    echo ""
    echo "End Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Exit Code: $EXIT_CODE"
    
} >> "$LOG_FILE" 2>&1

exit 0
