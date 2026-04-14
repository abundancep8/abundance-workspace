#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Run this every 30 minutes

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
SCRIPT="$CACHE_DIR/youtube-monitor.py"
LOG="$CACHE_DIR/youtube-monitor.log"

# Source API key if stored locally
if [ -f "$CACHE_DIR/.youtube-env" ]; then
  source "$CACHE_DIR/.youtube-env"
fi

# Check if Python script exists
if [ ! -f "$SCRIPT" ]; then
  echo "[$(date)] ERROR: Script not found at $SCRIPT" >> "$LOG"
  exit 1
fi

# Run monitor with timeout
timeout 300 python3 "$SCRIPT" >> "$LOG" 2>&1
exit_code=$?

if [ $exit_code -eq 124 ]; then
  echo "[$(date)] WARNING: Monitor timed out after 5 minutes" >> "$LOG"
elif [ $exit_code -ne 0 ]; then
  echo "[$(date)] ERROR: Monitor exited with code $exit_code" >> "$LOG"
fi

exit $exit_code
