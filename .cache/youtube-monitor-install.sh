#!/bin/bash
# YouTube Comment Monitor - Installation Script
# Usage: bash .cache/youtube-monitor-install.sh

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"

echo "🎬 YouTube Comment Monitor - Installation"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
python3 -m pip install google-api-python-client --quiet
echo "✅ Dependencies installed"

# Make scripts executable
chmod +x "$CACHE_DIR/youtube-monitor.py"

# Create config if it doesn't exist
if [ ! -f "$CACHE_DIR/youtube-monitor-config.json" ]; then
    echo ""
    echo "⚠️  Config file not found. Creating template..."
    cp "$CACHE_DIR/youtube-monitor-config.json.template" "$CACHE_DIR/youtube-monitor-config.json"
    echo "📝 Edit this file with your credentials:"
    echo "   $CACHE_DIR/youtube-monitor-config.json"
    echo ""
    echo "Need help? Read: $CACHE_DIR/YOUTUBE-MONITOR-SETUP.md"
else
    echo "✅ Config file exists"
fi

# Test the script
echo ""
echo "Testing script..."
python3 "$CACHE_DIR/youtube-monitor.py" && echo "✅ Test passed" || echo "⚠️  Test failed (check config)"

# Show cron setup
echo ""
echo "=========================================="
echo "📋 Next Steps:"
echo "=========================================="
echo ""
echo "1. Fill in credentials:"
echo "   nano $CACHE_DIR/youtube-monitor-config.json"
echo ""
echo "2. Set up cron (every 30 minutes):"
echo ""
echo "   crontab -e"
echo ""
echo "   Then add this line:"
echo "   */30 * * * * cd $WORKSPACE && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1"
echo ""
echo "3. Verify cron is installed:"
echo "   crontab -l"
echo ""
echo "4. Check logs:"
echo "   tail -f $CACHE_DIR/youtube-monitor.log"
echo ""
echo "📚 Full setup guide: $CACHE_DIR/YOUTUBE-MONITOR-SETUP.md"
echo ""
