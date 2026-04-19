#!/bin/bash
# YouTube Comment Monitor - Installation & Setup Helper

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"

echo "🎬 YouTube Comment Monitor - Setup Assistant"
echo "=============================================="
echo ""

# Step 1: Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q google-auth-oauthlib google-auth-httplib2 google-api-python-client
echo "✅ Dependencies installed"
echo ""

# Step 2: Check credentials
echo "🔐 Checking Google OAuth credentials..."
if [ ! -f "$CACHE_DIR/credentials.json" ]; then
    echo "⚠️  Missing: $CACHE_DIR/credentials.json"
    echo ""
    echo "To set up credentials:"
    echo "1. Go to: https://console.cloud.google.com"
    echo "2. Create a project"
    echo "3. Enable YouTube Data API v3"
    echo "4. Create OAuth 2.0 Credentials (Desktop app)"
    echo "5. Download JSON file"
    echo "6. Save as: $CACHE_DIR/credentials.json"
    echo ""
    read -p "Press Enter once credentials are saved, or Ctrl+C to exit..."
else
    echo "✅ Credentials file found"
fi
echo ""

# Step 3: Configure channel ID
echo "📺 YouTube Channel Configuration"
if [ ! -f "$WORKSPACE/youtube-monitor-config.json" ]; then
    echo "Creating config file..."
fi

CHANNEL_ID=""
while [ -z "$CHANNEL_ID" ] || [ "$CHANNEL_ID" == "CHANNEL_ID_HERE" ]; do
    read -p "Enter your YouTube channel ID (UCxxxxxxxxxxxxxxxxxxxxxx): " CHANNEL_ID
    if [ -z "$CHANNEL_ID" ]; then
        echo "Channel ID cannot be empty"
    elif [ ${#CHANNEL_ID} -ne 24 ]; then
        echo "Channel ID must be 24 characters (starts with UC)"
        CHANNEL_ID=""
    fi
done

# Update config with channel ID
python3 << EOF
import json
from pathlib import Path

config_file = Path("$WORKSPACE/youtube-monitor-config.json")
with open(config_file) as f:
    config = json.load(f)

config['channel_id'] = '$CHANNEL_ID'

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Channel ID configured: $CHANNEL_ID")
EOF
echo ""

# Step 4: Test the script
echo "🧪 Running first test (this will open Google login)..."
python3 "$CACHE_DIR/youtube-comment-monitor.py"
echo ""

# Step 5: Set up cron
echo "⏰ Setting up cron job..."
read -p "Install cron job to run every 30 minutes? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Create log directory
    mkdir -p "$CACHE_DIR"
    
    # Check if already installed
    CRON_JOB="*/30 * * * * python3 $CACHE_DIR/youtube-comment-monitor.py >> $CACHE_DIR/youtube-monitor.log 2>&1"
    
    if crontab -l 2>/dev/null | grep -q "youtube-comment-monitor"; then
        echo "⚠️  Cron job already installed"
    else
        (crontab -l 2>/dev/null || true; echo "$CRON_JOB") | crontab -
        echo "✅ Cron job installed (every 30 minutes)"
    fi
else
    echo "⏭️  Skipped cron installation"
fi
echo ""

# Step 6: Summary
echo "=============================================="
echo "✅ Setup Complete!"
echo ""
echo "📖 Next steps:"
echo "1. Monitor the log: tail -f $CACHE_DIR/youtube-monitor.log"
echo "2. View comments: cat $CACHE_DIR/youtube-comments.jsonl | jq ."
echo "3. Run reports: python3 $CACHE_DIR/youtube-monitor-report.py"
echo ""
echo "📚 Full setup guide: open $WORKSPACE/youtube-monitor-setup.md"
echo ""
