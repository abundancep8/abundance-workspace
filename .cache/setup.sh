#!/bin/bash
# YouTube Comment Monitor - Complete Setup Script

set -e

CACHE_DIR="$HOME/.openclaw/workspace/.cache"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎬 YouTube Comment Monitor - Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Step 1: Check Python
echo -e "\n${YELLOW}[1/5]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.7+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Step 2: Install dependencies
echo -e "\n${YELLOW}[2/5]${NC} Installing dependencies..."
if [ -f "$CACHE_DIR/requirements.txt" ]; then
    pip install -q -r "$CACHE_DIR/requirements.txt"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}! Could not find requirements.txt, installing manually...${NC}"
    pip install -q google-auth-oauthlib google-auth-httplib2 google-api-python-client
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Step 3: Make scripts executable
echo -e "\n${YELLOW}[3/5]${NC} Preparing scripts..."
chmod +x "$CACHE_DIR/youtube_monitor.py"
chmod +x "$CACHE_DIR/report_generator.py"
echo -e "${GREEN}✓ Scripts ready${NC}"

# Step 4: Guide through OAuth setup
echo -e "\n${YELLOW}[4/5]${NC} OAuth 2.0 Setup"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$CACHE_DIR/youtube-credentials.json" ]; then
    echo -e "${GREEN}✓ Credentials already configured${NC}"
else
    echo ""
    echo "To enable the monitor, you need OAuth 2.0 credentials:"
    echo ""
    echo "1. Go to https://console.developers.google.com"
    echo "2. Create a new project"
    echo "3. Enable YouTube Data API v3"
    echo "4. Create OAuth 2.0 Desktop credentials"
    echo "5. Download as JSON"
    echo ""
    
    read -p "Ready to paste credentials path? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 "$CACHE_DIR/youtube_monitor.py" --setup-auth
    else
        echo -e "${YELLOW}⚠ Skipping auth setup. Run this later:${NC}"
        echo "  python3 $CACHE_DIR/youtube_monitor.py --setup-auth"
    fi
fi

# Step 5: Cron installation
echo -e "\n${YELLOW}[5/5]${NC} Cron Scheduler"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

read -p "Install cron job to run every 30 minutes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    bash "$CACHE_DIR/CRON_CONFIG.sh"
    echo -e "${GREEN}✓ Cron job installed${NC}"
else
    echo -e "${YELLOW}⚠ To install later, run:${NC}"
    echo "  bash $CACHE_DIR/CRON_CONFIG.sh"
fi

# Summary
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "1. Test a single run:"
echo "   python3 $CACHE_DIR/youtube_monitor.py"
echo ""
echo "2. View the report:"
echo "   python3 $CACHE_DIR/report_generator.py"
echo ""
echo "3. Check logs:"
echo "   tail -f $CACHE_DIR/cron.log"
echo ""
echo "📖 Full documentation: $CACHE_DIR/README.md"
