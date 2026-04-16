#!/usr/bin/env python3
"""
Enhanced Claude API Usage Tracker
Monitors actual token usage from OpenClaw sessions and external APIs
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import re

CACHE_DIR = Path.home() / ".openclaw/workspace/.cache"
USAGE_FILE = CACHE_DIR / "claude-usage.json"

# Pricing rates (April 2026)
RATES = {
    "input_per_million": 0.4,
    "output_per_million": 1.2,
}

BUDGET_DAILY = 5.00
BUDGET_MONTHLY = 155.00
THRESHOLD_DAILY = BUDGET_DAILY * 0.75
THRESHOLD_MONTHLY = BUDGET_MONTHLY * 0.75

def get_timestamp():
    return datetime.now(timezone.utc).isoformat() + "Z"

def get_today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def query_openclaw_usage():
    """Query OpenClaw for actual token usage from current and recent sessions."""
    try:
        # Try to get session list with message limits to estimate usage
        result = subprocess.run(
            ["openclaw", "sessions", "list", "--limit", "10"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Parse output to estimate tokens
            # This is a placeholder - actual implementation would parse session data
            return None
    except:
        pass
    
    return None

def get_api_call_logs():
    """Parse recent API call logs to estimate usage."""
    log_file = CACHE_DIR / "api-call-log.jsonl"
    
    if not log_file.exists():
        return {"input": 0, "output": 0}
    
    tokens = {"input": 0, "output": 0}
    today = get_today()
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("date", "").startswith(today):
                        tokens["input"] += entry.get("input_tokens", 0)
                        tokens["output"] += entry.get("output_tokens", 0)
                except:
                    pass
    except:
        pass
    
    return tokens

def load_previous():
    """Load previous usage data."""
    if USAGE_FILE.exists():
        try:
            return json.loads(USAGE_FILE.read_text())
        except:
            pass
    return None

def calculate_cost(input_tokens, output_tokens):
    """Calculate cost for tokens."""
    input_cost = (input_tokens * RATES["input_per_million"]) / 1_000_000
    output_cost = (output_tokens * RATES["output_per_million"]) / 1_000_000
    return input_cost + output_cost

def get_status(cost_daily, cost_monthly):
    """Determine alert status."""
    if cost_daily > THRESHOLD_DAILY:
        return "ALERT_DAILY"
    if cost_monthly > THRESHOLD_MONTHLY:
        return "ALERT_MONTHLY"
    if cost_daily > THRESHOLD_DAILY * 0.9 or cost_monthly > THRESHOLD_MONTHLY * 0.9:
        return "WARNING"
    return "OK"

def send_webhook_alert(data):
    """Send webhook alert if configured."""
    webhook_url = os.getenv("WEBHOOK_MONITOR_URL")
    if not webhook_url:
        return False
    
    try:
        subprocess.run(
            ["curl", "-X", "POST", webhook_url,
             "-H", "Content-Type: application/json",
             "-d", json.dumps(data)],
            timeout=10,
            capture_output=True
        )
        return True
    except:
        return False

def main():
    """Main function."""
    try:
        today = get_today()
        timestamp = get_timestamp()
        
        # Get API call logs
        api_tokens = get_api_call_logs()
        
        # Load previous data
        previous = load_previous()
        
        # Determine if same day
        same_day = previous and previous.get("date") == today
        
        # Calculate tokens for today
        if same_day:
            # Increment from previous
            tokens_today_input = max(
                api_tokens["input"],
                previous.get("tokens_today_input", 0)
            )
            tokens_today_output = max(
                api_tokens["output"],
                previous.get("tokens_today_output", 0)
            )
        else:
            # New day - reset
            tokens_today_input = api_tokens["input"]
            tokens_today_output = api_tokens["output"]
        
        tokens_today = tokens_today_input + tokens_today_output
        cost_today = calculate_cost(tokens_today_input, tokens_today_output)
        
        # For monthly, increment from previous
        if same_day and previous:
            tokens_month = previous.get("tokens_month", tokens_today)
            cost_month = previous.get("cost_month", cost_today)
        else:
            # New month starting
            tokens_month = tokens_today
            cost_month = cost_today
        
        # Ensure monthly doesn't decrease
        if previous:
            prev_month = previous.get("cost_month", 0)
            if cost_month < prev_month:
                tokens_month = previous.get("tokens_month", tokens_today)
                cost_month = prev_month
        
        status = get_status(cost_today, cost_month)
        
        # Create entry
        entry = {
            "timestamp": timestamp,
            "date": today,
            "tokens_today": tokens_today,
            "tokens_today_input": tokens_today_input,
            "tokens_today_output": tokens_today_output,
            "cost_today": round(cost_today, 6),
            "tokens_month": tokens_month,
            "cost_month": round(cost_month, 6),
            "budget_daily": BUDGET_DAILY,
            "budget_monthly": BUDGET_MONTHLY,
            "alert_threshold_daily": THRESHOLD_DAILY,
            "alert_threshold_monthly": THRESHOLD_MONTHLY,
            "percent_daily": round((cost_today / BUDGET_DAILY * 100), 1),
            "percent_monthly": round((cost_month / BUDGET_MONTHLY * 100), 1),
            "status": status,
            "rates": RATES
        }
        
        # Write to file
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        USAGE_FILE.write_text(json.dumps(entry, indent=2))
        
        # Handle alerts
        should_alert = status in ["ALERT_DAILY", "ALERT_MONTHLY"]
        
        if should_alert:
            alert = {
                "alert_type": "claude_usage",
                "status": status,
                "cost_today": entry["cost_today"],
                "cost_month": entry["cost_month"],
                "percent_daily": entry["percent_daily"],
                "percent_monthly": entry["percent_monthly"],
                "timestamp": timestamp
            }
            send_webhook_alert(alert)
            print(f"🚨 {status}: {entry['percent_daily']:.0f}% daily, {entry['percent_monthly']:.0f}% monthly")
        else:
            status_icon = "✓" if status == "OK" else "⚠️"
            print(f"{status_icon} {status}: ${cost_today:.4f} today ({entry['percent_daily']:.1f}%), "
                  f"${cost_month:.4f} month ({entry['percent_monthly']:.1f}%)")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
