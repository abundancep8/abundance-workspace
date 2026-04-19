#!/bin/bash
# YouTube Comment Monitor - Setup Script
# Run this script to install dependencies and configure cron job

set -e

echo "=== YouTube Comment Monitor Setup ==="
echo

# Check Python
echo "✓ Checking Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
python3 --version
echo

# Install dependencies
echo "✓ Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo

# Make script executable
echo "✓ Making script executable..."
chmod +x youtube-comment-monitor.py
echo "✓ Script is now executable"
echo

# Create directories
echo "✓ Creating log directories..."
mkdir -p .state .cache
echo "✓ Directories created"
echo

# Test the API key
echo "⚠️  API Key Setup"
echo "━━━━━━━━━━━━━━━━"
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "YOUTUBE_API_KEY environment variable not set."
    echo
    echo "To get your API key:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a new project"
    echo "3. Enable 'YouTube Data API v3'"
    echo "4. Create an API key in Credentials"
    echo "5. Set: export YOUTUBE_API_KEY='your_key_here'"
    echo
    echo "Then run: python3 youtube-comment-monitor.py"
else
    echo "✓ YOUTUBE_API_KEY is set"
    
    # Test the script
    echo
    echo "✓ Testing script with API key..."
    python3 youtube-comment-monitor.py
    echo "✓ Script test successful!"
fi
echo

# Cron setup
echo "⚠️  Cron Job Setup"
echo "━━━━━━━━━━━━━━━━"
echo "To install as a cron job:"
echo "1. Edit youtube-monitor.cron"
echo "2. Replace YOUR_API_KEY_HERE with your actual API key"
echo "3. Run: crontab -e"
echo "4. Paste one of the lines from youtube-monitor.cron"
echo "5. Save and exit"
echo
echo "Example (every 30 minutes):"
echo "*/30 * * * * export YOUTUBE_API_KEY='your_key' && cd $(pwd) && python3 youtube-comment-monitor.py >> .cache/youtube-monitor-cron.log 2>&1"
echo

echo "=== Setup Complete ==="
echo
echo "Next steps:"
echo "1. Configure your API key in the cron entry"
echo "2. Test: python3 youtube-comment-monitor.py"
echo "3. Install cron job: crontab -e"
echo "4. Monitor logs: tail -f .cache/youtube-monitor.log"
echo
