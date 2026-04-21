#!/usr/bin/env python3
"""
YouTube Comment Monitor - Setup Verification Script

Verifies that your environment is correctly configured before running the monitor.

Usage:
    python verify_setup.py

This script checks:
- Python version
- Required environment variables
- YouTube API key validity
- Channel accessibility
- File permissions
- Cache directory setup
"""

import sys
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

# ============================================================================
# COLORS FOR OUTPUT
# ============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def header(msg):
    print(f"\n{Colors.BOLD}{msg}{Colors.RESET}")

# ============================================================================
# CHECKS
# ============================================================================

def check_python():
    """Verify Python version."""
    header("Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        error(f"Python {version.major}.{version.minor} (need 3.7+)")
        return False

def check_api_key():
    """Verify API key is set."""
    header("YouTube API Key")
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    
    if not api_key:
        error("YOUTUBE_API_KEY environment variable not set")
        info("Set it with: export YOUTUBE_API_KEY='your_key_here'")
        return False
    
    if len(api_key) < 20:
        error("API key seems too short (likely invalid)")
        return False
    
    success("API key found and looks valid")
    return True

def check_channel_id():
    """Verify channel ID is set."""
    header("YouTube Channel ID")
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID", "UCXXz-s8LjQGpAK-PEzMXbqg")
    
    if not channel_id:
        error("YOUTUBE_CHANNEL_ID not set (using default)")
        return False
    
    success(f"Channel ID: {channel_id}")
    return True

def check_api_connectivity():
    """Test API connectivity."""
    header("YouTube API Connectivity")
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID", "UCXXz-s8LjQGpAK-PEzMXbqg")
    
    if not api_key:
        warning("Skipping (API key not set)")
        return False
    
    try:
        url = (
            f"https://www.googleapis.com/youtube/v3/channels"
            f"?part=snippet"
            f"&id={channel_id}"
            f"&key={api_key}"
        )
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if "items" not in data or len(data["items"]) == 0:
                error(f"Channel not found: {channel_id}")
                return False
            
            channel_name = data["items"][0]["snippet"]["title"]
            subscriber_count = data["items"][0]["statistics"].get("subscriberCount", "Hidden")
            video_count = data["items"][0]["statistics"]["videoCount"]
            
            success(f"Connected to YouTube API")
            info(f"  Channel: {channel_name}")
            info(f"  Videos: {video_count}")
            info(f"  Subscribers: {subscriber_count}")
            return True
            
    except urllib.error.HTTPError as e:
        if e.code == 403:
            error("API key invalid or API not enabled")
            info("See SETUP.md for instructions")
        elif e.code == 404:
            error(f"Channel not found: {channel_id}")
        else:
            error(f"HTTP {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        error(f"Network error: {e.reason}")
        warning("Check your internet connection")
        return False
    except Exception as e:
        error(f"Unexpected error: {e}")
        return False

def check_file_structure():
    """Verify script files exist."""
    header("File Structure")
    script_dir = Path(__file__).parent
    
    checks = {
        "youtube_comment_monitor.py": script_dir / "youtube_comment_monitor.py",
        "README.md": script_dir / "README.md",
        "SETUP.md": script_dir / "SETUP.md",
    }
    
    all_ok = True
    for name, path in checks.items():
        if path.exists():
            success(f"{name}")
        else:
            error(f"{name} (not found at {path})")
            all_ok = False
    
    return all_ok

def check_cache_dir():
    """Verify cache directory is writable."""
    header("Cache Directory")
    cache_dir = Path(".cache")
    
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to write test file
        test_file = cache_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        
        success(f"Cache directory is writable: {cache_dir.absolute()}")
        return True
    except Exception as e:
        error(f"Cannot write to cache directory: {e}")
        return False

def check_script_syntax():
    """Verify main script has valid Python syntax."""
    header("Script Syntax")
    script_path = Path(__file__).parent / "youtube_comment_monitor.py"
    
    if not script_path.exists():
        warning("Script not found, skipping syntax check")
        return False
    
    try:
        with open(script_path, 'r') as f:
            compile(f.read(), str(script_path), 'exec')
        success("Script syntax is valid")
        return True
    except SyntaxError as e:
        error(f"Syntax error: {e}")
        return False
    except Exception as e:
        error(f"Error checking syntax: {e}")
        return False

def check_cron_executable():
    """Verify run_monitor.sh is executable."""
    header("Cron Wrapper")
    wrapper_path = Path(__file__).parent / "run_monitor.sh"
    
    if not wrapper_path.exists():
        warning("run_monitor.sh not found (optional)")
        return True
    
    if os.access(wrapper_path, os.X_OK):
        success("run_monitor.sh is executable")
        return True
    else:
        warning("run_monitor.sh is not executable")
        info(f"Make it executable with: chmod +x {wrapper_path}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all checks."""
    print(f"{Colors.BOLD}YouTube Comment Monitor - Setup Verification{Colors.RESET}")
    print("=" * 60)
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python()))
    results.append(("API Key", check_api_key()))
    results.append(("Channel ID", check_channel_id()))
    results.append(("API Connectivity", check_api_connectivity()))
    results.append(("File Structure", check_file_structure()))
    results.append(("Cache Directory", check_cache_dir()))
    results.append(("Script Syntax", check_script_syntax()))
    results.append(("Cron Wrapper", check_cron_executable()))
    
    # Summary
    print("\n" + "=" * 60)
    header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} — {name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        success("All checks passed! You're ready to run the monitor.")
        print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
        print("  1. Run once to test: python youtube_comment_monitor.py")
        print("  2. Check logs: tail -f .cache/youtube-monitor.log")
        print("  3. Set up cron: */30 * * * * YOUTUBE_API_KEY='...' python youtube_comment_monitor.py")
        print("\nSee README.md for more options and configuration.")
        return 0
    else:
        error(f"{total - passed} checks failed. See above for details.")
        print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
        print("  1. Fix the failed checks above")
        print("  2. Run this script again: python verify_setup.py")
        print("  3. See SETUP.md for detailed instructions")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        error(f"Fatal error: {e}")
        sys.exit(1)
