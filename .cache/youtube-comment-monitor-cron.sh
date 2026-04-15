#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Runs every 30 minutes via OpenClaw cron
# Logs to .cache/youtube-comments.jsonl and generates report

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
SCRIPT="$CACHE_DIR/youtube-comment-monitor-v2.py"
LOG="$CACHE_DIR/youtube-monitor-cron.log"
REPORT="$CACHE_DIR/youtube-comments-report.txt"

# Create cache dir if needed
mkdir -p "$CACHE_DIR"

# Run monitor
echo "[$(date)] Starting YouTube Comment Monitor..." >> "$LOG"
python3 "$SCRIPT" >> "$LOG" 2>&1

# Check report
if [ -f "$REPORT" ]; then
    echo "[$(date)] Monitor completed successfully" >> "$LOG"
else
    echo "[$(date)] WARNING: Report not generated" >> "$LOG"
fi

exit 0
