#!/bin/bash
# YouTube Comment Monitor - Cron Setup Helper
# Usage: bash youtube-cron-setup.sh [install|remove|status]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/youtube-monitor.js"
LOG_FILE="$SCRIPT_DIR/youtube-monitor.log"
CRON_ID="youtube-comment-monitor"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get API key from environment or prompt
get_api_key() {
  if [ -z "$YOUTUBE_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  YOUTUBE_API_KEY not set in environment${NC}"
    echo "Please enter your YouTube API key (or press Enter to skip):"
    read -s API_KEY
    if [ -z "$API_KEY" ]; then
      echo "❌ API key required to proceed"
      exit 1
    fi
  else
    API_KEY="$YOUTUBE_API_KEY"
  fi
}

# Install cron job
install_cron() {
  get_api_key
  
  echo -e "${YELLOW}Installing cron job to run every 30 minutes...${NC}"
  
  # Create the cron entry
  CRON_ENTRY="*/30 * * * * export YOUTUBE_API_KEY='$API_KEY' && node $MONITOR_SCRIPT >> $LOG_FILE 2>&1"
  
  # Check if cron job already exists
  if crontab -l 2>/dev/null | grep -q "$CRON_ID"; then
    echo -e "${RED}Cron job already exists. Remove first with: $0 remove${NC}"
    exit 1
  fi
  
  # Add to crontab
  (crontab -l 2>/dev/null; echo "# $CRON_ID") | crontab -
  (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cron job installed successfully${NC}"
    echo "   Runs every 30 minutes"
    echo "   Log file: $LOG_FILE"
    status_cron
  else
    echo -e "${RED}❌ Failed to install cron job${NC}"
    exit 1
  fi
}

# Remove cron job
remove_cron() {
  echo -e "${YELLOW}Removing cron job...${NC}"
  
  if ! crontab -l 2>/dev/null | grep -q "$MONITOR_SCRIPT"; then
    echo -e "${RED}Cron job not found${NC}"
    exit 1
  fi
  
  # Remove the cron entry
  crontab -l | grep -v "$MONITOR_SCRIPT" | crontab -
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cron job removed${NC}"
  else
    echo -e "${RED}❌ Failed to remove cron job${NC}"
    exit 1
  fi
}

# Check cron status
status_cron() {
  echo ""
  echo -e "${YELLOW}Current Cron Jobs:${NC}"
  crontab -l 2>/dev/null | grep -E "$MONITOR_SCRIPT|$CRON_ID" || echo "No YouTube monitor cron jobs found"
  
  echo ""
  if [ -f "$LOG_FILE" ]; then
    echo -e "${YELLOW}Recent Log Activity:${NC}"
    tail -5 "$LOG_FILE"
  else
    echo -e "${YELLOW}No log file yet (job hasn't run)${NC}"
  fi
}

# Test run
test_run() {
  get_api_key
  echo -e "${YELLOW}Running test...${NC}"
  export YOUTUBE_API_KEY="$API_KEY"
  node "$MONITOR_SCRIPT"
}

# Main
case "${1:-status}" in
  install)
    install_cron
    ;;
  remove)
    remove_cron
    ;;
  status)
    status_cron
    ;;
  test)
    test_run
    ;;
  *)
    echo "YouTube Comment Monitor - Cron Setup"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install  - Install cron job (runs every 30 min)"
    echo "  remove   - Remove cron job"
    echo "  status   - Show current cron job status"
    echo "  test     - Run monitor once for testing"
    echo ""
    echo "Environment:"
    echo "  YOUTUBE_API_KEY - Set this or you'll be prompted"
    echo ""
    exit 0
    ;;
esac
