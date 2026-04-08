#!/bin/bash

# Load X credentials
source .secrets/.x-tokens.env

# X API v2 Endpoint
ENDPOINT="https://api.twitter.com/2/tweets"

# Post content
POST_TEXT="I hired an AI and we're building a business together. Day 1: \$0 Day 7: We had our first customer. Day 30: \$4,200 in revenue. This is how we did it. 🔗 https://project-vdiaj.vercel.app/api/product?product=a"

# Create the POST body
REQUEST_BODY="{\"text\":\"$POST_TEXT\"}"

echo "Posting to X..."
echo "Text: $POST_TEXT"
echo ""

# Use curl with OAuth 1.0a via oauth header
# We need to use a tool that can handle OAuth 1.0a signing
# Since bash doesn't have built-in OAuth 1.0a, we'll use Python

python3 << 'PYTHON_SCRIPT'
import requests
from requests_oauthlib import OAuth1Session
import json
import os

# Load credentials from environment
consumer_key = os.environ['X_CONSUMER_KEY']
consumer_secret = os.environ['X_CONSUMER_SECRET']
access_token = os.environ['X_ACCESS_TOKEN']
access_token_secret = os.environ['X_ACCESS_TOKEN_SECRET']

# Create OAuth1 session
oauth = OAuth1Session(
    client_key=consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret
)

# Post content
text = "I hired an AI and we're building a business together. Day 1: $0 Day 7: We had our first customer. Day 30: $4,200 in revenue. This is how we did it. 🔗 https://project-vdiaj.vercel.app/api/product?product=a"

payload = {
    "text": text
}

# Make the request
url = "https://api.twitter.com/2/tweets"
try:
    response = oauth.post(url, json=payload)
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        tweet_data = response.json()
        if 'data' in tweet_data:
            print("\n✅ POST SUCCESSFUL!")
            print(f"Tweet ID: {tweet_data['data']['id']}")
            print(f"Text: {tweet_data['data']['text']}")
    else:
        print("\n❌ POSTING FAILED")
except Exception as e:
    print(f"Error: {e}")
PYTHON_SCRIPT
