#!/bin/bash
# YouTube Comment Monitor Setup
# Run this once to set up OAuth2 authentication

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
SECRETS_DIR="$WORKSPACE/.secrets"
CONFIG_DIR="$WORKSPACE/.config"
CACHE_DIR="$WORKSPACE/.cache"

echo "📺 YouTube Comment Monitor Setup"
echo "=================================="
echo ""

# Create directories
mkdir -p "$SECRETS_DIR" "$CONFIG_DIR" "$CACHE_DIR"
chmod 700 "$SECRETS_DIR"

# Check for credentials file
if [ ! -f "$SECRETS_DIR/youtube-credentials.json" ]; then
    echo "⚠️  STEP 1: Create YouTube API Credentials"
    echo ""
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a new project (or select existing)"
    echo "3. Enable YouTube Data API v3"
    echo "4. Go to 'Credentials' → 'Create Credentials' → OAuth 2.0 Client ID"
    echo "5. Choose 'Desktop application'"
    echo "6. Download the JSON file"
    echo "7. Save it to:"
    echo "   $SECRETS_DIR/youtube-credentials.json"
    echo ""
    read -p "Press ENTER when you've saved the credentials file..."
fi

if [ ! -f "$SECRETS_DIR/youtube-credentials.json" ]; then
    echo "❌ Credentials file not found. Exiting."
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Make script executable
chmod +x "$WORKSPACE/scripts/youtube-monitor.py"

# Initial auth run
echo ""
echo "🔐 Running initial authentication..."
echo "A browser window will open. Log in with the YouTube channel account."
echo ""
python3 "$WORKSPACE/scripts/youtube-monitor.py"

# Create config file if missing
if [ ! -f "$CONFIG_DIR/youtube-monitor.json" ]; then
    cat > "$CONFIG_DIR/youtube-monitor.json" << 'EOF'
{
  "channel_id": null,
  "last_comment_id": null,
  "stats": {
    "total": 0,
    "auto_responded": 0,
    "flagged": 0
  }
}
EOF
    echo "✓ Config file created: $CONFIG_DIR/youtube-monitor.json"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run the monitor manually to test:"
echo "   python3 $WORKSPACE/scripts/youtube-monitor.py"
echo ""
echo "2. Set up a cron job to run every 30 minutes:"
echo "   crontab -e"
echo "   Add this line:"
echo "   */30 * * * * /usr/bin/python3 $WORKSPACE/scripts/youtube-monitor.py"
echo ""
echo "3. Check logs:"
echo "   tail -f $CACHE_DIR/youtube-comments.jsonl"
