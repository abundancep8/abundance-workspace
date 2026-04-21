#!/bin/bash
# YouTube Comment Monitor Runner
# Use this wrapper to run the monitor from cron with proper environment setup

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to workspace
cd "$WORKSPACE_DIR"

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Require API key
if [ -z "$YOUTUBE_API_KEY" ] && [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "ERROR: Set YOUTUBE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS" >&2
    exit 1
fi

# Run the monitor
python3 "$SCRIPT_DIR/youtube-monitor.py" "$@"
