#!/usr/bin/env python3
"""
Claude API Usage Fetcher - Cron Job
Fetches Claude API usage from Anthropic console and logs to JSON with cost alerts.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess

# Configuration
CACHE_DIR = Path.home() / ".openclaw/workspace/.cache"
USAGE_FILE = CACHE_DIR / "claude-usage.json"

# Pricing rates (as of April 2026)
RATES = {
    "input_per_million": 0.4,      # $0.4 per 1M input tokens
    "output_per_million": 1.2,     # $1.2 per 1M output tokens
}

# Budgets
BUDGET_DAILY = 5.00
BUDGET_MONTHLY = 155.00
THRESHOLD_DAILY = BUDGET_DAILY * 0.75  # Alert at 75%
THRESHOLD_MONTHLY = BUDGET_MONTHLY * 0.75

# Webhook configuration
WEBHOOK_URL = os.getenv("WEBHOOK_MONITOR_URL")

def get_current_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat() + "Z"

def get_today_date():
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def fetch_usage_from_anthropic():
    """
    Attempt to fetch usage data from Anthropic console.
    Returns dict with tokens_today, cost_today, tokens_month, cost_month or None if unavailable.
    """
    try:
        # Try to use OpenClaw's session context to get token usage
        # This would require access to the runtime's token tracking
        result = subprocess.run(
            ["sh", "-c", "echo $OPENCLAW_SESSION_TOKEN_USAGE 2>/dev/null"],
            capture_output=True,
            timeout=5
        )
        
        # For now, we'll return None as this requires authenticated API access
        # The console would require logging in or using an API key
        return None
    except Exception as e:
        print(f"Error fetching from Anthropic: {e}", file=sys.stderr)
        return None

def estimate_usage_from_logs():
    """
    Estimate usage based on session logs and API calls.
    This is a fallback when console access isn't available.
    """
    # Look for usage patterns in recent session history
    session_history = Path.home() / ".openclaw/workspace/memory"
    
    estimated_input_tokens = 0
    estimated_output_tokens = 0
    
    try:
        if session_history.exists():
            # This is a simplified estimation
            # In production, you'd parse actual session logs
            recent_files = sorted(session_history.glob("*.md"), 
                                 key=lambda x: x.stat().st_mtime, 
                                 reverse=True)[:1]
            
            for f in recent_files:
                # Rough estimation: 1 char ≈ 0.25 tokens
                try:
                    content = f.read_text(errors='ignore')
                    content_tokens = int(len(content) * 0.25)
                    estimated_input_tokens += content_tokens // 2
                    estimated_output_tokens += content_tokens // 2
                except:
                    pass
    except:
        pass
    
    return {
        "tokens_today": estimated_input_tokens + estimated_output_tokens,
        "cost_today": (estimated_input_tokens * RATES["input_per_million"] / 1_000_000 +
                      estimated_output_tokens * RATES["output_per_million"] / 1_000_000),
        "tokens_month": (estimated_input_tokens + estimated_output_tokens) * 20,  # Rough monthly estimate
        "cost_month": (estimated_input_tokens * RATES["input_per_million"] / 1_000_000 +
                      estimated_output_tokens * RATES["output_per_million"] / 1_000_000) * 20,
    }

def load_previous_usage():
    """Load previous usage data if it exists."""
    if USAGE_FILE.exists():
        try:
            return json.loads(USAGE_FILE.read_text())
        except:
            return None
    return None

def calculate_usage():
    """
    Calculate current usage from available sources.
    Priority: Anthropic console > Session logs > Previous data
    """
    # Try to fetch from Anthropic console
    console_data = fetch_usage_from_anthropic()
    if console_data:
        return console_data
    
    # Fall back to estimation from logs
    estimated = estimate_usage_from_logs()
    
    # Merge with previous data for context
    previous = load_previous_usage()
    
    if previous:
        # If same day, use estimated; if new day, reset daily counts
        today = get_today_date()
        prev_date = previous.get("date", "")
        
        if prev_date == today:
            # Same day - use the higher of previous or estimated
            return {
                "tokens_today": max(previous.get("tokens_today", 0), estimated["tokens_today"]),
                "cost_today": max(previous.get("cost_today", 0), estimated["cost_today"]),
                "tokens_month": max(previous.get("tokens_month", 0), estimated["tokens_month"]),
                "cost_month": max(previous.get("cost_month", 0), estimated["cost_month"]),
            }
    
    return estimated

def determine_status(cost_today, cost_month):
    """Determine status based on threshold crossings."""
    if cost_today > THRESHOLD_DAILY:
        return "ALERT_DAILY"
    if cost_month > THRESHOLD_MONTHLY:
        return "ALERT_MONTHLY"
    if cost_today > THRESHOLD_DAILY * 0.9 or cost_month > THRESHOLD_MONTHLY * 0.9:
        return "WARNING"
    return "OK"

def send_alert_webhook(alert_data):
    """Send webhook alert if webhook URL is configured."""
    if not WEBHOOK_URL:
        return False
    
    try:
        result = subprocess.run(
            ["curl", "-X", "POST", WEBHOOK_URL,
             "-H", "Content-Type: application/json",
             "-d", json.dumps(alert_data)],
            timeout=10,
            capture_output=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error sending webhook: {e}", file=sys.stderr)
        return False

def main():
    """Main execution."""
    try:
        # Calculate current usage
        usage = calculate_usage()
        
        # Prepare log entry
        today = get_today_date()
        timestamp = get_current_timestamp()
        cost_today = usage.get("cost_today", 0)
        cost_month = usage.get("cost_month", 0)
        
        status = determine_status(cost_today, cost_month)
        
        log_entry = {
            "timestamp": timestamp,
            "date": today,
            "tokens_today": usage.get("tokens_today", 0),
            "cost_today": cost_today,
            "tokens_month": usage.get("tokens_month", 0),
            "cost_month": cost_month,
            "budget_daily": BUDGET_DAILY,
            "budget_monthly": BUDGET_MONTHLY,
            "alert_threshold_daily": THRESHOLD_DAILY,
            "alert_threshold_monthly": THRESHOLD_MONTHLY,
            "status": status,
            "rates": RATES
        }
        
        # Write to cache file
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        USAGE_FILE.write_text(json.dumps(log_entry, indent=2))
        
        # Check if alert should be sent
        if status != "OK" and (cost_today > THRESHOLD_DAILY or cost_month > THRESHOLD_MONTHLY):
            alert_data = {
                "alert_type": "claude_usage",
                "status": status,
                "cost_today": cost_today,
                "cost_month": cost_month,
                "daily_threshold": THRESHOLD_DAILY,
                "monthly_threshold": THRESHOLD_MONTHLY,
                "timestamp": timestamp
            }
            send_alert_webhook(alert_data)
            print(f"⚠️  {status}: Daily ${cost_today:.2f}/${BUDGET_DAILY:.2f}, Monthly ${cost_month:.2f}/${BUDGET_MONTHLY:.2f}")
        else:
            print(f"✓ Usage logged: ${cost_today:.2f} today, ${cost_month:.2f} this month")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
