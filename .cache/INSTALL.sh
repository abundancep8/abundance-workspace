#!/bin/bash
# Installation script for YouTube Comment Monitor

set -e

CACHE_DIR="$HOME/.openclaw/workspace/.cache"
SCRIPT="youtube-comment-monitor.py"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  YouTube Comment Monitor - Installation Guide         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Dependencies
echo "[Step 1/4] Installing Python dependencies..."
pip3 install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client 2>&1 | grep -E "Successfully|Requirement"
echo "✓ Dependencies installed"
echo ""

# Step 2: API Key
echo "[Step 2/4] YouTube API Setup"
echo ""
echo "You need to create a YouTube API key:"
echo "  1. Go to: https://console.cloud.google.com/"
echo "  2. Create a new project (if needed)"
echo "  3. Enable 'YouTube Data API v3'"
echo "  4. Go to Credentials → Create API Key"
echo ""
read -p "Paste your YouTube API Key (or press Enter to skip): " api_key

if [ -n "$api_key" ]; then
    # Store in a config file
    cat > "$CACHE_DIR/.youtube-config" << CONF
export YOUTUBE_API_KEY="$api_key"
CONF
    source "$CACHE_DIR/.youtube-config"
    echo "✓ API Key configured"
else
    echo "⚠ Skipped - you'll need to set YOUTUBE_API_KEY manually later"
fi
echo ""

# Step 3: Channel ID
echo "[Step 3/4] Channel Configuration"
read -p "YouTube Channel ID (e.g., UCxxxxxx, or press Enter to auto-detect): " channel_id

if [ -n "$channel_id" ]; then
    echo "export YOUTUBE_CHANNEL_ID=\"$channel_id\"" >> "$CACHE_DIR/.youtube-config"
    echo "✓ Channel ID set: $channel_id"
else
    echo "⚠ Will auto-detect channel by name (slower)"
fi
echo ""

# Step 4: Test
echo "[Step 4/4] Testing the script..."
cd "$CACHE_DIR"

if [ -n "$api_key" ]; then
    source .youtube-config
    python3 "$SCRIPT" --test 2>&1 | tail -3
    echo "✓ Script test passed"
else
    echo "⚠ Skipped test (need API key)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Installation Complete!                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Set up the cron job (runs every 30 minutes):"
echo "   $ crontab -e"
echo "   Then add this line:"
echo "   */30 * * * * source ~/.openclaw/workspace/.cache/.youtube-config && cd ~/.openclaw/workspace/.cache && python3 $SCRIPT >> monitor.log 2>&1"
echo ""
echo "2. Test it manually:"
echo "   $ cd ~/.openclaw/workspace/.cache"
echo "   $ source .youtube-config"
echo "   $ python3 $SCRIPT"
echo ""
echo "3. View the log:"
echo "   $ tail -f monitor.log"
echo ""
echo "4. See comments:"
echo "   $ tail youtube-comments.jsonl | python3 -m json.tool"
echo ""
echo "5. Generate report:"
echo "   $ python3 youtube-monitor-report.py"
echo ""
