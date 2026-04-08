#!/usr/bin/env python3

import requests_oauthlib
import json
import os
from pathlib import Path

# Read credentials from file
creds_file = Path('/Users/abundance/.openclaw/workspace/.secrets/.x-tokens.env')
creds = {}

with open(creds_file) as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            creds[key] = value.strip('"')

consumer_key = creds.get('X_CONSUMER_KEY')
consumer_secret = creds.get('X_CONSUMER_SECRET')
access_token = creds.get('X_ACCESS_TOKEN')
access_token_secret = creds.get('X_ACCESS_TOKEN_SECRET')

print(f"Consumer Key: {consumer_key[:15]}...")
print(f"Access Token: {access_token[:20]}...")
print("")

# Create OAuth1 session
try:
    oauth = requests_oauthlib.OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )
except Exception as e:
    print(f"OAuth setup error: {e}")
    exit(1)

# Post content
text = "I hired an AI and we're building a business together. Day 1: $0 Day 7: We had our first customer. Day 30: $4,200 in revenue. This is how we did it. 🔗 https://project-vdiaj.vercel.app/api/product?product=a"

payload = {
    "text": text
}

# Make the request
url = "https://api.twitter.com/2/tweets"
print(f"Posting to {url}...")
print(f"Text: {text[:80]}...")
print("")

try:
    response = oauth.post(url, json=payload)
    print(f"Status: {response.status_code}")
    
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if response.status_code == 201:
        if 'data' in result:
            print("\n✅ POST SUCCESSFUL!")
            print(f"Tweet ID: {result['data']['id']}")
    else:
        print("\n❌ POST FAILED")
        if 'errors' in result:
            print(f"Errors: {result['errors']}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
