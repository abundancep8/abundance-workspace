#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Runs every 30 minutes
# Usage: Add to crontab with: */30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="${SCRIPT_DIR}/youtube-monitor.log"
PYTHON_SCRIPT="${SCRIPT_DIR}/youtube-monitor.py"

# Load environment
export PATH="/usr/local/bin:/usr/bin:$PATH"

# Run monitor and log output
{
    echo "=========================================="
    echo "YouTube Monitor Run - $(date)"
    echo "=========================================="
    python3 "$PYTHON_SCRIPT" 2>&1
    echo "Status: $?"
    echo ""
} >> "$LOG_FILE"

# Rotate log if too large (>50MB)
if [ -f "$LOG_FILE" ]; then
    SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null)
    if [ "$SIZE" -gt 52428800 ]; then
        mv "$LOG_FILE" "${LOG_FILE}.$(date +%s)"
        echo "Log rotated" > "$LOG_FILE"
    fi
fi
