#!/usr/bin/env python3
"""
YouTube Monitor - Setup & Connectivity Tester
Verify YouTube API credentials and settings before running monitor
"""

import json
import sys
from pathlib import Path

CACHE_DIR = Path.home() / ".openclaw" / "workspace" / ".cache"
CREDENTIALS_FILE = CACHE_DIR / "youtube-credentials.json"
TOKEN_FILE = CACHE_DIR / "youtube-token.json"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
JSONL_FILE = CACHE_DIR / "youtube-comments.jsonl"

def test_files():
    """Check if all required files exist."""
    print("\n📁 FILE CHECK")
    print("="*60)
    
    checks = {
        "Script (monitor)": CACHE_DIR / "youtube-monitor.py",
        "Script (viewer)": CACHE_DIR / "youtube-log-viewer.py",
        "Credentials JSON": CREDENTIALS_FILE,
        "OAuth Token": TOKEN_FILE,
        "State File": STATE_FILE,
        "Log File": JSONL_FILE
    }
    
    all_good = True
    for name, path in checks.items():
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {name:20} {path}")
        if name in ["Credentials JSON"] and not exists:
            all_good = False
    
    return all_good

def test_dependencies():
    """Check if Python dependencies are installed."""
    print("\n📦 DEPENDENCY CHECK")
    print("="*60)
    
    deps = {
        "google.auth": "google-auth-oauthlib",
        "google.oauth2": "google-auth-oauthlib",
        "google_auth_oauthlib": "google-auth-oauthlib",
        "googleapiclient": "google-api-python-client"
    }
    
    all_good = True
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"✅ {module:30} (install: {package})")
        except ImportError:
            print(f"❌ {module:30} (install: {package})")
            all_good = False
    
    return all_good

def test_credentials():
    """Validate credentials JSON format."""
    print("\n🔑 CREDENTIALS CHECK")
    print("="*60)
    
    if not CREDENTIALS_FILE.exists():
        print("❌ Credentials file not found!")
        print(f"   Location: {CREDENTIALS_FILE}")
        print("   See YOUTUBE-SETUP.md for setup instructions")
        return False
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        
        required = ['installed', 'client_id', 'client_secret']
        
        if 'installed' in creds:
            print("✅ Credentials file format is valid")
            client_id = creds['installed'].get('client_id', '')
            print(f"   Client ID: {client_id[:20]}...")
            return True
        else:
            print("❌ Invalid credentials format (missing 'installed' key)")
            return False
            
    except json.JSONDecodeError:
        print("❌ Credentials file is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def test_token():
    """Check OAuth token status."""
    print("\n🔐 OAUTH TOKEN CHECK")
    print("="*60)
    
    if not TOKEN_FILE.exists():
        print("⚠️  No OAuth token found (will be created on first run)")
        return None
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            token = json.load(f)
        
        if 'access_token' in token:
            print("✅ OAuth token exists and is valid")
            print(f"   Type: {token.get('type', 'unknown')}")
            return True
        else:
            print("⚠️  Token file exists but may be invalid")
            return False
            
    except json.JSONDecodeError:
        print("❌ Token file is corrupted")
        return False

def test_state():
    """Check state file."""
    print("\n📊 STATE FILE CHECK")
    print("="*60)
    
    if not STATE_FILE.exists():
        print("⚠️  No state file (will be created on first run)")
        return None
    
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        last_check = state.get('last_check')
        processed = len(state.get('processed_comments', []))
        
        print(f"✅ State file is valid")
        print(f"   Last check: {last_check or 'Never'}")
        print(f"   Processed comments: {processed}")
        return True
        
    except json.JSONDecodeError:
        print("❌ State file is corrupted")
        return False

def test_log_file():
    """Check log file."""
    print("\n📝 LOG FILE CHECK")
    print("="*60)
    
    if not JSONL_FILE.exists():
        print("⚠️  No log file yet (will be created on first run)")
        return None
    
    try:
        count = 0
        categories = {}
        
        with open(JSONL_FILE, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                count += 1
                cat = entry.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
        
        print(f"✅ Log file is valid")
        print(f"   Total entries: {count}")
        print(f"   Categories:")
        for cat in sorted(categories.keys()):
            print(f"      {cat}: {categories[cat]}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Log file has invalid JSON: {e}")
        return False

def test_configuration():
    """Check script configuration."""
    print("\n⚙️  CONFIGURATION CHECK")
    print("="*60)
    
    monitor_file = CACHE_DIR / "youtube-monitor.py"
    
    if not monitor_file.exists():
        print("❌ Monitor script not found")
        return False
    
    with open(monitor_file, 'r') as f:
        content = f.read()
    
    checks = {
        "CHANNEL_NAME defined": 'CHANNEL_NAME = "Concessa Obvius"' in content or "CHANNEL_NAME =" in content,
        "TEMPLATES defined": "TEMPLATES = {" in content,
        "CATEGORY_PATTERNS defined": "CATEGORY_PATTERNS = {" in content,
        "YouTube API configured": "build('youtube', 'v3'" in content
    }
    
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_good = False
    
    return all_good

def print_summary(results):
    """Print final summary."""
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    unknown = sum(1 for v in results.values() if v is None)
    
    print(f"\n✅ Passed:  {passed}")
    print(f"❌ Failed:  {failed}")
    print(f"⚠️  Pending: {unknown}")
    
    if failed > 0:
        print("\n🔴 SETUP NOT COMPLETE")
        print("Follow these steps:")
        print("1. Read YOUTUBE-SETUP.md")
        print("2. Create Google Cloud project")
        print("3. Enable YouTube Data API v3")
        print("4. Download OAuth credentials")
        print("5. Save to: " + str(CREDENTIALS_FILE))
        print("6. Run this test again")
    elif unknown > 0:
        print("\n🟡 READY FOR FIRST RUN")
        print("Run: python3 youtube-monitor.py")
        print("(This will create token and log files)")
    else:
        print("\n🟢 ALL SYSTEMS GO!")
        print("Monitor is ready to run")

def main():
    print("\n" + "="*60)
    print("🎬 YOUTUBE COMMENT MONITOR - SETUP TEST")
    print("="*60)
    
    results = {
        "Files": test_files(),
        "Dependencies": test_dependencies(),
        "Credentials": test_credentials(),
        "Token": test_token(),
        "State": test_state(),
        "Log": test_log_file(),
        "Configuration": test_configuration()
    }
    
    print_summary(results)
    
    # Exit code
    failed = sum(1 for v in results.values() if v is False)
    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    main()
