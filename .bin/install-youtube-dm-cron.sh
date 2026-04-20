#!/bin/bash
##############################################################################
# YouTube DM Monitor — Install Hourly Cron Job
# 
# This script installs the hourly YouTube DM monitor as a launchd service
# on macOS or a cron job on Linux.
#
# Usage: ./install-youtube-dm-cron.sh
##############################################################################

set -e

WORKSPACE="$HOME/.openclaw/workspace"
BIN_DIR="$WORKSPACE/.bin"
CACHE_DIR="$WORKSPACE/.cache"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    YouTube DM Monitor — Hourly Cron Job Installer         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for required files
echo -e "${YELLOW}Checking prerequisites...${NC}"
if [ ! -f "$BIN_DIR/youtube-dm-hourly-monitor.py" ]; then
    echo -e "${RED}✗ Monitor script not found at $BIN_DIR/youtube-dm-hourly-monitor.py${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Monitor script found${NC}"

# Make scripts executable
chmod +x "$BIN_DIR/youtube-dm-hourly-monitor.py"
chmod +x "$BIN_DIR/youtube-dm-ingester.py"
echo -e "${GREEN}✓ Scripts made executable${NC}"

# Create cache directory
mkdir -p "$CACHE_DIR"
echo -e "${GREEN}✓ Cache directory ready${NC}"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo ""
    echo -e "${YELLOW}macOS detected — Setting up launchd service${NC}"
    
    PLIST_FILE="$HOME/Library/LaunchAgents/com.openclaw.youtube-dm-monitor.plist"
    
    cat > "$PLIST_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.youtube-dm-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{{WORKSPACE}}/.bin/youtube-dm-hourly-monitor.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{{WORKSPACE}}</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>{{WORKSPACE}}/.cache/youtube-dm-cron.log</string>
    <key>StandardErrorPath</key>
    <string>{{WORKSPACE}}/.cache/youtube-dm-cron-error.log</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

    # Replace placeholders
    sed -i '' "s|{{WORKSPACE}}|$WORKSPACE|g" "$PLIST_FILE"
    
    # Load the service
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    launchctl load "$PLIST_FILE"
    
    echo -e "${GREEN}✓ Installed launchd service${NC}"
    echo -e "${GREEN}✓ Service will run every hour starting now${NC}"
    
else
    # Linux
    echo ""
    echo -e "${YELLOW}Linux detected — Setting up cron job${NC}"
    
    # Add to crontab
    CRON_JOB="0 * * * * cd $WORKSPACE && python3 .bin/youtube-dm-hourly-monitor.py >> .cache/youtube-dm-cron.log 2>&1"
    
    # Check if already exists
    if crontab -l 2>/dev/null | grep -q "youtube-dm-hourly-monitor"; then
        echo -e "${YELLOW}ⓘ Cron job already exists${NC}"
    else
        (crontab -l 2>/dev/null || true; echo "$CRON_JOB") | crontab -
        echo -e "${GREEN}✓ Cron job installed${NC}"
    fi
fi

# Initialize state file
STATE_FILE="$CACHE_DIR/youtube-dms-state.json"
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << 'EOF'
{
  "processed_ids": [],
  "processed_hashes": [],
  "last_run": null,
  "total_processed": 0,
  "total_responses": 0,
  "partnerships_flagged": 0,
  "last_check": null,
  "status": "initialized"
}
EOF
    echo -e "${GREEN}✓ State file initialized${NC}"
fi

# Create test DM for verification
TEST_INBOX="$CACHE_DIR/youtube-dm-inbox.jsonl"
echo "" >> "$TEST_INBOX" 2>/dev/null || touch "$TEST_INBOX"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ INSTALLATION COMPLETE                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 Quick Reference:${NC}"
echo "  DM Ingester:     $BIN_DIR/youtube-dm-ingester.py"
echo "  Cache Directory: $CACHE_DIR"
echo "  Log File:        $CACHE_DIR/youtube-dm-cron.log"
echo "  DM Log:          $CACHE_DIR/youtube-dms.jsonl"
echo "  Partnerships:    $CACHE_DIR/youtube-flagged-partnerships.jsonl"
echo "  Report:          $CACHE_DIR/youtube-dm-report.txt"
echo ""

echo -e "${BLUE}🚀 Test the Monitor:${NC}"
echo "  $ python3 $BIN_DIR/youtube-dm-hourly-monitor.py"
echo ""

echo -e "${BLUE}📝 Queue a Test DM:${NC}"
echo "  $ python3 $BIN_DIR/youtube-dm-ingester.py \\"
echo "    --sender 'Test User' \\"
echo "    --text 'I need help with setup' \\"
echo "    --id 'test_user'"
echo ""

echo -e "${BLUE}📋 View Recent Report:${NC}"
echo "  $ cat $CACHE_DIR/youtube-dm-report.txt"
echo ""

echo -e "${BLUE}🔍 Check DM Log:${NC}"
echo "  $ tail -20 $CACHE_DIR/youtube-dms.jsonl"
echo ""

echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "  1. Set up YouTube API credentials (if not already done)"
echo "  2. Configure email forwarding for DMs (optional)"
echo "  3. Test with a sample DM"
echo "  4. Monitor .cache/youtube-dm-report.txt for activity"
echo ""
