#!/bin/bash
# Install YouTube Comment Monitor for automatic scheduling

set -e

WORKSPACE="${HOME}/.openclaw/workspace"
PLIST="${WORKSPACE}/com.youtube-monitor.plist"
AGENTS_DIR="${HOME}/Library/LaunchAgents"
AGENT_PLIST="${AGENTS_DIR}/com.youtube-monitor.plist"

echo "🚀 Installing YouTube Comment Monitor"
echo "====================================="
echo ""

# Check prerequisites
echo "1️⃣  Checking prerequisites..."

CREDS="${HOME}/.openclaw/youtube-credentials.json"
if [ ! -f "$CREDS" ]; then
    echo ""
    echo "❌ YouTube credentials not found!"
    echo "   Path: $CREDS"
    echo ""
    echo "   Steps to get credentials:"
    echo "   1. Go to https://console.cloud.google.com/"
    echo "   2. Create a new project"
    echo "   3. Enable YouTube Data API v3"
    echo "   4. Create OAuth2 Desktop Credentials"
    echo "   5. Download JSON and save to: $CREDS"
    echo ""
    echo "   📖 See YOUTUBE-MONITOR-SETUP.md for detailed steps"
    exit 1
fi
echo "   ✅ Credentials found"

if ! python3 -c "import google.oauth2.credentials" 2>/dev/null; then
    echo ""
    echo "❌ Google API libraries not installed"
    echo "   Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    exit 1
fi
echo "   ✅ Python libraries installed"

if [ ! -f "$PLIST" ]; then
    echo ""
    echo "❌ LaunchAgent plist not found: $PLIST"
    exit 1
fi
echo "   ✅ LaunchAgent config found"

# Create LaunchAgents directory if needed
mkdir -p "$AGENTS_DIR"

# Copy plist
echo ""
echo "2️⃣  Installing LaunchAgent..."
cp "$PLIST" "$AGENT_PLIST"
echo "   ✅ Copied to: $AGENT_PLIST"

# Unload if already loaded
if launchctl list | grep -q "com.youtube-monitor"; then
    echo "   ⚠️  Monitor already installed, reloading..."
    launchctl unload "$AGENT_PLIST" 2>/dev/null || true
fi

# Load new plist
launchctl load "$AGENT_PLIST"
echo "   ✅ LaunchAgent loaded"

# Start monitor
launchctl start com.youtube-monitor
echo "   ✅ Monitor started"

# Verify
echo ""
echo "3️⃣  Verifying installation..."
sleep 1
if launchctl list | grep -q "com.youtube-monitor"; then
    echo "   ✅ Monitor is running"
else
    echo "   ⚠️  Monitor may not be running"
fi

# Check log
LOG="${WORKSPACE}/.cache/youtube-monitor.log"
mkdir -p "${WORKSPACE}/.cache"
if [ -f "$LOG" ]; then
    LAST_LINE=$(tail -1 "$LOG")
    echo "   📝 Last log entry: $LAST_LINE"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📊 Next steps:"
echo "   • Monitor will run every 30 minutes automatically"
echo "   • Check results: tail ${WORKSPACE}/.cache/youtube-comments.jsonl"
echo "   • View log: tail ${WORKSPACE}/.cache/youtube-monitor.log"
echo "   • View report: bash ${WORKSPACE}/scripts/test-youtube-monitor.sh"
echo ""
echo "🛑 To stop: launchctl stop com.youtube-monitor"
echo "🔄 To restart: launchctl start com.youtube-monitor"
echo ""
echo "📖 Full docs: YOUTUBE-MONITOR-README.md"
