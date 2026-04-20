#!/bin/bash
# Run YouTube monitor with heartbeat reporting
# Call this from HEARTBEAT.md to check monitor status

cd /Users/abundance/.openclaw/workspace

# Run the monitor
python3 .cache/youtube-monitor.py

# Generate a quick report
echo -e "\n📊 MONITOR STATUS"
python3 .cache/youtube-monitor-report.py recent 6
