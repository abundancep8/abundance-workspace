#!/bin/bash
# YouTube DM Monitor - Hourly Cron Job
# Runs every hour to check for new DMs, categorize, and report

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
PYTHON_SCRIPT="$CACHE_DIR/youtube-dm-monitor-hourly.py"
LOG_FILE="$CACHE_DIR/youtube-dm-hourly-cron.log"
REPORT_FILE="$CACHE_DIR/youtube-dms-hourly-report-$(date +%Y-%m-%d-%H%M).json"

# Timestamp for logging
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting YouTube DM Monitor hourly check..." >> "$LOG_FILE"

# Run the monitor
cd "$WORKSPACE" || exit 1
python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    # Copy report to timestamped file for archival
    if [ -f "$CACHE_DIR/youtube-dms-hourly-report.json" ]; then
        cp "$CACHE_DIR/youtube-dms-hourly-report.json" "$REPORT_FILE"
    fi
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ YouTube DM Monitor completed successfully" >> "$LOG_FILE"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ YouTube DM Monitor failed with exit code $EXIT_CODE" >> "$LOG_FILE"
fi

exit $EXIT_CODE
