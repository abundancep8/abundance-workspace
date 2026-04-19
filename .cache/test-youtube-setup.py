#!/usr/bin/env python3
"""
YouTube Comment Monitor - Setup Test
Validates configuration and performs end-to-end testing
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE / ".cache"

class Tester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test(self, name: str, condition: bool, error_msg: str = ""):
        """Record test result."""
        if condition:
            print(f"✓ {name}")
            self.passed += 1
        else:
            print(f"✗ {name}")
            if error_msg:
                print(f"  → {error_msg}")
            self.failed += 1
    
    def warn(self, name: str, msg: str = ""):
        """Record warning."""
        print(f"⚠ {name}")
        if msg:
            print(f"  → {msg}")
        self.warnings += 1
    
    def section(self, title: str):
        """Print section header."""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    
    def summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"  Test Summary")
        print(f"{'=' * 60}\n")
        print(f"  ✓ Passed: {self.passed}")
        print(f"  ✗ Failed: {self.failed}")
        print(f"  ⚠ Warnings: {self.warnings}")
        print(f"  Total: {total}\n")
        
        if self.failed == 0:
            print("✨ All tests passed! Monitor is ready to deploy.\n")
            return True
        else:
            print(f"❌ {self.failed} test(s) failed. Fix issues above.\n")
            return False

def test_environment(t: Tester):
    """Test Python environment."""
    t.section("Environment")
    
    t.test(
        "Python version ≥ 3.8",
        sys.version_info >= (3, 8),
        f"Current: {sys.version}"
    )
    
    t.test(
        "Workspace directory exists",
        WORKSPACE.exists(),
        f"Path: {WORKSPACE}"
    )
    
    t.test(
        "Cache directory exists",
        CACHE_DIR.exists(),
        f"Path: {CACHE_DIR}"
    )

def test_dependencies(t: Tester):
    """Test required Python packages."""
    t.section("Dependencies")
    
    packages = {
        'google': 'google-api-python-client',
        'google_auth_oauthlib': 'google-auth-oauthlib',
        'google.auth': 'google-auth-httplib2',
    }
    
    for module, package_name in packages.items():
        try:
            __import__(module)
            t.test(f"Package: {package_name}", True)
        except ImportError as e:
            t.test(
                f"Package: {package_name}",
                False,
                f"Install with: pip install {package_name}"
            )

def test_scripts(t: Tester):
    """Test script files exist and are readable."""
    t.section("Script Files")
    
    scripts = [
        "youtube-comment-monitor.py",
        "youtube-monitor-cron.sh",
        "setup-youtube-cron.py",
        "youtube-monitor-dashboard.py",
    ]
    
    for script in scripts:
        path = CACHE_DIR / script
        t.test(
            f"File: {script}",
            path.exists(),
            f"Path: {path}"
        )

def test_credentials(t: Tester):
    """Test credentials setup."""
    t.section("Credentials")
    
    creds_file = CACHE_DIR / "youtube_credentials.json"
    
    t.test(
        "Credentials file exists",
        creds_file.exists(),
        "Download from Google Cloud Console > Credentials"
    )
    
    if creds_file.exists():
        try:
            with open(creds_file) as f:
                creds = json.load(f)
            
            t.test(
                "Credentials file is valid JSON",
                'installed' in creds or 'web' in creds,
                "JSON doesn't look like OAuth credentials"
            )
            
            if 'installed' in creds:
                t.test(
                    "Has client_id",
                    'client_id' in creds['installed'],
                    "Missing client_id in credentials"
                )
                t.test(
                    "Has client_secret",
                    'client_secret' in creds['installed'],
                    "Missing client_secret in credentials"
                )
        except json.JSONDecodeError:
            t.test("Credentials file is valid JSON", False, "File is not valid JSON")
        except Exception as e:
            t.test("Credentials file is readable", False, str(e))

def test_configuration(t: Tester):
    """Test script configuration."""
    t.section("Configuration")
    
    monitor_script = CACHE_DIR / "youtube-comment-monitor.py"
    
    if not monitor_script.exists():
        t.warn("Cannot read configuration", "Script file not found")
        return
    
    try:
        with open(monitor_script) as f:
            content = f.read()
        
        # Check for placeholder channel ID
        if 'CHANNEL_ID = "UCa_mZVVqV5Aq48a0MnIjS-w"' in content:
            t.warn(
                "Channel ID is placeholder",
                "Update CHANNEL_ID in youtube-comment-monitor.py with actual channel ID"
            )
        else:
            t.test("Channel ID is configured", True)
        
        # Check for response templates
        t.test(
            "Response templates defined",
            'RESPONSE_TEMPLATES' in content,
            "Cannot find RESPONSE_TEMPLATES in script"
        )
        
        # Check for category patterns
        t.test(
            "Category patterns defined",
            'PATTERNS' in content,
            "Cannot find PATTERNS in script"
        )
    except Exception as e:
        t.test("Configuration readable", False, str(e))

def test_cron(t: Tester):
    """Test cron configuration."""
    t.section("Cron")
    
    try:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True
        )
        
        crontab_content = result.stdout
        has_youtube_job = 'youtube-monitor' in crontab_content
        
        t.test(
            "Cron job installed",
            has_youtube_job,
            "No youtube-monitor job found in crontab. Run: setup-youtube-cron.py"
        )
        
        if has_youtube_job:
            # Extract the job
            for line in crontab_content.split('\n'):
                if 'youtube-monitor' in line and not line.startswith('#'):
                    t.test(
                        "Cron job is valid",
                        '*/30' in line or '*' in line,
                        f"Job: {line}"
                    )
                    break
    except Exception as e:
        t.warn("Cannot read crontab", str(e))

def test_permissions(t: Tester):
    """Test file permissions."""
    t.section("Permissions")
    
    cron_wrapper = CACHE_DIR / "youtube-monitor-cron.sh"
    
    if cron_wrapper.exists():
        try:
            stat_info = os.stat(cron_wrapper)
            is_executable = bool(stat_info.st_mode & 0o111)
            
            t.test(
                "Cron wrapper is executable",
                is_executable,
                f"Run: chmod +x {cron_wrapper}"
            )
        except Exception as e:
            t.test("Cron wrapper readable", False, str(e))

def test_storage(t: Tester):
    """Test storage setup."""
    t.section("Storage")
    
    comments_log = CACHE_DIR / "youtube-comments.jsonl"
    
    if comments_log.exists():
        try:
            size = comments_log.stat().st_size
            t.test(
                f"Comments log exists ({size} bytes)",
                True,
                f"Path: {comments_log}"
            )
            
            # Try to read first line
            with open(comments_log) as f:
                first_line = f.readline()
                if first_line.strip():
                    try:
                        json.loads(first_line)
                        t.test("Comments log is valid JSONL", True)
                    except json.JSONDecodeError:
                        t.test("Comments log is valid JSONL", False, "First line is not valid JSON")
        except Exception as e:
            t.test("Comments log readable", False, str(e))
    else:
        t.test("Comments log (not yet created)", True, "Will be created on first run")

def test_documentation(t: Tester):
    """Test documentation files."""
    t.section("Documentation")
    
    docs = [
        "README-YOUTUBE-MONITOR.md",
        "YOUTUBE-SETUP.md",
        "YOUTUBE-CHEATSHEET.md",
    ]
    
    for doc in docs:
        path = CACHE_DIR / doc
        t.test(
            f"Doc: {doc}",
            path.exists(),
            f"Path: {path}"
        )

def test_json_tool(t: Tester):
    """Test if jq is available for queries."""
    t.section("Optional Tools")
    
    try:
        result = subprocess.run(
            ['which', 'jq'],
            capture_output=True
        )
        has_jq = result.returncode == 0
        
        if has_jq:
            t.test("jq is installed", True)
        else:
            t.warn(
                "jq not found",
                "Optional but useful. Install: brew install jq"
            )
    except Exception as e:
        t.warn("Cannot check for jq", str(e))

def main():
    """Run all tests."""
    print("\n🧪 YouTube Comment Monitor - Setup Test\n")
    
    t = Tester()
    
    test_environment(t)
    test_dependencies(t)
    test_scripts(t)
    test_credentials(t)
    test_configuration(t)
    test_permissions(t)
    test_cron(t)
    test_storage(t)
    test_documentation(t)
    test_json_tool(t)
    
    success = t.summary()
    
    if success:
        print("Next steps:")
        print("  1. Run: python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py")
        print("  2. Authorize in browser")
        print("  3. Monitor logs: tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log")
        print("  4. View stats: python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py")
    else:
        print("Next steps:")
        print("  1. Fix issues above")
        print("  2. Run this test again")
        print("  3. Refer to: ~/.openclaw/workspace/.cache/YOUTUBE-SETUP.md")
    
    print()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}\n")
        sys.exit(1)
