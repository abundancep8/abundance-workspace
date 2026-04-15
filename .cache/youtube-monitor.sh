#!/bin/bash
# YouTube Comment Monitor - Cron Wrapper
# Runs every 30 minutes

export YOUTUBE_API_KEY="${YOUTUBE_API_KEY}"
export YOUTUBE_CHANNEL_ID="${YOUTUBE_CHANNEL_ID}"

cd "$(dirname "$0")/.."
python3 .cache/youtube-monitor.py
