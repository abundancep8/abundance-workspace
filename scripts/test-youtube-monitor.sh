#!/bin/bash
# Test script for YouTube Comment Monitor
# Checks setup and runs a single monitor cycle

set -e

echo "🔍 YouTube Comment Monitor - Setup Test"
echo "========================================"
echo ""

WORKSPACE="${HOME}/.openclaw/workspace"
CREDS="${HOME}/.openclaw/youtube-credentials.json"
SCRIPT="${WORKSPACE}/scripts/youtube-comment-monitor.py"

# Check 1: Credentials file
echo "1️⃣  Checking credentials..."
if [ -f "$CREDS" ]; then
    echo "   ✅ Found: $CREDS"
else
    echo "   ❌ MISSING: $CREDS"
    echo "   📖 See YOUTUBE-MONITOR-SETUP.md for instructions"
    exit 1
fi

# Check 2: Python libraries
echo ""
echo "2️⃣  Checking Python libraries..."
if python3 -c "import google.oauth2.credentials" 2>/dev/null; then
    echo "   ✅ google-auth libraries installed"
else
    echo "   ❌ Missing google-auth libraries"
    echo "   💾 Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    exit 1
fi

# Check 3: Script exists
echo ""
echo "3️⃣  Checking monitor script..."
if [ -f "$SCRIPT" ]; then
    echo "   ✅ Found: $SCRIPT"
else
    echo "   ❌ MISSING: $SCRIPT"
    exit 1
fi

# Check 4: Workspace directory
echo ""
echo "4️⃣  Checking workspace..."
if [ -d "$WORKSPACE" ]; then
    echo "   ✅ Workspace: $WORKSPACE"
else
    echo "   ❌ MISSING workspace"
    exit 1
fi

# Check 5: Cache directory
echo ""
echo "5️⃣  Checking cache directory..."
mkdir -p "${WORKSPACE}/.cache"
echo "   ✅ Cache: ${WORKSPACE}/.cache"

# Run test
echo ""
echo "6️⃣  Running monitor (one cycle)..."
echo "   (First run will prompt for browser authorization)"
echo ""

cd "$WORKSPACE"
python3 "$SCRIPT"

# Check results
echo ""
echo "7️⃣  Checking results..."
LOG="${WORKSPACE}/.cache/youtube-comments.jsonl"
if [ -f "$LOG" ]; then
    COUNT=$(wc -l < "$LOG")
    echo "   ✅ Log file created: $LOG"
    echo "   📊 Entries: $COUNT"
else
    echo "   ⚠️  No log file yet (may need to wait for next run)"
fi

echo ""
echo "✅ Setup test complete!"
echo ""
echo "Next: Set up cron or LaunchAgent for every 30 minutes."
echo "📖 See YOUTUBE-MONITOR-SETUP.md for scheduler instructions."
