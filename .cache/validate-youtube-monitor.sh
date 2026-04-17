#!/bin/bash
# Validate YouTube Monitor Setup

echo "🔍 YouTube Comment Monitor - Setup Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
PASSED=0
FAILED=0

# Check 1: Monitor script exists
echo -n "✓ Monitor script: "
if [ -f "$CACHE_DIR/youtube-monitor.py" ]; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "❌ MISSING"
    FAILED=$((FAILED+1))
fi

# Check 2: Cron runner script exists
echo -n "✓ Cron runner script: "
if [ -f "$CACHE_DIR/youtube-monitor-cron.sh" ]; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "❌ MISSING"
    FAILED=$((FAILED+1))
fi

# Check 3: Cron runner is executable
echo -n "✓ Cron script executable: "
if [ -x "$CACHE_DIR/youtube-monitor-cron.sh" ]; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "❌ NOT EXECUTABLE"
    FAILED=$((FAILED+1))
fi

# Check 4: Config file exists
echo -n "✓ Config file: "
if [ -f "$CACHE_DIR/youtube-monitor-config.json" ]; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "❌ MISSING (optional)"
fi

# Check 5: Cache directory writable
echo -n "✓ Cache directory writable: "
if [ -w "$CACHE_DIR" ]; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "❌ NOT WRITABLE"
    FAILED=$((FAILED+1))
fi

# Check 6: Comments log exists
echo -n "✓ Comments log file: "
if [ -f "$CACHE_DIR/youtube-comments.jsonl" ]; then
    LINES=$(wc -l < "$CACHE_DIR/youtube-comments.jsonl")
    echo "✅ ($LINES entries)"
    PASSED=$((PASSED+1))
else
    echo "⚠️  Not yet created (will be on first run)"
fi

# Check 7: Python3 available
echo -n "✓ Python 3: "
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ ($VERSION)"
    PASSED=$((PASSED+1))
else
    echo "❌ NOT FOUND"
    FAILED=$((FAILED+1))
fi

# Check 8: YouTube API libraries
echo -n "✓ Google API libraries: "
if python3 -c "import google.auth" 2>/dev/null && \
   python3 -c "from googleapiclient.discovery import build" 2>/dev/null; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "⚠️  NOT INSTALLED - Install with: pip install google-api-python-client google-auth-oauthlib"
fi

# Check 9: Cron job installed
echo -n "✓ Cron job scheduled: "
if crontab -l 2>/dev/null | grep -q "youtube-monitor-cron.sh"; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "⚠️  Not installed yet - Run setup command"
fi

# Check 10: YouTube credentials
echo -n "✓ YouTube API credentials: "
if [ -n "$YOUTUBE_CREDS_FILE" ] && [ -f "$YOUTUBE_CREDS_FILE" ]; then
    echo "✅ ($YOUTUBE_CREDS_FILE)"
    PASSED=$((PASSED+1))
elif [ -f "$HOME/.openclaw/credentials/youtube.json" ]; then
    echo "✅"
    PASSED=$((PASSED+1))
else
    echo "⚠️  Not configured - Set YOUTUBE_CREDS_FILE or place in ~/.openclaw/credentials/youtube.json"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary: $PASSED passed, $FAILED failed"

if [ $FAILED -eq 0 ]; then
    echo "✅ System is ready to monitor comments!"
    exit 0
else
    echo "❌ Fix the issues above before starting"
    exit 1
fi
