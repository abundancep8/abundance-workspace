#!/bin/bash
# Setup script for YouTube Comment Monitor
# Usage: ./setup-youtube-monitor.sh [API_KEY]

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"

echo "🎬 YouTube Comment Monitor Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if API key provided
if [ -z "$1" ]; then
    echo "⚠️  No API key provided."
    echo ""
    echo "To set up with your API key:"
    echo "  1. Get API key from https://console.cloud.google.com/"
    echo "  2. Run: $0 'your-api-key-here'"
    echo ""
    echo "For now, you can test with the demo:"
    echo "  python3 youtube_monitor_demo.py"
    echo ""
    exit 0
fi

API_KEY="$1"

# Create cache directory
mkdir -p "$CACHE_DIR"
echo "✅ Cache directory: $CACHE_DIR"

# Export API key
export YOUTUBE_API_KEY="$API_KEY"

# Test the API key
echo ""
echo "🔐 Testing API key..."
python3 << 'EOF'
import os
import sys
import requests

api_key = os.getenv("YOUTUBE_API_KEY")
if not api_key:
    print("❌ API key not set")
    sys.exit(1)

try:
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={"part": "snippet", "q": "test", "type": "channel", "key": api_key, "maxResults": 1},
        timeout=5
    )
    
    if response.status_code == 200:
        print("✅ API key is valid and working!")
    elif response.status_code == 403:
        print("❌ API key is invalid or YouTube Data API not enabled")
        sys.exit(1)
    else:
        print(f"❌ API error: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ API key validation failed"
    exit 1
fi

# Set up permanent environment variable
echo ""
echo "📝 Setting up permanent environment variable..."

SHELL_RC="$HOME/.zshrc"
if [ ! -f "$SHELL_RC" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

# Check if already set
if grep -q "YOUTUBE_API_KEY" "$SHELL_RC"; then
    echo "⚠️  YOUTUBE_API_KEY already in $SHELL_RC"
else
    echo "" >> "$SHELL_RC"
    echo "# YouTube Comment Monitor" >> "$SHELL_RC"
    echo "export YOUTUBE_API_KEY='$API_KEY'" >> "$SHELL_RC"
    echo "✅ Added to $SHELL_RC"
fi

# Create cron job
echo ""
echo "📅 Setting up cron job (every 30 minutes)..."

CRON_CMD="*/30 * * * * export YOUTUBE_API_KEY='$API_KEY' && cd '$WORKSPACE' && python3 youtube_monitor.py >> '$CACHE_DIR/youtube-monitor-cron.log' 2>&1"

# Check if already exists
if crontab -l 2>/dev/null | grep -q "youtube_monitor.py"; then
    echo "⚠️  Cron job already exists"
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cron job installed"
fi

# Summary
echo ""
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Documentation:"
echo "  - Main script: youtube_monitor.py"
echo "  - Demo script: youtube_monitor_demo.py"
echo "  - README:      YOUTUBE_MONITOR_README.md"
echo ""
echo "🚀 Run manually:"
echo "  python3 youtube_monitor.py"
echo ""
echo "📊 View reports:"
echo "  ls -la .cache/youtube-report-*.txt"
echo ""
echo "🔍 View comments log:"
echo "  cat .cache/youtube-comments.jsonl | jq ."
echo ""
echo "📋 Check cron status:"
echo "  crontab -l"
echo ""
echo "✨ All set! The monitor will run every 30 minutes automatically."
echo ""
