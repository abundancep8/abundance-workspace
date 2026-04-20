#!/bin/bash
# YouTube Comment Monitor - 30-minute cycle launcher
# Runs the cron worker and logs output

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE="${WORKSPACE}/.cache"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cd "$WORKSPACE"

# Run worker
python3 youtube-monitor-cron-worker.py >> "${CACHE}/youtube-comment-monitor-cron.log" 2>&1

# Append execution record
echo "[${TIMESTAMP}] ✓ Cron cycle completed" >> "${CACHE}/youtube-monitor-execution.log"
