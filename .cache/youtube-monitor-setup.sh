#!/bin/bash

# YouTube Comment Monitor - Setup Helper
# Quick setup script for OpenClaw YouTube monitor

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SECRETS_DIR="${HOME}/.openclaw/secrets"
CREDENTIALS_FILE="${SECRETS_DIR}/youtube.json"
MONITOR_SCRIPT="${SCRIPT_DIR}/youtube-comment-monitor.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   YouTube Comment Monitor - OpenClaw Setup Helper          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
echo -e "${YELLOW}1. Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Install Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check dependencies
echo -e "\n${YELLOW}2. Checking dependencies...${NC}"
REQUIRED_PACKAGES=("google-auth-oauthlib" "google-auth-httplib2" "google-api-python-client")
MISSING=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import ${package//-/_}" 2>/dev/null; then
        MISSING+=("$package")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing packages: ${MISSING[*]}${NC}"
    pip3 install "${MISSING[@]}"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ All dependencies found${NC}"
fi

# Create secrets directory
echo -e "\n${YELLOW}3. Setting up credentials directory...${NC}"
mkdir -p "$SECRETS_DIR"
echo -e "${GREEN}✓ Directory ready: ${SECRETS_DIR}${NC}"

# Check for existing credentials
if [ -f "$CREDENTIALS_FILE" ]; then
    echo -e "\n${GREEN}✓ Credentials file found: ${CREDENTIALS_FILE}${NC}"
else
    echo -e "\n${YELLOW}⚠ No credentials found at: ${CREDENTIALS_FILE}${NC}"
    echo -e "${YELLOW}You need to:${NC}"
    echo "  1. Go to https://console.cloud.google.com"
    echo "  2. Create a new project"
    echo "  3. Enable 'YouTube Data API v3'"
    echo "  4. Create OAuth2 credentials (Desktop app)"
    echo "  5. Download and save to: ${CREDENTIALS_FILE}"
    echo ""
    echo -e "${YELLOW}Need help? Run:${NC} python3 ${MONITOR_SCRIPT} --setup"
fi

# Test credentials if present
if [ -f "$CREDENTIALS_FILE" ]; then
    echo -e "\n${YELLOW}4. Testing credentials...${NC}"
    if python3 "$MONITOR_SCRIPT" --dry-run > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Credentials are valid${NC}"
    else
        echo -e "${RED}✗ Credentials test failed. Check your API key.${NC}"
        exit 1
    fi
fi

# Make scripts executable
chmod +x "$MONITOR_SCRIPT" 2>/dev/null || true

# Summary
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

echo "Next steps:"
echo -e "  ${BLUE}1. Add credentials:${NC}"
echo -e "     • Go to: https://console.cloud.google.com"
echo -e "     • Create OAuth2 credentials (Desktop app)"
echo -e "     • Save JSON to: ${CREDENTIALS_FILE}"
echo ""
echo -e "  ${BLUE}2. Test the monitor:${NC}"
echo -e "     python3 ${MONITOR_SCRIPT} --dry-run"
echo ""
echo -e "  ${BLUE}3. Run it:${NC}"
echo -e "     python3 ${MONITOR_SCRIPT}"
echo ""
echo -e "  ${BLUE}4. View logs:${NC}"
echo -e "     • Comments: tail -f ~/.openclaw/workspace/.cache/youtube-comments.jsonl"
echo -e "     • Errors: tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log"
echo ""
echo -e "  ${BLUE}5. Integrate with OpenClaw:${NC}"
echo -e "     • Add to HEARTBEAT.md for periodic runs"
echo -e "     • Or use cron for fixed schedules"
echo ""
echo -e "Documentation: ${SCRIPT_DIR}/YOUTUBE-MONITOR-README.md"
