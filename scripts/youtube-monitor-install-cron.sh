#!/bin/bash
# YouTube Comment Monitor - Automated Cron Installation Script
# Run this script to automatically install the cron job

WORKSPACE="/Users/abundance/.openclaw/workspace"
CRON_COMMAND="*/30 * * * * $WORKSPACE/scripts/youtube-monitor-cron.sh >> $WORKSPACE/.cache/youtube-monitor-cron-exec.log 2>&1"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  YouTube Comment Monitor - Automated Cron Installation        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "youtube-monitor-cron.sh"; then
    echo "✓ Cron job already installed!"
    echo ""
    echo "Current cron job:"
    crontab -l 2>/dev/null | grep "youtube-monitor-cron.sh"
    echo ""
    exit 0
fi

echo "Installing cron job..."
echo ""

# Get current crontab (if any)
CURRENT_CRONTAB=$(crontab -l 2>/dev/null || echo "")

# Create temporary file with current crontab + new job
TMP_CRONTAB=$(mktemp)
echo "$CURRENT_CRONTAB" > "$TMP_CRONTAB"
echo "$CRON_COMMAND" >> "$TMP_CRONTAB"

# Install the new crontab
crontab "$TMP_CRONTAB"
RESULT=$?

# Clean up
rm "$TMP_CRONTAB"

if [ $RESULT -eq 0 ]; then
    echo "✓ Cron job installed successfully!"
    echo ""
    echo "Job details:"
    echo "  Schedule: Every 30 minutes (*/30 * * * *)"
    echo "  Script: $WORKSPACE/scripts/youtube-monitor-cron.sh"
    echo "  Logs: $WORKSPACE/.cache/youtube-monitor-cron-exec.log"
    echo ""
    echo "Verify installation:"
    crontab -l 2>/dev/null | grep "youtube-monitor-cron.sh"
    echo ""
    echo "Your YouTube comment monitor is now running! 🎉"
    echo ""
    echo "Next steps:"
    echo "  1. Wait for the next 30-minute interval (cron runs at :00 and :30)"
    echo "  2. Check logs: tail -f $WORKSPACE/.cache/youtube-monitor-cron-exec.log"
    echo "  3. View reports: cat $WORKSPACE/.cache/youtube-comments-report.txt"
    echo ""
else
    echo "✗ Failed to install cron job"
    echo ""
    echo "Please try manually:"
    echo "  1. Run: crontab -e"
    echo "  2. Add this line:"
    echo "     $CRON_COMMAND"
    echo "  3. Save and exit"
    exit 1
fi
