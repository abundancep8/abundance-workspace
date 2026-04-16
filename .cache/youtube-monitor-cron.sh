#!/bin/bash
# YouTube Comment Monitor - Cron wrapper
# Add to crontab with: */30 * * * * /path/to/youtube-monitor-cron.sh

export YOUTUBE_API_KEY="${YOUTUBE_API_KEY}"
export YOUTUBE_CHANNEL_ID="${YOUTUBE_CHANNEL_ID}"
export PATH="/usr/local/bin:$PATH"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="${SCRIPT_DIR}/youtube-monitor.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting monitor..." >> "$LOG_FILE"
node "$SCRIPT_DIR/youtube-monitor.js" >> "$LOG_FILE" 2>&1
RESULT=$?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Monitor finished (exit code: $RESULT)" >> "$LOG_FILE"

exit $RESULT
