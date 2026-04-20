#!/bin/bash
# Quick installation script for YouTube Comment Monitor

set -e

echo "🚀 Installing YouTube Comment Monitor..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.8+"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --quiet google-auth google-api-python-client

# Create cache directory
mkdir -p .cache

# Copy/verify script
if [ ! -f .cache/youtube-monitor.py ]; then
    echo "❌ youtube-monitor.py not found"
    exit 1
fi

chmod +x .cache/youtube-monitor.py

# Check for API key
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo ""
    echo "⚠️  YOUTUBE_API_KEY not set"
    echo ""
    echo "Get your API key:"
    echo "  1. Go to https://console.cloud.google.com/"
    echo "  2. Create a project or select existing"
    echo "  3. Enable 'YouTube Data API v3'"
    echo "  4. Create API Key credentials"
    echo "  5. Export: export YOUTUBE_API_KEY='your-key-here'"
    echo ""
else
    echo "✅ YOUTUBE_API_KEY found"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Test run:"
echo "  python3 .cache/youtube-monitor.py"
echo ""
echo "View logs:"
echo "  jq . .cache/youtube-comments.jsonl"
