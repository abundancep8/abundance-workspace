#!/bin/bash
# YouTube Monitor Cron Installer

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}YouTube Comment Monitor - Cron Installer${NC}"
echo

# Check if already configured
if grep -q "youtube-monitor" /var/spool/cron/tabs/$USER 2>/dev/null; then
    echo -e "${YELLOW}⚠ Cron already configured${NC}"
    echo "Run 'crontab -e' to view or modify"
    exit 0
fi

# Create environment file
ENV_FILE="$HOME/.config/openclaw/youtube-monitor.env"
mkdir -p "$(dirname "$ENV_FILE")"

echo -e "${BLUE}Setting up environment file: $ENV_FILE${NC}"

if [ ! -f "$ENV_FILE" ]; then
    read -p "Enter YouTube API Key: " API_KEY
    read -p "Enter YouTube Channel ID (or press Enter for default): " CHANNEL_ID
    
    cat > "$ENV_FILE" << EOF
export YOUTUBE_API_KEY="$API_KEY"
export YOUTUBE_CHANNEL_ID="${CHANNEL_ID:-UCH-I6yRUDqt8TL-d7gGp7ow}"
EOF
    
    chmod 600 "$ENV_FILE"
    echo -e "${GREEN}✓ Created $ENV_FILE${NC}"
else
    echo -e "${YELLOW}✓ Using existing $ENV_FILE${NC}"
fi

# Get workspace path
WORKSPACE="/Users/abundance/.openclaw/workspace"

# Create cron entry
CRON_ENTRY="*/30 * * * * cd $WORKSPACE && source $ENV_FILE && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1"

# Install cron
echo -e "${BLUE}Installing cron job (every 30 minutes)...${NC}"

# Get current crontab or create empty
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Add new entry
echo "$CRON_ENTRY" >> "$TEMP_CRON"

# Install
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo -e "${GREEN}✓ Cron installed successfully${NC}"
echo
echo -e "${BLUE}Cron Details:${NC}"
echo "  Schedule:   Every 30 minutes"
echo "  Script:     $WORKSPACE/.cache/youtube-monitor.py"
echo "  Log File:   $WORKSPACE/.cache/youtube-monitor.log"
echo "  Environment: $ENV_FILE"
echo
echo -e "${BLUE}Management:${NC}"
echo "  View crontab:    crontab -l"
echo "  Edit crontab:    crontab -e"
echo "  Remove cron:     crontab -r"
echo "  Check log:       tail -f .cache/youtube-monitor.log"
echo
echo -e "${GREEN}✓ Setup complete!${NC}"
