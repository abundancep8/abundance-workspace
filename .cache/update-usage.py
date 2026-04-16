#!/usr/bin/env python3
"""
Manual Claude API usage updater
Use this to manually input usage data from the Anthropic console
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def update_usage(tokens_today: int, tokens_month: int, webhook_url: str = None) -> dict:
    """Update usage log with provided token counts and calculate costs"""
    
    # Rates (April 2026)
    INPUT_RATE = 0.4   # $0.4 per 1M input tokens
    OUTPUT_RATE = 1.2  # $1.2 per 1M output tokens
    
    # Budgets
    DAILY_BUDGET = 5.00
    MONTHLY_BUDGET = 155.00
    ALERT_DAILY_THRESHOLD = 3.75
    ALERT_MONTHLY_THRESHOLD = 116.25
    
    # Calculate costs
    def calculate_cost(tokens):
        """Calculate cost for tokens (input tokens only, for simplicity)"""
        millions = tokens / 1_000_000
        return round(millions * INPUT_RATE, 4)
    
    cost_today = calculate_cost(tokens_today)
    cost_month = calculate_cost(tokens_month)
    
    # Determine status
    status = "OK"
    if cost_today > ALERT_DAILY_THRESHOLD:
        status = "ALERT_DAILY"
    elif cost_month > ALERT_MONTHLY_THRESHOLD:
        status = "ALERT_MONTHLY"
    
    # Create usage data
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    usage_data = {
        "timestamp": now.isoformat() + "Z",
        "date": now.strftime("%Y-%m-%d"),
        "tokens_today": tokens_today,
        "cost_today": cost_today,
        "tokens_month": tokens_month,
        "cost_month": cost_month,
        "budget_daily": DAILY_BUDGET,
        "budget_monthly": MONTHLY_BUDGET,
        "alert_threshold_daily": ALERT_DAILY_THRESHOLD,
        "alert_threshold_monthly": ALERT_MONTHLY_THRESHOLD,
        "status": status,
        "rates": {
            "input_per_million": INPUT_RATE,
            "output_per_million": OUTPUT_RATE
        }
    }
    
    # Write to cache file
    cache_file = Path.home() / ".openclaw" / "workspace" / ".cache" / "claude-usage.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_file, "w") as f:
        json.dump(usage_data, f, indent=2)
    
    print(f"✅ Usage updated:")
    print(f"   Today: {tokens_today:,} tokens = ${cost_today:.2f} ({int(cost_today/DAILY_BUDGET*100)}% of daily budget)")
    print(f"   Month: {tokens_month:,} tokens = ${cost_month:.2f} ({int(cost_month/MONTHLY_BUDGET*100)}% of monthly budget)")
    print(f"   Status: {status}")
    print(f"   Saved to: {cache_file}")
    
    # Trigger webhook if needed
    if status != "OK" and webhook_url:
        trigger_webhook(usage_data, status, webhook_url)
    
    return usage_data


def trigger_webhook(usage_data: dict, status: str, webhook_url: str):
    """Send alert to webhook"""
    import urllib.request
    import urllib.error
    
    alert_data = {
        "status": "alert",
        "type": status,
        "message": f"Claude API usage alert: {status}",
        "usage": usage_data
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(alert_data).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"✅ Alert sent to webhook: {response.status}")
    except urllib.error.URLError as e:
        print(f"⚠️  Webhook failed: {e}")


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update Claude API usage log",
        epilog="Example: update-usage.py --today 1500000 --month 25000000"
    )
    parser.add_argument("--today", type=int, required=True, help="Tokens used today")
    parser.add_argument("--month", type=int, required=True, help="Tokens used this month")
    parser.add_argument("--webhook", help="Webhook URL for alerts (optional)")
    
    args = parser.parse_args()
    
    update_usage(args.today, args.month, args.webhook)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive mode if no args
        print("Claude API Usage Updater")
        print("=" * 40)
        try:
            today = int(input("Tokens used today: "))
            month = int(input("Tokens used this month: "))
            update_usage(today, month)
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
            sys.exit(1)
    else:
        main()
