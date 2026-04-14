#!/bin/bash
# Wrapper script for YouTube Comment Monitor
# Runs every 30 minutes via cron

set -e

WORKSPACE="${HOME}/.openclaw/workspace"
SCRIPT="${WORKSPACE}/scripts/youtube-comment-monitor.py"
LOG="${WORKSPACE}/.cache/youtube-monitor.log"

# Ensure directories exist
mkdir -p "${WORKSPACE}/.cache"

# Run monitor with error handling
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Monitor run started" >> "$LOG"

if python3 "$SCRIPT" >> "$LOG" 2>&1; then
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Monitor run completed successfully" >> "$LOG"
else
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Monitor run FAILED" >> "$LOG"
fi

# Keep log size manageable (last 1000 lines)
tail -1000 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
