#!/usr/bin/env python3
"""
YouTube Comment Monitor - Setup Helper
Assists with installation and cron configuration
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE / ".cache"
SCRIPT_PATH = CACHE_DIR / "youtube-comment-monitor.py"
CRON_WRAPPER = CACHE_DIR / "youtube-monitor-cron.sh"
CREDENTIALS_FILE = CACHE_DIR / "youtube_credentials.json"

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(num, text):
    """Print step indicator."""
    print(f"[{num}] {text}")

def check_dependencies():
    """Check if required packages are installed."""
    print_step(1, "Checking dependencies...")
    
    required = [
        'google',
        'google_auth_oauthlib',
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages. Install with:")
        print(f"  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client\n")
        return False
    
    print("  ✓ All dependencies installed\n")
    return True

def check_credentials():
    """Check if credentials exist."""
    print_step(2, "Checking credentials...")
    
    if CREDENTIALS_FILE.exists():
        print(f"  ✓ Found: {CREDENTIALS_FILE}")
        return True
    else:
        print(f"  ✗ Not found: {CREDENTIALS_FILE}")
        print(f"\n  You need to:")
        print(f"    1. Go to https://console.cloud.google.com")
        print(f"    2. Create a project: 'Concessa Obvius Monitor'")
        print(f"    3. Enable 'YouTube Data API v3'")
        print(f"    4. Create OAuth 2.0 credentials (Desktop app)")
        print(f"    5. Download JSON and save to: {CREDENTIALS_FILE}\n")
        return False

def check_channel_id():
    """Check if channel ID is configured."""
    print_step(3, "Checking channel configuration...")
    
    try:
        with open(SCRIPT_PATH) as f:
            content = f.read()
            if 'CHANNEL_ID = "UCa_mZVVqV5Aq48a0MnIjS-w"' in content:
                print("  ⚠️  Channel ID is placeholder - update with real ID\n")
                print("  To find channel ID:")
                print("    • Visit channel URL: youtube.com/@concessaobvius")
                print("    • Check channel about page for full URL")
                print("    • Extract channel ID and update CHANNEL_ID in script\n")
                return False
            else:
                print("  ✓ Channel ID is configured\n")
                return True
    except Exception as e:
        print(f"  ✗ Error reading config: {e}\n")
        return False

def make_executable():
    """Make cron wrapper executable."""
    print_step(4, "Making cron wrapper executable...")
    
    try:
        os.chmod(CRON_WRAPPER, 0o755)
        print(f"  ✓ {CRON_WRAPPER}\n")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False

def setup_crontab():
    """Set up cron job."""
    print_step(5, "Setting up cron job...")
    
    cron_entry = f"*/30 * * * * /bin/bash {CRON_WRAPPER}"
    
    # Check current crontab
    try:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True
        )
        current_crontab = result.stdout if result.returncode == 0 else ""
    except Exception as e:
        print(f"  ✗ Error reading crontab: {e}")
        print(f"\n  Manual setup: run `crontab -e` and add:")
        print(f"    {cron_entry}\n")
        return False
    
    # Check if already installed
    if CRON_WRAPPER.name in current_crontab:
        print("  ✓ Cron job already installed\n")
        return True
    
    # Install cron job
    print(f"  Installing cron job: {cron_entry}")
    
    try:
        new_crontab = current_crontab.rstrip() + "\n" + cron_entry + "\n"
        process = subprocess.Popen(
            ['crontab', '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            print("  ✓ Cron job installed\n")
            return True
        else:
            print(f"  ✗ Error installing cron: {stderr}")
            print(f"\n  Manual setup: run `crontab -e` and add:")
            print(f"    {cron_entry}\n")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        print(f"\n  Manual setup: run `crontab -e` and add:")
        print(f"    {cron_entry}\n")
        return False

def create_log_directory():
    """Ensure log directory exists."""
    print_step(6, "Setting up log directory...")
    
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {CACHE_DIR}\n")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False

def test_first_run():
    """Run script in test mode."""
    print_step(7, "Testing monitor script...")
    
    print("  Running first test (will open browser for authorization)...\n")
    
    try:
        result = subprocess.run(
            ['python3', str(SCRIPT_PATH)],
            cwd=str(WORKSPACE),
            timeout=60
        )
        
        if result.returncode == 0:
            print("\n  ✓ Test successful\n")
            return True
        else:
            print(f"\n  ✗ Script exited with error\n")
            return False
    except subprocess.TimeoutExpired:
        print("\n  ⚠️  Script timed out (auth may be pending)\n")
        return True
    except Exception as e:
        print(f"\n  ✗ Error: {e}\n")
        return False

def print_summary(checks):
    """Print summary of setup."""
    print_header("Setup Summary")
    
    checks_list = [
        ("Dependencies", checks.get('deps')),
        ("Credentials", checks.get('creds')),
        ("Channel ID", checks.get('channel')),
        ("Executable", checks.get('exec')),
        ("Log Directory", checks.get('logs')),
        ("Cron Job", checks.get('cron')),
    ]
    
    all_good = True
    for name, status in checks_list:
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {name}")
        if not status:
            all_good = False
    
    print()
    
    if all_good:
        print("✨ Setup complete! Your monitor is ready.")
        print("\n  Monitor will run every 30 minutes.")
        print(f"  View logs: tail -f {CACHE_DIR}/youtube-monitor.log")
        print(f"  View comments: cat {CACHE_DIR}/youtube-comments.jsonl")
        print("\n  📚 Full guide: " + str(CACHE_DIR / "YOUTUBE-SETUP.md"))
    else:
        print("⚠️  Setup incomplete. Fix the issues above, then run this script again.")
    
    print()

def main():
    """Run setup."""
    print_header("YouTube Comment Monitor - Setup")
    
    checks = {
        'deps': check_dependencies(),
        'creds': check_credentials(),
        'logs': create_log_directory(),
        'channel': check_channel_id(),
        'exec': make_executable(),
    }
    
    # Only setup cron if dependencies and credentials are OK
    if checks['deps'] and checks['creds']:
        checks['cron'] = setup_crontab()
    else:
        checks['cron'] = False
    
    print_summary(checks)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}\n")
        sys.exit(1)
