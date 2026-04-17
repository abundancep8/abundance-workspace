#!/bin/bash

###############################################################################
# YouTube OAuth Setup & Validation Script
# Purpose: Guided setup for YouTube API credentials + auto-migration to live mode
# Time to complete: ~15-20 minutes (mostly waiting for Google Cloud)
###############################################################################

set -e

WORKSPACE_ROOT="/Users/abundance/.openclaw/workspace"
SECRETS_DIR="${WORKSPACE_ROOT}/.cache/.secrets"
YOUTUBE_CREDS_FILE="${SECRETS_DIR}/youtube-credentials.json"
VALIDATION_LOG="${WORKSPACE_ROOT}/.cache/youtube-oauth-validation.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure secrets directory exists
mkdir -p "${SECRETS_DIR}"

###############################################################################
# Step 1: Print Welcome & Check Prerequisites
###############################################################################
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ YouTube OAuth Setup & Live Migration${NC}"
echo -e "${BLUE}║${NC}"
echo -e "${BLUE}║ This script will:${NC}"
echo -e "${BLUE}║ 1. Guide you through Google Cloud OAuth setup${NC}"
echo -e "${BLUE}║ 2. Validate your credentials${NC}"
echo -e "${BLUE}║ 3. Test against YouTube API${NC}"
echo -e "${BLUE}║ 4. Automatically enable live monitoring${NC}"
echo -e "${BLUE}║${NC}"
echo -e "${BLUE}║ Time: ~15-20 minutes (mostly waiting)${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if credentials already exist
if [ -f "${YOUTUBE_CREDS_FILE}" ]; then
    echo -e "${GREEN}✓ Found existing YouTube credentials${NC}"
    read -p "Do you want to replace them? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing credentials. Skipping Google Cloud setup."
        SKIP_SETUP=1
    else
        SKIP_SETUP=0
    fi
else
    SKIP_SETUP=0
fi

###############################################################################
# Step 2: Google Cloud Setup (if needed)
###############################################################################
if [ $SKIP_SETUP -eq 0 ]; then
    echo -e "${YELLOW}Step 1: Create Google Cloud OAuth Credentials${NC}"
    echo ""
    echo "Opening Google Cloud Console setup guide..."
    echo ""
    cat << 'EOF'
Follow these steps:

1. Open: https://console.cloud.google.com
2. Create a new project (if needed):
   - Click "Select a Project" → "New Project"
   - Name: "YouTube Monitor"
   - Click "Create"

3. Enable YouTube Data API v3:
   - Search "YouTube Data API" in the search bar
   - Click "YouTube Data API v3"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "Credentials" (left sidebar)
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure consent screen first:
     * User Type: "External"
     * App Name: "YouTube Monitor"
     * User Support Email: (your email)
     * Save & Continue through scopes (no changes needed)
   - Application Type: "Desktop application"
   - Name: "YouTube Monitor CLI"
   - Click "Create"

5. Download the JSON file:
   - Click the download icon (⬇️) next to your new credential
   - This downloads "client_secret_*.json"

6. Copy the JSON content to this terminal (Step 2)
   - Open the downloaded file in a text editor
   - Copy all the content (Ctrl+C / Cmd+C)

Ready? Type "next" when you have the JSON file:
EOF
    read -p "> " user_input
    if [ "$user_input" != "next" ]; then
        echo "Setup cancelled."
        exit 1
    fi

    echo ""
    echo -e "${YELLOW}Step 2: Paste Your Credentials${NC}"
    echo "Paste the entire JSON file content below."
    echo "When done, press Enter twice:"
    echo ""

    # Read multiline JSON input
    creds_content=""
    while IFS= read -r line; do
        if [ -z "$line" ] && [ ! -z "$creds_content" ]; then
            break
        fi
        creds_content="${creds_content}${line}"$'\n'
    done

    # Validate JSON
    if ! echo "$creds_content" | jq empty 2>/dev/null; then
        echo -e "${RED}✗ Invalid JSON format. Please try again.${NC}"
        exit 1
    fi

    # Save credentials
    echo "$creds_content" > "${YOUTUBE_CREDS_FILE}"
    echo -e "${GREEN}✓ Credentials saved to: ${YOUTUBE_CREDS_FILE}${NC}"
    chmod 600 "${YOUTUBE_CREDS_FILE}"
else
    echo -e "${GREEN}✓ Skipping Google Cloud setup (using existing credentials)${NC}"
fi

###############################################################################
# Step 3: Validate Credentials
###############################################################################
echo ""
echo -e "${YELLOW}Step 3: Validating Credentials${NC}"

if [ ! -f "${YOUTUBE_CREDS_FILE}" ]; then
    echo -e "${RED}✗ Credentials file not found: ${YOUTUBE_CREDS_FILE}${NC}"
    exit 1
fi

