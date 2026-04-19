#!/bin/bash
# YouTube Comment Monitor - Verification Script
# Run this to check that everything is set up correctly

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
cd "$WORKSPACE"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  YouTube Comment Monitor - Verification Suite                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2 (NOT FOUND: $1)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2 (NOT FOUND: $1)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check if file is executable
check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2 (NOT EXECUTABLE: $1)"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check Python dependencies
check_python_dep() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python module: $1"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} Python module missing: $1"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 FILE STRUCTURE CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "scripts/youtube-comment-monitor.py" "Main monitor script"
check_file "scripts/youtube-monitor-cron.sh" "Cron launcher script"
check_file ".secrets/youtube-credentials.json" "OAuth2 credentials"
check_file ".secrets/youtube-token.json" "OAuth2 token"
check_dir ".cache" "Cache directory"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 EXECUTABLE PERMISSIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_executable "scripts/youtube-comment-monitor.py" "Monitor script is executable"
check_executable "scripts/youtube-monitor-cron.sh" "Cron launcher is executable"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 PYTHON DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_python_dep "google.auth" "google-auth"
check_python_dep "google.oauth2" "google-auth"
check_python_dep "google_auth_oauthlib" "google-auth-oauthlib"
check_python_dep "googleapiclient" "google-api-python-client"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  CONFIGURATION CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file ".youtube-monitor-config.json" "Monitor configuration file"

# Check if channel ID is configured in the script
if grep -q "UC326742c_CXvNQ6IcnZ8Jkw" scripts/youtube-comment-monitor.py; then
    echo -e "${GREEN}✓${NC} Channel ID configured correctly"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Channel ID not properly configured"
    ((CHECKS_FAILED++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 LOG & CACHE CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if cache directory is writable
if [ -w ".cache" ]; then
    echo -e "${GREEN}✓${NC} Cache directory is writable"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Cache directory is not writable"
    ((CHECKS_FAILED++))
fi

# Check if comment log exists
if [ -f ".cache/youtube-comments.jsonl" ]; then
    LINE_COUNT=$(wc -l < ".cache/youtube-comments.jsonl")
    echo -e "${GREEN}✓${NC} Comment log exists ($LINE_COUNT entries)"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Comment log doesn't exist yet (will be created on first run)"
fi

# Check if report exists
if [ -f ".cache/youtube-comments-report.txt" ]; then
    echo -e "${GREEN}✓${NC} Report file exists"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Report file doesn't exist yet (will be created on first run)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📅 CRON JOB CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if crontab -l 2>/dev/null | grep -q "youtube-monitor-cron.sh"; then
    echo -e "${GREEN}✓${NC} Cron job is installed"
    ((CHECKS_PASSED++))
    echo ""
    echo "  Current cron job:"
    crontab -l 2>/dev/null | grep "youtube-monitor-cron.sh" | sed 's/^/    /'
else
    echo -e "${YELLOW}⚠${NC}  Cron job is NOT installed yet"
    echo ""
    echo "  To install, run:"
    echo "    crontab -e"
    echo ""
    echo "  Then add this line:"
    echo "    */30 * * * * /Users/abundance/.openclaw/workspace/scripts/youtube-monitor-cron.sh >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron-exec.log 2>&1"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TOTAL=$((CHECKS_PASSED + CHECKS_FAILED))
echo ""
echo "Checks Passed: ${GREEN}$CHECKS_PASSED${NC} / $TOTAL"
echo "Checks Failed: ${RED}$CHECKS_FAILED${NC} / $TOTAL"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Your YouTube Comment Monitor is ready! 🎉"
    echo ""
    echo "Next steps:"
    echo "  1. Install the cron job: crontab -e (if not already installed)"
    echo "  2. Test the monitor: python3 scripts/youtube-comment-monitor.py"
    echo "  3. Check the report: cat .cache/youtube-comments-report.txt"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME CHECKS FAILED${NC}"
    echo ""
    echo "Please fix the issues above and run this script again."
    echo ""
    exit 1
fi
