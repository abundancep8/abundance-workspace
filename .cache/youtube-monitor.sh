#!/bin/bash
# YouTube Comment Monitor Runner
# Set your credentials below, then run: bash .cache/youtube-monitor.sh

# ============ CONFIGURATION ============
YOUTUBE_API_KEY="YOUR_API_KEY_HERE"
YOUTUBE_CHANNEL_ID="YOUR_CHANNEL_ID_HERE"
# =======================================

# Validate credentials
if [ "$YOUTUBE_API_KEY" = "YOUR_API_KEY_HERE" ] || [ "$YOUTUBE_CHANNEL_ID" = "YOUR_CHANNEL_ID_HERE" ]; then
    echo "❌ Configuration required!"
    echo ""
    echo "Edit this script and set:"
    echo "  YOUTUBE_API_KEY - Your Google API key"
    echo "  YOUTUBE_CHANNEL_ID - YouTube channel ID (starts with UC...)"
    echo ""
    echo "See .cache/youtube-monitor-setup.md for detailed instructions."
    exit 1
fi

# Export and run
export YOUTUBE_API_KEY
export YOUTUBE_CHANNEL_ID

cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-monitor.py
