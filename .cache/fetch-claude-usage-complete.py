#!/usr/bin/env python3
"""
Fetch Claude API usage from Anthropic console via browser automation.
Logs to claude-usage.json and triggers webhook alerts if thresholds exceeded.
"""

import json
import sys
import os
import subprocess
import re
from datetime import datetime, timezone
from pathlib import Path
import time

# Configuration
CACHE_DIR = Path("/Users/abundance/.openclaw/workspace/.cache")
OUTPUT_FILE = CACHE_DIR / "claude-usage.json"
WEBHOOK_URL = os.getenv("WEBHOOK_MONITOR_URL")
ANTHROPIC_CONSOLE_URL = "https://console.anthropic.com/dashboard"

# Rate constants (Haiku)
HAIKU_INPUT_RATE = 0.4 / 1_000_000  # $0.4 per 1M input tokens
HAIKU_OUTPUT_RATE = 1.2 / 1_000_000  # $1.2 per 1M output tokens

# Budget thresholds (75% triggers alert)
DAILY_BUDGET = 5.00
MONTHLY_BUDGET = 155.00
DAILY_ALERT_THRESHOLD = DAILY_BUDGET * 0.75  # $3.75
MONTHLY_ALERT_THRESHOLD = MONTHLY_BUDGET * 0.75  # $116.25

def calculate_cost(input_tokens, output_tokens):
    """Calculate cost from token counts."""
    if input_tokens is None or output_tokens is None:
        return None
    return (input_tokens * HAIKU_INPUT_RATE) + (output_tokens * HAIKU_OUTPUT_RATE)

