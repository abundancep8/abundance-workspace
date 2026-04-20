#!/bin/bash
# YouTube Comment Monitor - Environment Setup Helper

set -e

echo "🎥 YouTube Comment Monitor Setup"
echo "=================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q google-auth-oauthlib google-api-python-client
echo "✅ Dependencies installed"
echo ""

# Prompt for YouTube credentials path
echo "🔑 YouTube API Setup"
echo "-------------------"
echo "Do you have a YouTube API credentials JSON file?"
echo "(Get it from: https://console.cloud.google.com/ → YouTube Data API v3 → OAuth 2.0)"
echo ""
read -p "Enter path to credentials.json (or press Enter to skip): " CREDS_PATH

if [ ! -z "$CREDS_PATH" ]; then
    if [ ! -f "$CREDS_PATH" ]; then
        echo "❌ File not found: $CREDS_PATH"
        exit 1
    fi
    mkdir -p ~/.openclaw
    cp "$CREDS_PATH" ~/.openclaw/youtube-credentials.json
    echo "✅ Credentials saved to ~/.openclaw/youtube-credentials.json"
else
    echo "⚠️  Skipping credentials setup. You can add them manually later."
    echo "   Copy your JSON file to: ~/.openclaw/youtube-credentials.json"
fi

echo ""

# Prompt for channel ID
echo "📺 Concessa Obvius Channel ID"
echo "----------------------------"
read -p "Enter the YouTube channel ID (starts with 'UC'): " CHANNEL_ID

if [ ! -z "$CHANNEL_ID" ]; then
    # Check if it looks like a valid channel ID
    if [[ $CHANNEL_ID =~ ^UC[a-zA-Z0-9_-]+$ ]]; then
        echo "export YOUTUBE_CHANNEL_ID=\"$CHANNEL_ID\"" >> ~/.zshrc
        echo "export YOUTUBE_CHANNEL_ID=\"$CHANNEL_ID\"" >> ~/.bashrc
        export YOUTUBE_CHANNEL_ID="$CHANNEL_ID"
        echo "✅ Channel ID saved to shell profile"
    else
        echo "❌ Invalid channel ID format. Should start with 'UC'"
        exit 1
    fi
else
    echo "⚠️  Channel ID not set. You can set it manually:"
    echo "   export YOUTUBE_CHANNEL_ID=\"UCxxxxxxxx\""
fi

echo ""
echo "🚀 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Reload shell: source ~/.zshrc"
echo "2. Run monitor: python3 .cache/youtube-monitor.py"
echo "3. Check logs: .cache/youtube-comments.jsonl"
