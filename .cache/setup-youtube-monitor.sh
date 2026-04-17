#!/bin/bash
# YouTube Comment Monitor Setup Script

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace/.cache"
SCRIPT="${WORKSPACE}/youtube-monitor.py"

echo "🎥 YouTube Comment Monitor Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
echo "✓ Checking Python..."
python3 --version

# Install dependencies
echo "📦 Installing dependencies..."
pip install google-api-python-client --quiet
echo "✓ google-api-python-client installed"

# Check API key
echo ""
echo "🔑 API Key Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "⚠️  YOUTUBE_API_KEY not set"
    echo ""
    echo "Get one from: https://console.cloud.google.com/apis/credentials"
    echo "Then add to ~/.zshrc or ~/.bashrc:"
    echo ""
    echo "  export YOUTUBE_API_KEY=\"your-key-here\""
    echo ""
    echo "After setting, reload your shell:"
    echo "  source ~/.zshrc"
    echo ""
else
    echo "✓ YOUTUBE_API_KEY is set"
fi

# Check script
echo ""
echo "📝 Script Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$SCRIPT" ]; then
    chmod +x "$SCRIPT"
    echo "✓ youtube-monitor.py is ready"
else
    echo "✗ youtube-monitor.py not found"
    exit 1
fi

# Cron setup
echo ""
echo "⏰ Cron Job Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To run every 30 minutes, add to crontab:"
echo ""
echo "  */30 * * * * source ~/.zshrc && python $SCRIPT >> $WORKSPACE/youtube-monitor.log 2>&1"
echo ""
echo "Edit crontab with: crontab -e"
echo ""

# Offer to run test
echo "🧪 Test Run"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "⚠️  Skipping test — please set YOUTUBE_API_KEY first"
else
    echo "Ready to test? (y/n)"
    read -r response
    
    if [ "$response" = "y" ] || [ "$response" = "yes" ]; then
        echo ""
        echo "Running test..."
        python3 "$SCRIPT"
    fi
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "📚 See YOUTUBE_SETUP.md for troubleshooting and customization"
