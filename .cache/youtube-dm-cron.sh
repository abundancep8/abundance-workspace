#!/bin/bash
# YouTube DM Monitor Cron Job
# Runs every hour, processes DMs from queue, logs results

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CACHE="$WORKSPACE/.cache"
SCRIPT="$CACHE/youtube-dm-monitor.py"
LOG_DIR="$CACHE/cron-logs"

mkdir -p "$LOG_DIR"

# Run monitor and capture output
TIMESTAMP=$(date -u '+%Y%m%d-%H%M%S')
OUTPUT_FILE="$LOG_DIR/youtube-dm-monitor-$TIMESTAMP.log"

python3 "$SCRIPT" > "$OUTPUT_FILE" 2>&1

# Keep only last 30 cron logs to save space
find "$LOG_DIR" -name "youtube-dm-monitor-*.log" -type f -mtime +30 -delete

exit 0
