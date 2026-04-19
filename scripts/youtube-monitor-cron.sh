#!/bin/bash
# YouTube Comment Monitor - Cron Launcher
# Runs every 30 minutes

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd /Users/abundance/.openclaw/workspace

# Activate virtual environment and run the monitor
source .venv/bin/activate 2>/dev/null || {
    echo "Virtual environment not found. Attempting to create..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
}

# Run the monitor
python3 scripts/youtube-comment-monitor.py 2>&1 | tee -a .cache/youtube-monitor.log

# Keep log under 5MB
if [ -f .cache/youtube-monitor.log ]; then
    SIZE=$(stat -f%z .cache/youtube-monitor.log 2>/dev/null || stat -c%s .cache/youtube-monitor.log 2>/dev/null)
    if [ "$SIZE" -gt 5242880 ]; then
        tail -n 1000 .cache/youtube-monitor.log > .cache/youtube-monitor.log.tmp
        mv .cache/youtube-monitor.log.tmp .cache/youtube-monitor.log
    fi
fi
