#!/bin/bash
# Cron wrapper for YouTube comment monitor
# Run every 30 minutes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/.cache/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

mkdir -p "$LOG_DIR"

# Run monitor with error handling
python3 "$SCRIPT_DIR/youtube-monitor.py" \
    >> "$LOG_DIR/monitor_$TIMESTAMP.log" \
    2>&1 || {
        echo "[ERROR] Monitor failed at $TIMESTAMP" >> "$LOG_DIR/errors.log"
        exit 1
    }

exit 0
