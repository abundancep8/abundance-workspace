#!/bin/bash
# Verify YouTube Comment Monitor setup

echo "🔍 YouTube Comment Monitor - Verification Check"
echo "=================================================="
echo ""

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
PASS="✅"
FAIL="❌"

# Check 1: Python dependencies
echo "1️⃣  Python Dependencies"
if python3 -c "import googleapiclient" 2>/dev/null; then
    echo "   $PASS Google API client installed"
else
    echo "   $FAIL Missing: pip install google-api-python-client"
fi

if python3 -c "import google.oauth2" 2>/dev/null; then
    echo "   $PASS Google auth libraries installed"
else
    echo "   $FAIL Missing: pip install google-auth-oauthlib"
fi
echo ""

# Check 2: Config file
echo "2️⃣  Configuration Files"
if [ -f "$WORKSPACE/youtube-monitor-config.json" ]; then
    echo "   $PASS Config file exists"
    CHANNEL_ID=$(jq -r '.channel_id' "$WORKSPACE/youtube-monitor-config.json" 2>/dev/null || echo "")
    if [ "$CHANNEL_ID" != "CHANNEL_ID_HERE" ] && [ ! -z "$CHANNEL_ID" ]; then
        echo "   $PASS Channel ID configured: $CHANNEL_ID"
    else
        echo "   $FAIL Channel ID not set (see setup guide)"
    fi
else
    echo "   $FAIL Config file missing"
fi
echo ""

# Check 3: Credentials
echo "3️⃣  Google OAuth Credentials"
if [ -f "$CACHE_DIR/credentials.json" ]; then
    echo "   $PASS OAuth credentials file found"
else
    echo "   ⚠️  OAuth credentials not set up (needed for first run)"
fi

if [ -f "$CACHE_DIR/youtube-token.json" ]; then
    echo "   $PASS Authentication token exists (already authorized)"
else
    echo "   ℹ️  No token yet (will be created on first run)"
fi
echo ""

# Check 4: Main scripts
echo "4️⃣  Scripts"
scripts=("youtube-comment-monitor.py" "youtube-monitor-report.py" "youtube-monitor-install.sh")
for script in "${scripts[@]}"; do
    if [ -f "$CACHE_DIR/$script" ]; then
        if [ -x "$CACHE_DIR/$script" ]; then
            echo "   $PASS $script (executable)"
        else
            echo "   ⚠️  $script (not executable, fixing...)"
            chmod +x "$CACHE_DIR/$script"
        fi
    else
        echo "   $FAIL Missing: $script"
    fi
done
echo ""

# Check 5: Log files
echo "5️⃣  Log Files"
if [ -f "$CACHE_DIR/youtube-comments.jsonl" ]; then
    COUNT=$(wc -l < "$CACHE_DIR/youtube-comments.jsonl")
    echo "   $PASS youtube-comments.jsonl ($COUNT entries)"
else
    echo "   ℹ️  youtube-comments.jsonl (will be created on first run)"
fi

if [ -f "$CACHE_DIR/youtube-monitor.log" ]; then
    echo "   $PASS youtube-monitor.log exists"
else
    echo "   ℹ️  youtube-monitor.log (will be created by cron)"
fi

if [ -f "$CACHE_DIR/seen-comment-ids.json" ]; then
    echo "   $PASS seen-comment-ids.json (dedup tracking)"
else
    echo "   ℹ️  seen-comment-ids.json (created on first run)"
fi
echo ""

# Check 6: Cron job
echo "6️⃣  Cron Job"
if crontab -l 2>/dev/null | grep -q "youtube-comment-monitor"; then
    echo "   $PASS Cron job installed"
    echo "   Details:"
    crontab -l 2>/dev/null | grep "youtube-comment-monitor" | sed 's/^/      /'
else
    echo "   ⚠️  Cron job not installed (run setup script to add)"
fi
echo ""

# Check 7: Directories
echo "7️⃣  Directories"
if [ -d "$WORKSPACE" ]; then
    echo "   $PASS Workspace: $WORKSPACE"
else
    echo "   $FAIL Workspace directory missing"
fi

if [ -d "$CACHE_DIR" ]; then
    echo "   $PASS Cache directory: $CACHE_DIR"
else
    echo "   $FAIL Cache directory missing"
fi
echo ""

# Summary
echo "=================================================="
echo "✨ Setup Status Summary"
echo ""
echo "To complete setup:"
echo "1. bash $CACHE_DIR/youtube-monitor-install.sh"
echo ""
echo "To test manually:"
echo "   python3 $CACHE_DIR/youtube-comment-monitor.py"
echo ""
echo "To view reports:"
echo "   python3 $CACHE_DIR/youtube-monitor-report.py"
echo ""
echo "Full guide: $WORKSPACE/YOUTUBE-MONITOR-GUIDE.md"
echo "=================================================="
