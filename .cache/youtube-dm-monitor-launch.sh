#!/bin/bash
# YouTube DM Monitor - Hourly Execution Script
cd /Users/abundance/.openclaw/workspace
python3 agents/youtube-agent/youtube-dm-monitor-concessa.py >> .cache/youtube-dms-cron.log 2>&1
