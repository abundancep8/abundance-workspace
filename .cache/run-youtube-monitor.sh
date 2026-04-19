#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Runs the monitor, logs output, and sends summary if needed

WORKSPACE_DIR="$HOME/.openclaw/workspace"
SCRIPT="$WORKSPACE_DIR/.cache/youtube-monitor.py"
LOG_DIR="$WORKSPACE_DIR/.cache"
LOG_FILE="$LOG_DIR/youtube-monitor.log"
REPORT_FILE="$LOG_DIR/youtube-monitor-report.txt"

# Create log dir if needed
mkdir -p "$LOG_DIR"

# Run the monitor and capture output
{
    echo "=== YouTube Comment Monitor Run ==="
    echo "Started: $(date)"
    echo ""
    
    cd "$WORKSPACE_DIR"
    python3 "$SCRIPT" 2>&1
    
    echo ""
    echo "Completed: $(date)"
    echo "=== End Run ==="
} >> "$LOG_FILE" 2>&1

# Extract report from log (last run's output)
tail -20 "$LOG_FILE" > "$REPORT_FILE"

exit 0
