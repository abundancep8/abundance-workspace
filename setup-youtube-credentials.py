#!/usr/bin/env python3
"""
Setup YouTube API OAuth2 Credentials
Run this once to generate credentials.json for youtube-monitor.py
"""

import json
import sys
from pathlib import Path
from google.auth.oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CREDENTIALS_DIR = Path.home() / ".youtube"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "client_secret.json"


def setup_credentials():
    """Generate OAuth2 credentials using InstalledAppFlow"""
    
    # Ensure directory exists
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if client_secret.json exists
    if not CLIENT_SECRETS_FILE.exists():
        print("=" * 70)
        print("YouTube API Credentials Setup")
        print("=" * 70)
        print()
        print("ERROR: client_secret.json not found!")
        print()
        print("Follow these steps:")
        print()
        print("1. Go to https://console.cloud.google.com/apis/dashboard")
        print("2. Create a new project (or select existing)")
        print("3. Search for 'YouTube Data API v3' and enable it")
        print("4. Go to 'Credentials' → 'Create Credentials'")
        print("5. Choose 'OAuth 2.0 Client ID' → 'Desktop Application'")
        print("6. Download the JSON and save as:")
        print(f"   {CLIENT_SECRETS_FILE}")
        print()
        print("Then run this script again.")
        print()
        return False
    
    try:
        # Create flow from client secrets
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES
        )
        
        print("=" * 70)
        print("YouTube API OAuth2 Setup")
        print("=" * 70)
        print()
        print("A browser window will open for authentication...")
        print()
        
        # Run the flow (opens browser)
        creds = flow.run_local_server(port=0)
        
        # Save credentials
        creds_dict = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "id_token": creds.id_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }
        
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(creds_dict, f, indent=2)
        
        print()
        print("✓ Credentials saved to:", CREDENTIALS_FILE)
        print()
        print("You can now run: python youtube-monitor.py")
        print()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        print()
        return False


if __name__ == "__main__":
    success = setup_credentials()
    sys.exit(0 if success else 1)
