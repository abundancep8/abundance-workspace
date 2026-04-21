#!/bin/bash
# Install YouTube Comment Monitor as LaunchD service
# Runs every 30 minutes to check for new comments

set -e

WORKSPACE="${HOME}/.openclaw/workspace"
PLIST="${WORKSPACE}/com.openclaw.youtube-comment-monitor.plist"
LAUNCH_AGENT_DIR="${HOME}/Library/LaunchAgents"

echo "🎬 Installing YouTube Comment Monitor..."
echo ""

# 1. Check if workspace exists
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ Workspace not found: $WORKSPACE"
    exit 1
fi

# 2. Check if monitor script exists
if [ ! -f "$WORKSPACE/.bin/youtube-comment-monitor.py" ]; then
    echo "❌ Monitor script not found: $WORKSPACE/.bin/youtube-comment-monitor.py"
    exit 1
fi

# 3. Check if plist exists
if [ ! -f "$PLIST" ]; then
    echo "❌ LaunchD config not found: $PLIST"
    exit 1
fi

# 4. Create LaunchAgent directory if needed
mkdir -p "$LAUNCH_AGENT_DIR"
echo "✅ LaunchAgent directory ready: $LAUNCH_AGENT_DIR"

# 5. Copy plist to LaunchAgents
cp "$PLIST" "$LAUNCH_AGENT_DIR/"
echo "✅ Installed LaunchD service: com.openclaw.youtube-comment-monitor"

# 6. Check if service is already loaded
if launchctl list | grep -q "com.openclaw.youtube-comment-monitor"; then
    echo "⚠️  Service already loaded. Unloading for restart..."
    launchctl unload "$LAUNCH_AGENT_DIR/com.openclaw.youtube-comment-monitor.plist" || true
fi

# 7. Load the service
launchctl load "$LAUNCH_AGENT_DIR/com.openclaw.youtube-comment-monitor.plist"
echo "✅ Service loaded and scheduled"

# 8. Verify it's running
sleep 1
if launchctl list | grep -q "com.openclaw.youtube-comment-monitor"; then
    PID=$(launchctl list | grep "com.openclaw.youtube-comment-monitor" | awk '{print $1}')
    echo "✅ Service is running (PID: $PID)"
else
    echo "⚠️  Service loaded but not yet running (will start in 30 minutes)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  YouTube Comment Monitor Installation Complete ✅            ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Schedule: Every 30 minutes                                 ║"
echo "║  Monitor Script: ~/.openclaw/workspace/.bin/youtube-comment-monitor.py"
echo "║  LaunchAgent: ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist"
echo "║  Logs: ~/.openclaw/workspace/.cache/youtube-comment-monitor.log"
echo "║  Data: ~/.openclaw/workspace/.cache/youtube-comments.jsonl"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "📖 Next Steps:"
echo ""
echo "1. Test the monitor manually:"
echo "   python3 ~/.openclaw/workspace/.bin/youtube-comment-monitor.py"
echo ""
echo "2. Queue a test comment:"
echo "   python3 ~/.openclaw/workspace/.bin/youtube-comment-ingester.py \\"
echo "     --commenter 'Test User' \\"
echo "     --text 'How do I get started?'"
echo ""
echo "3. View the latest report:"
echo "   cat ~/.openclaw/workspace/.cache/youtube-comment-report.txt"
echo ""
echo "4. Check logs:"
echo "   tail -f ~/.openclaw/workspace/.cache/youtube-comment-monitor.log"
echo ""
echo "5. View processed comments:"
echo "   tail -10 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool"
echo ""
echo "6. Verify service status:"
echo "   launchctl list | grep youtube-comment-monitor"
echo ""

exit 0
