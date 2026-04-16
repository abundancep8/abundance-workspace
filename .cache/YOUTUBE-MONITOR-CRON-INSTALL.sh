#!/bin/bash
# YouTube Comment Monitor - Cron Installation Script
# Sets up monitoring to run every 30 minutes

set -e

SCRIPT_DIR="/Users/abundance/.openclaw/workspace/.cache"
CRON_JOB="*/30 * * * * cd $SCRIPT_DIR && bash youtube-monitor-cron.sh >> youtube-monitor.log 2>&1"

echo "=================================="
echo "YouTube Comment Monitor - Cron Setup"
echo "=================================="
echo ""

# Check if crontab already has this job
if crontab -l 2>/dev/null | grep -q "youtube-monitor-cron.sh"; then
    echo "✓ Cron job already installed"
else
    echo "Adding cron job to run every 30 minutes..."
    
    # Get current crontab (or empty if none exists)
    CURRENT=$(crontab -l 2>/dev/null || echo "")
    
    # Add new job
    NEW_CRON=$(echo "$CURRENT"; echo "$CRON_JOB")
    echo "$NEW_CRON" | crontab -
    
    echo "✓ Cron job installed successfully"
fi

echo ""
echo "Cron Job Details:"
echo "  Interval: Every 30 minutes"
echo "  Script: $SCRIPT_DIR/youtube-monitor-cron.sh"
echo "  Log: $SCRIPT_DIR/youtube-monitor.log"
echo ""

echo "Verify installation:"
echo "  crontab -l | grep youtube"
echo ""

# Run a test
echo "Running test monitor..."
cd "$SCRIPT_DIR"
bash youtube-monitor-cron.sh
