#!/usr/bin/env python3
"""
YouTube API Authentication Setup
Run this once to authorize the monitor script to access your YouTube account.
"""

import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

WORKSPACE = Path("/Users/abundance/.openclaw/workspace")
SECRETS_DIR = WORKSPACE / ".secrets"
YOUTUBE_API_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def setup_auth():
    """Run authentication flow and save credentials."""
    creds_path = SECRETS_DIR / "youtube-credentials.json"
    token_path = SECRETS_DIR / "youtube-token.json"
    
    if not creds_path.exists():
        print(f"❌ Credentials file not found: {creds_path}")
        print("   You need to:")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Create a new project or select existing")
        print("   3. Enable YouTube Data API v3")
        print("   4. Create an OAuth 2.0 Desktop App credential")
        print("   5. Download credentials.json and save to:", creds_path)
        return False
    
    print("🔐 Starting YouTube API authentication...")
    print("   A browser window will open. Authorize the app to access your YouTube account.")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(creds_path), YOUTUBE_API_SCOPES
        )
        creds = flow.run_local_server(port=0)
        
        # Save token
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        
        print(f"✓ Authentication successful!")
        print(f"  Token saved to: {token_path}")
        print(f"\n  Your monitor is now ready to run:")
        print(f"  python3 {WORKSPACE}/scripts/youtube-comment-monitor.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = setup_auth()
    sys.exit(0 if success else 1)