def fetch_usage_via_browser():
    """
    Attempt to fetch usage via browser automation.
    Returns: (tokens_today, tokens_month, input_today, output_today, input_month, output_month)
    """
    try:
        # Try using Playwright with OpenClaw's browser tool
        # This requires the browser to already be open with authentication
        result = subprocess.run(
            ["curl", "-s", "-b", os.path.expanduser("~/.cookies"), ANTHROPIC_CONSOLE_URL],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
            
        html = result.stdout
        
        # Parse usage data from page (pattern matching)
        # This is a fallback - ideally you'd use Playwright/Selenium
        patterns = {
            'today': r'Today:\s*[\$]?([\d.]+)',
            'month': r'This month:\s*[\$]?([\d.]+)',
        }
        
        data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                data[key] = float(match.group(1))
        
        if len(data) >= 2:
            return data.get('today'), data.get('month')
        
    except Exception as e:
        print(f"Browser fetch failed: {e}", file=sys.stderr)
    
    return None

def fetch_usage_from_env():
    """
    Fetch usage from environment variables (manual input).
    Expected format:
      ANTHROPIC_USAGE_INPUT_TOKENS_TODAY
      ANTHROPIC_USAGE_OUTPUT_TOKENS_TODAY
      ANTHROPIC_USAGE_INPUT_TOKENS_MONTH
      ANTHROPIC_USAGE_OUTPUT_TOKENS_MONTH
    """
    try:
        input_today = int(os.getenv("ANTHROPIC_USAGE_INPUT_TOKENS_TODAY", 0))
        output_today = int(os.getenv("ANTHROPIC_USAGE_OUTPUT_TOKENS_TODAY", 0))
        input_month = int(os.getenv("ANTHROPIC_USAGE_INPUT_TOKENS_MONTH", 0))
        output_month = int(os.getenv("ANTHROPIC_USAGE_OUTPUT_TOKENS_MONTH", 0))
        
        if input_today or output_today or input_month or output_month:
            return {
                "input_today": input_today,
                "output_today": output_today,
                "input_month": input_month,
                "output_month": output_month,
            }
    except (ValueError, TypeError):
        pass
    
    return None

def log_usage(data):
    """Write usage data to JSON file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))

def trigger_webhook(alert_data):
    """POST alert to webhook if configured."""
    if not WEBHOOK_URL:
        return
    
    try:
        subprocess.run(
            ["curl", "-s", "-X", "POST", WEBHOOK_URL, 
             "-H", "Content-Type: application/json",
             "-d", json.dumps(alert_data)],
            timeout=5
        )
    except Exception as e:
        print(f"Webhook trigger failed: {e}", file=sys.stderr)

def main():
    now = datetime.now(timezone.utc)
    
    # Try to fetch usage
    usage = fetch_usage_from_env()
    
    if not usage:
        # Fallback: try browser
        result = fetch_usage_via_browser()
        if result:
            today_cost, month_cost = result
            usage = {
                "cost_today": today_cost,
                "cost_month": month_cost,
                "input_today": None,
                "output_today": None,
                "input_month": None,
                "output_month": None,
            }
    
    # Build response
    response = {
        "timestamp": now.isoformat(),
        "status": "unknown",
        "budget_daily": DAILY_BUDGET,
        "budget_monthly": MONTHLY_BUDGET,
        "rates": {
            "haiku_input_per_1m": HAIKU_INPUT_RATE * 1_000_000,
            "haiku_output_per_1m": HAIKU_OUTPUT_RATE * 1_000_000,
        },
    }
    
    if usage:
        # Calculate costs if tokens available
        cost_today = None
        cost_month = None
        
        if "input_today" in usage and "output_today" in usage:
            cost_today = calculate_cost(usage["input_today"], usage["output_today"])
        elif "cost_today" in usage:
            cost_today = usage["cost_today"]
        
        if "input_month" in usage and "output_month" in usage:
            cost_month = calculate_cost(usage["input_month"], usage["output_month"])
        elif "cost_month" in usage:
            cost_month = usage["cost_month"]
        
        response.update({
            "status": "success",
            "tokens_today": usage.get("input_today", 0) + usage.get("output_today", 0) if usage.get("input_today") else None,
            "tokens_month": usage.get("input_month", 0) + usage.get("output_month", 0) if usage.get("input_month") else None,
            "cost_today": cost_today,
            "cost_month": cost_month,
            "input_tokens_today": usage.get("input_today"),
            "output_tokens_today": usage.get("output_today"),
            "input_tokens_month": usage.get("input_month"),
            "output_tokens_month": usage.get("output_month"),
        })
        
        # Check thresholds and trigger alert if needed
        alert_triggered = False
        alert_reasons = []
        
        if cost_today and cost_today > DAILY_ALERT_THRESHOLD:
            alert_triggered = True
            alert_reasons.append(f"Daily cost ${cost_today:.2f} exceeds 75% threshold (${DAILY_ALERT_THRESHOLD:.2f})")
        
        if cost_month and cost_month > MONTHLY_ALERT_THRESHOLD:
            alert_triggered = True
            alert_reasons.append(f"Monthly cost ${cost_month:.2f} exceeds 75% threshold (${MONTHLY_ALERT_THRESHOLD:.2f})")
        
        if alert_triggered:
            response["alert"] = True
            response["alert_reasons"] = alert_reasons
            
            alert_data = {
                "timestamp": now.isoformat(),
                "type": "claude_usage_alert",
                "severity": "warning",
                "reasons": alert_reasons,
                "usage": {
                    "cost_today": cost_today,
                    "cost_month": cost_month,
                    "tokens_today": response["tokens_today"],
                    "tokens_month": response["tokens_month"],
                },
                "budgets": {
                    "daily": DAILY_BUDGET,
                    "monthly": MONTHLY_BUDGET,
                }
            }
            
            trigger_webhook(alert_data)
    else:
        response["status"] = "failed"
        response["error"] = "Unable to fetch usage data"
        response["help"] = "Set environment variables: ANTHROPIC_USAGE_INPUT_TOKENS_TODAY, ANTHROPIC_USAGE_OUTPUT_TOKENS_TODAY, etc."
    
    # Log and output
    log_usage(response)
    
    return 0 if response["status"] == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
