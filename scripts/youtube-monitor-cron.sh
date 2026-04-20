#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Run every 30 minutes via: */30 * * * * /path/to/youtube-monitor-cron.sh

set -e

# Change to workspace directory
cd /Users/abundance/.openclaw/workspace

# Load environment (adjust path if using separate .env file)
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Fallback to environment variables if not in .env
YOUTUBE_API_KEY="${YOUTUBE_API_KEY:-}"
YOUTUBE_CHANNEL_ID="${YOUTUBE_CHANNEL_ID:-}"

if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "ERROR: YOUTUBE_API_KEY not set" >> .cache/monitor.log
    exit 1
fi

if [ -z "$YOUTUBE_CHANNEL_ID" ]; then
    echo "ERROR: YOUTUBE_CHANNEL_ID not set" >> .cache/monitor.log
    exit 1
fi

# Ensure .cache exists
mkdir -p .cache

# Run monitor with environment variables
(
    echo "=========================================="
    echo "Monitor run: $(date)"
    python3 scripts/youtube-comment-monitor.py
    echo "=========================================="
) >> .cache/monitor.log 2>&1

exit $?
