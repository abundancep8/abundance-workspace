#!/bin/bash
# Cron wrapper for YouTube DM Monitor - runs hourly
# Logs to .cache/youtube-dm-monitor.log

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="${WORKSPACE}/.cache"
MONITOR_SCRIPT="${WORKSPACE}/youtube-dm-monitor-live.py"
LOG_FILE="${CACHE_DIR}/youtube-dms.jsonl"
CRON_LOG="${CACHE_DIR}/youtube-dm-monitor-cron.log"

# Create cache directory
mkdir -p "$CACHE_DIR"

{
    echo "=========================================="
    echo "YouTube DM Monitor - Hourly Run"
    echo "Time: $(date +'%Y-%m-%d %H:%M:%S %Z')"
    echo "=========================================="
    
    # Run the monitor
    python3 "$MONITOR_SCRIPT" --report 2>&1
    
    # Check status
    if [ $? -eq 0 ]; then
        echo "✅ Run completed successfully"
    else
        echo "⚠️  Run completed with warnings"
    fi
    
    echo ""
} >> "$CRON_LOG"

# Tail last few lines for verification
echo "Latest report:"
tail -20 "$CRON_LOG" | head -15