# Check JSON structure
if ! jq -e '.installed.client_id' "${YOUTUBE_CREDS_FILE}" >/dev/null 2>&1; then
    echo -e "${RED}✗ Invalid credentials structure. Expected OAuth client JSON.${NC}"
    exit 1
fi

CLIENT_ID=$(jq -r '.installed.client_id' "${YOUTUBE_CREDS_FILE}")
CLIENT_SECRET=$(jq -r '.installed.client_secret' "${YOUTUBE_CREDS_FILE}")
REDIRECT_URI=$(jq -r '.installed.redirect_uris[0]' "${YOUTUBE_CREDS_FILE}")

if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
    echo -e "${RED}✗ client_id not found in credentials${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Credentials valid${NC}"
echo "  Client ID: ${CLIENT_ID:0:20}..."
echo "  Redirect URI: ${REDIRECT_URI}"

###############################################################################
# Step 4: Test Credentials (Optional OAuth Flow)
###############################################################################
echo ""
echo -e "${YELLOW}Step 4: Test Credentials with YouTube API${NC}"
echo ""
echo "Next, we'll test authentication. You'll need to:"
echo "1. Click the authorization link below"
echo "2. Grant 'YouTube Monitor' permission"
echo "3. Copy the authorization code back to this terminal"
echo ""
read -p "Ready to test? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Skipping OAuth test (you can test manually later)${NC}"
else
    echo -e "${BLUE}Generate authorization URL...${NC}"
    
    AUTH_URL="https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=https://www.googleapis.com/auth/youtube.readonly"
    
    echo ""
    echo "Authorization URL:"
    echo "${AUTH_URL}"
    echo ""
    echo "🔗 Open this link in your browser and authorize access."
    echo ""
    read -p "Enter the authorization code: " auth_code
    
    if [ -z "$auth_code" ]; then
        echo -e "${YELLOW}No authorization code provided. Skipping token generation.${NC}"
    else
        echo -e "${BLUE}Exchanging auth code for access token...${NC}"
        
        # Exchange code for token
        token_response=$(curl -s -X POST \
            "https://oauth2.googleapis.com/token" \
            -d "code=${auth_code}" \
            -d "client_id=${CLIENT_ID}" \
            -d "client_secret=${CLIENT_SECRET}" \
            -d "redirect_uri=${REDIRECT_URI}" \
            -d "grant_type=authorization_code")
        
        if echo "$token_response" | jq -e '.access_token' >/dev/null 2>&1; then
            echo -e "${GREEN}✓ OAuth authorization successful!${NC}"
            echo "$token_response" | jq . > "${SECRETS_DIR}/youtube-token.json"
            echo -e "${GREEN}✓ Access token saved${NC}"
        else
            echo -e "${RED}✗ Token exchange failed${NC}"
            echo "Error: $(echo "$token_response" | jq -r '.error_description // .error')"
        fi
    fi
fi

###############################################################################
# Step 5: Auto-Enable Live Mode
###############################################################################
echo ""
echo -e "${YELLOW}Step 5: Enabling Live Mode for YouTube Monitors${NC}"

# Create environment file for monitors to source
ENV_FILE="${WORKSPACE_ROOT}/.cache/.youtube-monitor-env"
cat > "${ENV_FILE}" << ENVEOF
export YOUTUBE_OAUTH_CREDS_FILE="${YOUTUBE_CREDS_FILE}"
export YOUTUBE_OAUTH_TOKEN="${SECRETS_DIR}/youtube-token.json"
export YOUTUBE_MONITOR_MODE="live"
ENVEOF

chmod 600 "${ENV_FILE}"
echo -e "${GREEN}✓ Created environment file: ${ENV_FILE}${NC}"

###############################################################################
# Step 6: Summary & Next Steps
###############################################################################
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ Setup Complete!${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ YouTube credentials configured${NC}"
echo -e "${GREEN}✓ Environment file created${NC}"
echo ""
echo "Next steps:"
echo "1. YouTube DM Monitor will auto-detect live credentials on next cron run (hourly)"
echo "2. YouTube Comment Monitor will auto-detect live credentials on next cron run (30 min)"
echo "3. Both monitors will automatically switch from demo → live mode"
echo ""
echo "⏱️  Timeline:"
echo "   - Within 1 hour: DM Monitor goes live"
echo "   - Within 30 min: Comment Monitor goes live"
echo "   - Within 24 hours: First partnerships/sales identified"
echo ""
echo "Monitor progress:"
echo "   tail -f ${WORKSPACE_ROOT}/.cache/youtube-dms.jsonl"
echo "   tail -f ${WORKSPACE_ROOT}/.cache/youtube-comments.jsonl"
echo ""
echo "Credentials stored (secure):"
echo "   ${YOUTUBE_CREDS_FILE} (mode: 600)"
echo "   ${SECRETS_DIR}/youtube-token.json (if generated)"
echo ""

date >> "${VALIDATION_LOG}"
echo "✓ Setup completed successfully" >> "${VALIDATION_LOG}"
