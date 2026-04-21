#!/bin/bash
# YouTube Comment Monitor - Cron wrapper
# Runs every 30 minutes via cron

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/youtube-monitor.py"

# Ensure cache directory exists
mkdir -p "$WORKSPACE_DIR/.cache"

# Check if credentials exist
if [ ! -f "$WORKSPACE_DIR/.cache/youtube-credentials.json" ]; then
    echo "[ERROR] YouTube credentials not found!"
    echo "Please complete setup at: docs/youtube-monitor-setup.md"
    exit 1
fi

# Run the monitor
cd "$WORKSPACE_DIR"
python3 "$PYTHON_SCRIPT"
