#!/bin/bash
# YouTube DM Monitor — Cron Wrapper
# Runs every hour to monitor Concessa Obvius DMs

cd /Users/abundance/.openclaw/workspace

# Run the monitor
python3 agents/youtube-agent/youtube-dm-monitor-concessa.py >> .cache/youtube-dm-monitor.log 2>&1

# Optional: Send report to Discord if configured
# curl -X POST https://discord.webhook/... -d @.cache/youtube-dm-report.txt
