#!/usr/bin/env python3
"""
Validate YouTube Monitor setup
Run this to check that all dependencies and credentials are in place
"""

import sys
import json
from pathlib import Path

print("=" * 70)
print("YouTube Monitor Setup Validation")
print("=" * 70)
print()

all_good = True

# 1. Check Python version
print("✓ Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor} OK")
else:
    print(f"  ✗ Python 3.8+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
    all_good = False

print()

# 2. Check dependencies
print("✓ Checking dependencies...")
required_packages = [
    "google.auth",
    "google.oauth2",
    "google.api_core",
    "googleapiclient",
]

for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} NOT INSTALLED")
        all_good = False

if not all_good:
    print()
    print("  Install dependencies:")
    print("  pip install -r youtube-monitor-requirements.txt")

print()

# 3. Check .youtube directory
print("✓ Checking ~/.youtube directory...")
youtube_dir = Path.home() / ".youtube"
if youtube_dir.exists():
    print(f"  ✓ Directory exists: {youtube_dir}")
else:
    print(f"  ✗ Directory not found: {youtube_dir}")
    print(f"     Create with: mkdir -p {youtube_dir}")
    all_good = False

print()

# 4. Check client_secret.json
print("✓ Checking client_secret.json...")
client_secret = youtube_dir / "client_secret.json"
if client_secret.exists():
    try:
        with open(client_secret) as f:
            data = json.load(f)
        if "installed" in data or "web" in data:
            print(f"  ✓ Found and valid: {client_secret}")
        else:
            print(f"  ✗ Invalid format: {client_secret}")
            all_good = False
    except Exception as e:
        print(f"  ✗ Error reading {client_secret}: {e}")
        all_good = False
else:
    print(f"  ⚠ Not found: {client_secret}")
    print(f"     Get it from Google Cloud Console:")
    print(f"     1. https://console.cloud.google.com/apis/dashboard")
    print(f"     2. Create/select project")
    print(f"     3. Enable 'YouTube Data API v3'")
    print(f"     4. Create OAuth 2.0 credentials (Desktop)")
    print(f"     5. Download and save to: {client_secret}")

print()

# 5. Check credentials.json
print("✓ Checking credentials.json...")
credentials = youtube_dir / "credentials.json"
if credentials.exists():
    try:
        with open(credentials) as f:
            data = json.load(f)
        if "token" in data and "refresh_token" in data:
            print(f"  ✓ Found and valid: {credentials}")
        else:
            print(f"  ⚠ Present but may be incomplete: {credentials}")
    except Exception as e:
        print(f"  ✗ Error reading {credentials}: {e}")
        all_good = False
else:
    print(f"  ⚠ Not found: {credentials}")
    print(f"     Generate with: python setup-youtube-credentials.py")

print()

# 6. Check .cache directory
print("✓ Checking workspace/.cache directory...")
cache_dir = Path.home() / ".openclaw" / "workspace" / ".cache"
if cache_dir.exists():
    print(f"  ✓ Directory exists: {cache_dir}")
else:
    print(f"  ⚠ Will be created on first run: {cache_dir}")

print()

# 7. Check main script
print("✓ Checking scripts...")
workspace = Path.home() / ".openclaw" / "workspace"
scripts = [
    "youtube-monitor.py",
    "setup-youtube-credentials.py",
    "youtube-monitor-query.py",
]

for script in scripts:
    script_path = workspace / script
    if script_path.exists():
        if script_path.stat().st_mode & 0o111:
            print(f"  ✓ {script} (executable)")
        else:
            print(f"  ✓ {script} (not executable)")
    else:
        print(f"  ✗ {script} NOT FOUND")
        all_good = False

print()
print("=" * 70)

if all_good and credentials.exists():
    print("✓ ALL CHECKS PASSED!")
    print()
    print("Ready to run:")
    print("  python youtube-monitor.py")
    print()
elif not all_good:
    print("✗ SETUP INCOMPLETE")
    print()
    print("Next steps:")
    if not client_secret.exists():
        print("  1. Get client_secret.json from Google Cloud Console")
        print("  2. Save to: " + str(client_secret))
    if not credentials.exists():
        print("  3. Run: python setup-youtube-credentials.py")
    if not all(Path.home() / ".openclaw" / "workspace" / s for s in scripts):
        print("  4. Ensure all scripts are in: " + str(workspace))
    print()
    print("See YOUTUBE-MONITOR-SETUP.md for detailed instructions")
    print()
else:
    print("⚠ PARTIALLY READY")
    print()
    print("Next step:")
    print("  python setup-youtube-credentials.py")
    print()

print("=" * 70)
