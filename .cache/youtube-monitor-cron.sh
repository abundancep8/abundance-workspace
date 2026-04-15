#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Runs every 30 minutes

set -e

WORKSPACE="$HOME/.openclaw/workspace"
SCRIPT="$WORKSPACE/.cache/youtube-monitor.py"
LOG_DIR="$WORKSPACE/.cache"
LOG_FILE="$LOG_DIR/youtube-monitor.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Run the monitor and append output to log
{
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Run: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python3 "$SCRIPT" 2>&1
    echo ""
} >> "$LOG_FILE"

exit 0
