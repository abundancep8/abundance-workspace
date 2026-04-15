#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Runs every 30 minutes via macOS LaunchAgent
# Logs to .cache/youtube-comments.jsonl

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
SCRIPT="$CACHE_DIR/youtube-comment-monitor-v2.py"
LOG="$CACHE_DIR/youtube-monitor.log"

# Create directories if needed
mkdir -p "$CACHE_DIR"

# Add timestamp and run
{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ==== YouTube Comment Monitor Run ===="
  python3 "$SCRIPT" 2>&1
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ==== Run Complete ===="
} >> "$LOG" 2>&1

exit 0
