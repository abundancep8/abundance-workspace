#!/bin/bash
# YouTube Comment Monitor - 30-minute cycle
# Monitors Concessa Obvius channel for new comments
# Categorizes: questions, praise, spam, sales
# Auto-responds to categories 1-2, flags category 4

set -e

WORKSPACE=/Users/abundance/.openclaw/workspace
cd "$WORKSPACE"

# Activate venv
source .venv/bin/activate

# Run monitor
python3 youtube-monitor.py

# Log run time
echo "[$(date '+%Y-%m-%d %H:%M:%S')] YouTube comment monitor cycle completed" >> .cache/youtube-monitor.log
