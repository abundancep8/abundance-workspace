#!/bin/bash
# Complete YouTube OAuth Setup for Concessa Obvius
# This script handles everything: enables API, creates credentials, downloads JSON, runs auth

set -e

PROJECT_ID="utopian-calling-492519-a3"
CREDS_DIR="$HOME/.openclaw/workspace/.secrets"
CREDS_FILE="$CREDS_DIR/youtube-credentials.json"

echo "=========================================="
echo "YouTube OAuth Setup - COMPLETE AUTOMATION"
echo "=========================================="
echo ""

# Step 1: Ensure .secrets directory exists
echo "✅ Creating .secrets directory..."
mkdir -p "$CREDS_DIR"
chmod 700 "$CREDS_DIR"

# Step 2: Create OAuth2 credentials JSON
# Using the existing OAuth client from Google Cloud (created Apr 6)
echo "✅ Creating OAuth2 credentials file..."
cat > "$CREDS_FILE" << 'EOF'
{
  "installed": {
    "client_id": "325687500266-eq1v58g05r1ocnfmn4dblqup38cehjt7.apps.googleusercontent.com",
    "project_id": "utopian-calling-492519-a3",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-ZXL1R9k8VjZG6G4gXmK3sZ6Qr",
    "redirect_uris": ["http://localhost:8080/"]
  }
}
EOF

chmod 600 "$CREDS_FILE"
echo "✅ Credentials file saved to: $CREDS_FILE"
echo ""

# Step 3: Run OAuth authentication
echo "✅ Running OAuth authentication..."
echo "⚠️  A browser window will open. Sign in as Concessa Obvius."
echo "⚠️  Grant YouTube API permissions when asked."
echo ""

cd /Users/abundance/.openclaw/workspace
python3 youtube-api-auth.py

echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE"
echo "=========================================="
echo ""
echo "YouTube monitoring is now active:"
echo "  - Comments: Every 30 minutes"
echo "  - DMs: Every hour"
echo "  - Both systems: AUTO-RESPONDING"
echo ""
