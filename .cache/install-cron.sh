#!/bin/bash
# YouTube Comment Monitor - Cron Installation Script
# This script installs the 30-minute monitoring job

set -e

echo "🚀 Installing YouTube Comment Monitor Cron Job..."
echo ""

# Create temporary cron file
TEMP_CRON=$(mktemp)
trap "rm -f $TEMP_CRON" EXIT

# Get existing crontab (if any)
echo "📋 Reading existing crontab..."
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# Check if job already exists
if grep -q "youtube-monitor-cron" "$TEMP_CRON"; then
    echo "✅ YouTube monitor job already installed!"
    echo ""
    crontab -l | grep youtube
    exit 0
fi

# Add new job
echo "" >> "$TEMP_CRON"
echo "# YouTube Comment Monitor - Concessa Obvius (Every 30 minutes)" >> "$TEMP_CRON"
echo "*/30 * * * * $HOME/.openclaw/workspace/.cache/youtube-monitor-cron.sh >> $HOME/.openclaw/workspace/.cache/youtube-monitor-cron.log 2>&1" >> "$TEMP_CRON"

# Install crontab
echo "📝 Installing cron job..."
crontab "$TEMP_CRON"

# Verify
echo "✅ Installation complete!"
echo ""
echo "📋 Installed job:"
crontab -l | grep youtube
echo ""
echo "⏰ Monitor will run every 30 minutes starting now"
echo "📊 Check progress: cat ~/.openclaw/workspace/.cache/youtube-comments-report.txt"
echo ""
