#!/bin/bash
# YouTube Comment Monitor - Setup Script

set -e

SCRIPT_DIR="$HOME/.openclaw/workspace/.cache"
SCRIPT="$SCRIPT_DIR/youtube-comment-monitor.py"

echo "=== YouTube Comment Monitor Setup ==="
echo ""

# 1. Check Python and dependencies
echo "[1/3] Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Install Python 3.8+"
    exit 1
fi

python3 -c "import google.auth" 2>/dev/null || {
    echo "Installing YouTube API client..."
    pip3 install --user google-auth-oauthlib google-auth-httplib2 google-api-python-client
}

echo "✓ Dependencies OK"
echo ""

# 2. Get YouTube API credentials
echo "[2/3] Setting up YouTube API credentials..."
echo ""
echo "You need a YouTube Data API key or OAuth credentials."
echo "Options:"
echo "  A) API Key (simplest, read-only)"
echo "  B) Service Account (OAuth, can post comments)"
echo ""
read -p "Choose (A/B): " choice

case "$choice" in
    A|a)
        read -p "Enter your YouTube Data API Key: " api_key
        export YOUTUBE_API_KEY="$api_key"
        echo "YOUTUBE_API_KEY=\"$api_key\"" >> ~/.zprofile
        ;;
    B|b)
        read -p "Path to service account JSON file: " creds_file
        if [ ! -f "$creds_file" ]; then
            echo "ERROR: File not found"
            exit 1
        fi
        export YOUTUBE_CREDENTIALS_JSON="$creds_file"
        echo "YOUTUBE_CREDENTIALS_JSON=\"$creds_file\"" >> ~/.zprofile
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo "✓ Credentials configured"
echo ""

# 3. Set channel ID
echo "[3/3] Setting up channel configuration..."
read -p "YouTube channel ID for 'Concessa Obvius' (or leave blank to auto-detect): " channel_id

if [ -n "$channel_id" ]; then
    export YOUTUBE_CHANNEL_ID="$channel_id"
    echo "YOUTUBE_CHANNEL_ID=\"$channel_id\"" >> ~/.zprofile
    echo "✓ Channel ID set"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To add cron job, run:"
echo "  crontab -e"
echo ""
echo "Then add this line:"
echo "  */30 * * * * cd $SCRIPT_DIR && python3 youtube-comment-monitor.py >> $SCRIPT_DIR/monitor.log 2>&1"
echo ""
echo "Test the script manually:"
echo "  python3 $SCRIPT"
echo ""
