#!/bin/bash
# YouTube Comment Monitor - Quick Setup Script
# This script handles most of the one-time setup

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
cd "$WORKSPACE"

echo "🎬 YouTube Comment Monitor - Setup Wizard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Check prerequisites
echo "📋 Step 1: Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi
echo "  ✓ Python 3 found: $(python3 --version)"

if [ ! -f ".secrets/youtube-credentials.json" ]; then
    echo "❌ YouTube credentials not found at .secrets/youtube-credentials.json"
    echo "   Please download your OAuth credentials from Google Cloud Console."
    exit 1
fi
echo "  ✓ YouTube credentials found"

# Step 2: Check Python dependencies
echo ""
echo "📋 Step 2: Checking Python dependencies..."
python3 -c "import google.auth; import googleapiclient.discovery" 2>/dev/null && {
    echo "  ✓ Google API libraries installed"
} || {
    echo "  ⚠️  Installing Google API libraries..."
    pip3 install google-auth-oauthlib google-api-python-client
    echo "  ✓ Libraries installed"
}

# Step 3: Make scripts executable
echo ""
echo "📋 Step 3: Setting up permissions..."
chmod +x scripts/youtube-comment-monitor.py
chmod +x scripts/youtube-setup-auth.py
chmod +x scripts/youtube-monitor-cron.sh
echo "  ✓ Scripts are executable"

# Step 4: Create cache directory if needed
echo ""
echo "📋 Step 4: Creating cache directory..."
mkdir -p .cache
echo "  ✓ Cache directory ready"

# Step 5: Authenticate
echo ""
echo "🔐 Step 5: YouTube API Authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  A browser window will open. Please authorize the app to access your YouTube channel."
echo ""
read -p "Press Enter to continue with authentication..." -r

python3 scripts/youtube-setup-auth.py

# Step 6: Test the monitor
echo ""
echo "📋 Step 6: Testing the monitor..."
read -p "Run a test to make sure everything works? (y/n) " -r -n 1
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running monitor test..."
    python3 scripts/youtube-comment-monitor.py
fi

# Step 7: Set up cron
echo ""
echo "📋 Step 7: Cron Job Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose your cron setup method:"
echo ""
echo "  A) System Crontab (runs in background)"
echo "  B) Skip for now (set up manually later)"
echo ""
read -p "Choose (A/B): " -r method

case $method in
    [Aa])
        echo ""
        echo "Installing cron job..."
        (crontab -l 2>/dev/null || echo "") | cat - << 'EOF' | crontab -
# YouTube Comment Monitor - Every 30 minutes
*/30 * * * * cd /Users/abundance/.openclaw/workspace && bash scripts/youtube-monitor-cron.sh >> .cache/youtube-monitor.log 2>&1
EOF
        echo "✓ Cron job installed!"
        echo ""
        echo "Verify with:"
        echo "  crontab -l | grep youtube"
        ;;
    [Bb])
        echo ""
        echo "Skipped. You can set up cron later with:"
        echo "  bash $WORKSPACE/scripts/setup-youtube-monitor.sh"
        echo ""
        echo "See YOUTUBE-MONITOR-CRON-SETUP.md for manual options."
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Your monitor is ready! Here's what happens next:"
echo ""
echo "  • Every 30 minutes, new comments are fetched"
echo "  • Questions & praise get auto-replied"
echo "  • Sales inquiries are flagged for review"
echo "  • Everything is logged to: .cache/youtube-comments.jsonl"
echo ""
echo "📈 Monitor your activity:"
echo ""
echo "  Watch logs live:"
echo "    tail -f .cache/youtube-monitor.log"
echo ""
echo "  View recent comments:"
echo "    tail -20 .cache/youtube-comments.jsonl | jq ."
echo ""
echo "  Find flagged sales:"
echo "    grep 'sales' .cache/youtube-comments.jsonl | jq ."
echo ""
echo "📚 For more info, see:"
echo "  • YOUTUBE-MONITOR-SUMMARY.md (overview)"
echo "  • YOUTUBE-MONITOR-SETUP.md (detailed guide)"
echo "  • YOUTUBE-MONITOR-CRON-SETUP.md (cron options)"
echo ""
echo "🚀 You're all set!"
