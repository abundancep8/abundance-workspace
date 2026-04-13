#!/usr/bin/env python3
"""
Manual update helper for Claude API usage metrics.
Use when exporting data from console.anthropic.com/account/usage

Example:
    python3 update-usage.py --tokens-today 12500 --cost-today 2.45 --tokens-month 125000 --cost-month 45.30
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

CACHE_FILE = Path.home() / ".openclaw/workspace/.cache/claude-usage.json"
BUDGET_DAILY = 5.00
BUDGET_MONTHLY = 155.00
ALERT_THRESHOLD_DAILY = BUDGET_DAILY * 0.75
ALERT_THRESHOLD_MONTHLY = BUDGET_MONTHLY * 0.75


def load_cache():
    """Load existing cache or create new one."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tokens_today": 0,
        "cost_today": 0.0,
        "tokens_month": 0,
        "cost_month": 0.0,
        "budget_daily": BUDGET_DAILY,
        "budget_monthly": BUDGET_MONTHLY,
        "status": "ok",
        "last_check": datetime.utcnow().isoformat() + "Z"
    }


def save_cache(data):
    """Save updated cache."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Updated: {CACHE_FILE}")


def check_alerts(data):
    """Check if thresholds exceeded and print alerts."""
    alerts = []
    
    if data["cost_today"] > ALERT_THRESHOLD_DAILY:
        pct = (data["cost_today"] / data["budget_daily"]) * 100
        alerts.append(f"⚠️  Daily budget at {pct:.1f}% (${data['cost_today']:.2f}/${BUDGET_DAILY})")
    
    if data["cost_month"] > ALERT_THRESHOLD_MONTHLY:
        pct = (data["cost_month"] / data["budget_monthly"]) * 100
        alerts.append(f"⚠️  Monthly budget at {pct:.1f}% (${data['cost_month']:.2f}/${BUDGET_MONTHLY})")
    
    if alerts:
        data["status"] = "alert"
        for alert in alerts:
            print(alert, file=sys.stderr)
    else:
        data["status"] = "ok"
        print(f"✓ Daily: ${data['cost_today']:.2f} / ${BUDGET_DAILY} ({(data['cost_today']/BUDGET_DAILY)*100:.1f}%)")
        print(f"✓ Monthly: ${data['cost_month']:.2f} / ${BUDGET_MONTHLY} ({(data['cost_month']/BUDGET_MONTHLY)*100:.1f}%)")
    
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Update Claude API usage metrics from console data"
    )
    parser.add_argument("--tokens-today", type=int, help="Input+output tokens used today")
    parser.add_argument("--cost-today", type=float, help="USD cost for today")
    parser.add_argument("--tokens-month", type=int, help="Input+output tokens used this month")
    parser.add_argument("--cost-month", type=float, help="USD cost for this month")
    parser.add_argument("--show", action="store_true", help="Show current usage without updating")
    
    args = parser.parse_args()
    
    data = load_cache()
    
    if args.show:
        print(json.dumps(data, indent=2))
        return
    
    if not any([args.tokens_today is not None, args.cost_today is not None, 
                args.tokens_month is not None, args.cost_month is not None]):
        parser.print_help()
        sys.exit(1)
    
    if args.tokens_today is not None:
        data["tokens_today"] = args.tokens_today
    if args.cost_today is not None:
        data["cost_today"] = float(args.cost_today)
    if args.tokens_month is not None:
        data["tokens_month"] = args.tokens_month
    if args.cost_month is not None:
        data["cost_month"] = float(args.cost_month)
    
    data["timestamp"] = datetime.utcnow().isoformat() + "Z"
    data["last_check"] = datetime.utcnow().isoformat() + "Z"
    
    data = check_alerts(data)
    save_cache(data)


if __name__ == "__main__":
    main()
