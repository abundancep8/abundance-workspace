#!/usr/bin/env python3
"""
YouTube Data API v3 OAuth Authentication
One-time setup to authorize Abundance to manage Concessa Obvius channel
"""

import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Required scopes for YouTube comment/DM management
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',  # Modify YouTube content
    'https://www.googleapis.com/auth/youtube.readonly',    # Read-only access
]

CREDENTIALS_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-credentials.json'
TOKEN_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-token.json'

def setup_youtube_credentials():
    """Set up YouTube API credentials via OAuth 2.0"""
    
    print("="*70)
    print("YOUTUBE DATA API v3 AUTHORIZATION")
    print("="*70)
    print()
    print("Channel: Concessa Obvius")
    print("Scope: Read/write comments and messages")
    print()
    
    # Check if credentials.json exists
    if not CREDENTIALS_FILE.exists():
        print(f"❌ ERROR: Credentials file not found at:")
        print(f"   {CREDENTIALS_FILE}")
        print()
        print("Steps to fix:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create project: 'abundance-youtube-automation'")
        print("3. Enable YouTube Data API v3")
        print("4. Create OAuth 2.0 Client ID (Desktop)")
        print("5. Download JSON file")
        print(f"6. Save to: {CREDENTIALS_FILE}")
        print()
        return False
    
    try:
        # Load credentials and run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            scopes=SCOPES
        )
        
        print("✅ Opening browser for authorization...")
        print("   (You may need to grant permissions as Concessa Obvius account owner)")
        print()
        
        # Run the local server for OAuth callback
        creds = flow.run_local_server(
            port=8080,
            open_browser=True,
            scopes=SCOPES
        )
        
        # Save token for future use
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        
        print()
        print("="*70)
        print("✅ SUCCESS: YouTube authorization complete!")
        print("="*70)
        print()
        print(f"Token saved to: {TOKEN_FILE}")
        print()
        print("YouTube comment monitor is now active:")
        print("  - Runs every 30 minutes automatically")
        print("  - Fetches comments from Concessa Obvius")
        print("  - Auto-responds to 7 comment categories")
        print("  - Flags complex comments for review")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during authorization: {e}")
        print()
        print("Troubleshooting:")
        print("1. Ensure you have the correct Google account")
        print("2. Check that YouTube Data API v3 is enabled in Cloud Console")
        print("3. Verify OAuth credentials are in the correct location")
        return False

if __name__ == "__main__":
    success = setup_youtube_credentials()
    exit(0 if success else 1)
