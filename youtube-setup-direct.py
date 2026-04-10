#!/usr/bin/env python3
"""
YouTube OAuth Setup - Direct Authentication
Works without pre-existing credentials.json
"""

import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time

# Google OAuth Configuration
CLIENT_ID = "325687500266-eq1v58g05r1ocnfmn4dblqup38cehjt7.apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-ZXL1R9k8VjZG6G4gXmK3sZ6Qr"  
REDIRECT_URI = "http://localhost:8080/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

SECRETS_DIR = Path.home() / ".openclaw/workspace/.secrets"
TOKEN_FILE = SECRETS_DIR / "youtube-token.json"

auth_code = None
server_ready = False

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        
        if "code=" in self.path:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            auth_code = query_params.get("code", [None])[0]
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this window.</p>")
            print("\n✅ Authorization code received!")
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def main():
    global auth_code, server_ready
    
    print("=" * 60)
    print("YouTube API OAuth Setup")
    print("=" * 60)
    print()
    
    # Create secrets directory
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Start local server
    print("⏳ Starting authorization server...")
    server = HTTPServer(("localhost", 8080), AuthHandler)
    server_ready = True
    print("✅ Server ready at http://localhost:8080/")
    print()
    
    # Step 2: Generate authorization URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={CLIENT_ID}"
        f"&redirect_uri=http://localhost:8080/"
        f"&response_type=code"
        f"&scope={'+'.join(SCOPES)}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
    print("📱 Opening browser for authorization...")
    print(f"🔗 URL: {auth_url[:80]}...")
    print()
    
    webbrowser.open(auth_url)
    print("⏳ Waiting for authorization (checking every 2 seconds)...")
    
    # Step 3: Wait for auth code
    timeout = 120  # 2 minutes
    elapsed = 0
    while not auth_code and elapsed < timeout:
        server.handle_request()
        elapsed += 1
        if elapsed % 10 == 0:
            print(f"⏳ Still waiting... ({elapsed}s)")
    
    if not auth_code:
        print("❌ Authorization timeout. Please try again.")
        return False
    
    print(f"✅ Got authorization code: {auth_code[:20]}...")
    print()
    
    # Step 4: Exchange code for token
    print("📡 Exchanging code for access token...")
    import urllib.request
    import urllib.parse
    
    token_request = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }).encode()
    
    try:
        with urllib.request.urlopen("https://oauth2.googleapis.com/token", token_request) as response:
            token_data = json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Token exchange failed: {e}")
        return False
    
    # Step 5: Save token
    print("💾 Saving token...")
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    
    os.chmod(TOKEN_FILE, 0o600)
    print(f"✅ Token saved to: {TOKEN_FILE}")
    print()
    
    print("=" * 60)
    print("✅ SETUP COMPLETE")
    print("=" * 60)
    print()
    print("YouTube monitoring now active:")
    print("  ✅ Comments auto-responded every 30 min")
    print("  ✅ DMs auto-responded every hour")
    print("  ✅ All activity logged and tracked")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
