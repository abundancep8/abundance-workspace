#!/bin/bash
#
# Setup YouTube DM Monitor Cron Job
# Automates hourly DM monitoring for Concessa Obvius channel
#

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE_DIR/.cache"
SCRIPT="$CACHE_DIR/youtube_dm_monitor.py"
LOG_FILE="$CACHE_DIR/youtube-dms-cron.log"

echo "🎥 YouTube DM Monitor - Cron Setup"
echo "=================================="
echo ""

# Check if script exists
if [ ! -f "$SCRIPT" ]; then
    echo "❌ Script not found: $SCRIPT"
    echo "Please ensure youtube_dm_monitor.py is in .cache/"
    exit 1
fi

# Make script executable
chmod +x "$SCRIPT"
echo "✅ Script is executable"

# Create log directory if needed
mkdir -p "$CACHE_DIR"
echo "✅ Cache directory ready: $CACHE_DIR"

# Test script
echo ""
echo "Testing script with mock data..."
python3 "$SCRIPT" --mock-mode > /dev/null 2>&1 || {
    echo "❌ Script test failed. Check Python dependencies:"
    echo "   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    exit 1
}
echo "✅ Script test passed"

# Add to crontab if not already present
echo ""
echo "Setting up hourly cron job..."
CRON_JOB="0 * * * * cd $WORKSPACE_DIR && python3 $SCRIPT >> $LOG_FILE 2>&1"

# Check if cron already exists
if crontab -l 2>/dev/null | grep -q "youtube_dm_monitor.py"; then
    echo "⚠️  Cron job already exists!"
    echo "Run: crontab -l (to view) or crontab -e (to edit)"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job added"
    echo ""
    echo "Scheduled to run:"
    echo "  Time: Every hour (0, 1:00, 2:00, ...)"
    echo "  Script: $SCRIPT"
    echo "  Log: $LOG_FILE"
fi

# Show cron status
echo ""
echo "Current crontab entries for youtube_dm_monitor:"
echo "───────────────────────────────────────────────"
crontab -l 2>/dev/null | grep youtube_dm_monitor || echo "(none yet)"

echo ""
echo "Next steps:"
echo "1. Test: python3 $SCRIPT --mock-mode"
echo "2. Set up DM input (email, webhook, or manual queue)"
echo "3. Monitor: tail -f $LOG_FILE"
echo "4. Check reports: python3 $SCRIPT --report"
echo ""
echo "✅ Setup complete!"
