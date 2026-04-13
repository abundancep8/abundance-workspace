#!/usr/bin/env python3
"""
Claude API Usage Monitor
Fetches usage data from Anthropic Console and tracks costs with alerts.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess
import requests

# Configuration
CACHE_FILE = Path.home() / ".openclaw/workspace/.cache/claude-usage.json"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Pricing rates (2026)
INPUT_RATE = 0.4 / 1_000_000  # $0.4 per 1M tokens
OUTPUT_RATE = 1.2 / 1_000_000  # $1.2 per 1M tokens

# Budgets
DAILY_BUDGET = 5.00
MONTHLY_BUDGET = 155.00
DAILY_ALERT_THRESHOLD = 3.75  # 75%
MONTHLY_ALERT_THRESHOLD = 116.25  # 75%


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate cost from token counts."""
    return (input_tokens * INPUT_RATE) + (output_tokens * OUTPUT_RATE)


def fetch_from_console_browser() -> dict:
    """
    Fetch usage data using browser automation.
    Requires chromium and playwright or similar.
    """
    try:
        result = subprocess.run(
            [
                "node",
                "-e",
                """
const playwright = require('playwright');
(async () => {
    const browser = await playwright.chromium.launch();
    const page = await browser.newPage();
    await page.goto('https://console.anthropic.com/account/usage');
    
    // Wait for data to load
    await page.waitForLoadState('networkidle');
    
    // Try to extract usage data from the page
    const data = await page.evaluate(() => {
        // Look for usage stats in the DOM
        const tokens = document.querySelector('[data-testid="usage-tokens"]')?.textContent || null;
        const cost = document.querySelector('[data-testid="usage-cost"]')?.textContent || null;
        return { tokens, cost };
    });
    
    console.log(JSON.stringify(data));
    await browser.close();
})();
                """,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Browser automation failed: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Could not use browser automation: {e}", file=sys.stderr)
        return None


def log_usage(
    input_tokens_today: int,
    output_tokens_today: int,
    input_tokens_month: int,
    output_tokens_month: int,
):
    """Log usage data and check thresholds."""

    timestamp = datetime.utcnow().isoformat() + "Z"
    tokens_today = input_tokens_today + output_tokens_today
    tokens_month = input_tokens_month + output_tokens_month

    cost_today = calculate_cost(input_tokens_today, output_tokens_today)
    cost_month = calculate_cost(input_tokens_month, output_tokens_month)

    percent_daily = (cost_today / DAILY_BUDGET) * 100
    percent_monthly = (cost_month / MONTHLY_BUDGET) * 100

    # Determine status
    status = "ok"
    alert_triggered = False

    if cost_today > DAILY_ALERT_THRESHOLD:
        status = "warning_daily"
        alert_triggered = True
        print(f"⚠️  Daily budget alert: ${cost_today:.4f} / ${DAILY_BUDGET:.2f}")

    if cost_month > MONTHLY_ALERT_THRESHOLD:
        status = "warning_monthly"
        alert_triggered = True
        print(f"⚠️  Monthly budget alert: ${cost_month:.4f} / ${MONTHLY_BUDGET:.2f}")

    # Build log entry
    log_entry = {
        "timestamp": timestamp,
        "tokens_today": tokens_today,
        "input_tokens_today": input_tokens_today,
        "output_tokens_today": output_tokens_today,
        "cost_today": round(cost_today, 4),
        "tokens_month": tokens_month,
        "input_tokens_month": input_tokens_month,
        "output_tokens_month": output_tokens_month,
        "cost_month": round(cost_month, 4),
        "budget_daily": DAILY_BUDGET,
        "budget_monthly": MONTHLY_BUDGET,
        "percent_daily": round(percent_daily, 1),
        "percent_monthly": round(percent_monthly, 1),
        "status": status,
    }

    # Write to cache
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(log_entry, f, indent=2)

    print(f"✅ Logged to {CACHE_FILE}")
    print(json.dumps(log_entry, indent=2))

    # Send webhook if needed
    if alert_triggered and WEBHOOK_URL:
        print(f"🔔 Triggering webhook alert...")
        try:
            response = requests.post(
                WEBHOOK_URL, json=log_entry, timeout=10
            )
            response.raise_for_status()
            print("✅ Webhook sent")
        except Exception as e:
            print(f"❌ Webhook failed: {e}")

    return log_entry


def main():
    """Main entry point."""
    print("📊 Claude API Usage Monitor")
    print(f"⏰ {datetime.utcnow().isoformat()}Z")
    print()

    # Try to get data from environment variables first
    usage_daily = os.getenv("USAGE_DATA_DAILY", "")
    usage_month = os.getenv("USAGE_DATA_MONTH", "")

    if usage_daily and usage_month:
        # Parse: "input=123456 output=789012"
        daily_parts = dict(
            part.split("=") for part in usage_daily.split()
        )
        month_parts = dict(
            part.split("=") for part in usage_month.split()
        )

        input_today = int(daily_parts.get("input", 0))
        output_today = int(daily_parts.get("output", 0))
        input_month = int(month_parts.get("input", 0))
        output_month = int(month_parts.get("output", 0))

        print("✅ Using environment data")
        log_usage(input_today, output_today, input_month, output_month)
    else:
        print(
            "ℹ️  No environment data. To use this script, set:"
        )
        print(
            "  export USAGE_DATA_DAILY='input=123456 output=789012'"
        )
        print(
            "  export USAGE_DATA_MONTH='input=1234567 output=7890123'"
        )
        print()
        print("Or configure browser automation for automatic fetching.")
        sys.exit(1)


if __name__ == "__main__":
    main()
