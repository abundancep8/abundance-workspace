#!/usr/bin/env python3
"""
YouTube Token Refresh - Autonomous token refresh for cron jobs
Refreshes expired OAuth token using stored refresh_token
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

TOKEN_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-token.json'
CREDENTIALS_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-credentials.json'

def refresh_youtube_token():
    """Refresh expired YouTube OAuth token using refresh_token"""
    
    print("[YouTube Token Refresh]", datetime.now().isoformat())
    
    if not TOKEN_FILE.exists():
        print("ERROR: Token file not found")
        return False
    
    if not CREDENTIALS_FILE.exists():
        print("ERROR: Credentials file not found")
        return False
    
    # Load credentials
    with open(CREDENTIALS_FILE, 'r') as f:
        creds = json.load(f)['installed']
    
    # Load token
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
    
    if not token_data.get('refresh_token'):
        print("ERROR: No refresh_token in saved credentials")
        print("ACTION: Run interactive auth: python3 youtube-api-auth.py")
        return False
    
    # Refresh the token
    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': creds['client_id'],
                'client_secret': creds['client_secret'],
                'refresh_token': token_data['refresh_token'],
                'grant_type': 'refresh_token',
            }
        )
        
        if response.status_code != 200:
            print(f"ERROR: Token refresh failed")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Update token data
        new_token = response.json()
        token_data['token'] = new_token['access_token']
        token_data['token_expiry'] = (
            datetime.utcnow() + timedelta(seconds=new_token['expires_in'])
        ).isoformat() + 'Z'
        
        # Save updated token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"✅ Token refreshed successfully")
        print(f"   New expiry: {token_data['token_expiry']}")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == '__main__':
    success = refresh_youtube_token()
    exit(0 if success else 1)
