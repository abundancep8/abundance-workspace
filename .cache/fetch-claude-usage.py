#!/usr/bin/env python3
"""
Claude API Usage Fetcher - Cron Job
Fetches Claude API usage and logs to JSON with cost tracking and alerts.

This script:
1. Queries OpenClaw session history for recent token usage
2. Calculates costs based on Anthropic rates
3. Logs to .cache/claude-usage.json
4. Triggers webhook if 75% of budget is exceeded

Usage:
  ./fetch-claude-usage.py
  
Cron:
  0 * * * * ~/.openclaw/workspace/.cache/fetch-claude-usage.py

Environment:
  WEBHOOK_MONITOR_URL - Optional webhook to POST alerts to
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re

# Configuration
CACHE_DIR = Path.home() / ".openclaw/workspace/.cache"
USAGE_FILE = CACHE_DIR / "claude-usage.json"
LOGS_DIR = Path.home() / ".openclaw/workspace/.cache/logs"

# Ensure cache dir exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Pricing rates (April 2026 - Haiku)
RATES = {
    "input": 0.4 / 1_000_000,      # $0.4 per 1M input tokens
    "output": 1.2 / 1_000_000,     # $1.2 per 1M output tokens
}

# Budgets
BUDGET_DAILY = 5.00
BUDGET_MONTHLY = 155.00
ALERT_THRESHOLD = 0.75  # 75%

# Webhook
WEBHOOK_URL = os.getenv("WEBHOOK_MONITOR_URL")

def get_timestamp():
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def get_date():
    """Get current date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def fetch_openclaw_sessions():
    """
    Fetch recent OpenClaw session metrics.
    Queries the session history for token usage.
    """
    try:
        # Run openclaw sessions_list command
        result = subprocess.run(
            ["openclaw", "sessions", "list", "--kinds", "agent", "--activeMinutes", "1440", "--limit", "20"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Parse output (it's likely text-based, not JSON)
            return result.stdout
        return None
    except Exception as e:
        print(f"⚠️  Failed to fetch OpenClaw sessions: {e}", file=sys.stderr)
        return None

def parse_session_log_file():
    """
    Parse recent session log files to extract token usage.
    Looks for patterns like "tokens_in: X, tokens_out: Y"
    """
    total_input_tokens = 0
    total_output_tokens = 0
    
    try:
        if not LOGS_DIR.exists():
            return total_input_tokens, total_output_tokens
        
        # Look at recent log files (last 24 hours)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)
        
        for log_file in sorted(LOGS_DIR.glob("*.log"), reverse=True)[:10]:
            try:
                if log_file.stat().st_mtime < cutoff.timestamp():
                    continue
                
                content = log_file.read_text(errors='ignore')
                
                # Look for token patterns
                # Pattern 1: "🧮 Tokens: 99 in / 2.4k out"
                match = re.search(r'🧮\s*Tokens:\s*([\d.k]+)\s*in\s*/\s*([\d.k]+)\s*out', content)
                if match:
                    in_tokens = parse_token_count(match.group(1))
                    out_tokens = parse_token_count(match.group(2))
                    total_input_tokens += in_tokens
                    total_output_tokens += out_tokens
                
                # Pattern 2: Direct token counts
                matches = re.findall(r'tokens[:\s]+(\d+).*out.*?(\d+)', content, re.IGNORECASE)
                for match in matches:
                    total_input_tokens += int(match[0])
                    total_output_tokens += int(match[1])
                    
            except Exception as e:
                print(f"⚠️  Error parsing {log_file.name}: {e}", file=sys.stderr)
                continue
        
        return total_input_tokens, total_output_tokens
    except Exception as e:
        print(f"⚠️  Error scanning log files: {e}", file=sys.stderr)
        return 0, 0

def parse_token_count(s):
    """Parse token count strings like '99', '2.4k', etc."""
    s = str(s).lower().strip()
    try:
        if 'k' in s:
            return int(float(s.replace('k', '')) * 1000)
        elif 'm' in s:
            return int(float(s.replace('m', '')) * 1_000_000)
        else:
            return int(float(s))
    except:
        return 0

def estimate_tokens_from_memory():
    """
    Estimate tokens based on memory/session files.
    Fallback when direct token counts aren't available.
    """
    memory_dir = Path.home() / ".openclaw/workspace/memory"
    total_tokens = 0
    
    try:
        if not memory_dir.exists():
            return 0
        
        # Get files from last 24 hours
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)
        
        for f in memory_dir.glob("*.md"):
            if f.stat().st_mtime >= cutoff.timestamp():
                # Rough estimation: 4 chars ≈ 1 token
                content = f.read_text(errors='ignore')
                tokens = len(content) // 4
                total_tokens += tokens
    except:
        pass
    
    return total_tokens

def calculate_costs(input_tokens, output_tokens):
    """Calculate costs based on token counts and rates."""
    cost_input = input_tokens * RATES["input"]
    cost_output = output_tokens * RATES["output"]
    total_cost = cost_input + cost_output
    return round(total_cost, 4)

def determine_status(cost_today, cost_month):
    """Determine status based on budget thresholds."""
    daily_threshold = BUDGET_DAILY * ALERT_THRESHOLD
    monthly_threshold = BUDGET_MONTHLY * ALERT_THRESHOLD
    
    daily_percent = round((cost_today / BUDGET_DAILY) * 100, 1) if BUDGET_DAILY > 0 else 0
    monthly_percent = round((cost_month / BUDGET_MONTHLY) * 100, 1) if BUDGET_MONTHLY > 0 else 0
    
    alert_triggered = False
    status = "OK"
    
    if cost_today > daily_threshold:
        status = f"ALERT_DAILY ({daily_percent}%)"
        alert_triggered = True
    elif cost_month > monthly_threshold:
        status = f"ALERT_MONTHLY ({monthly_percent}%)"
        alert_triggered = True
    else:
        status = f"OK (Daily: {daily_percent}% | Monthly: {monthly_percent}%)"
    
    return status, alert_triggered, daily_percent, monthly_percent

def post_webhook_alert(data):
    """Post alert to webhook if configured."""
    if not WEBHOOK_URL:
        return False
    
    try:
        payload = json.dumps({
            "alert_type": data["status"].split("(")[0].strip(),
            "timestamp": data["timestamp"],
            "cost_today": data["cost_today"],
            "budget_daily": data["budget_daily"],
            "daily_percent": data["daily_percent"],
            "cost_month": data["cost_month"],
            "budget_monthly": data["budget_monthly"],
            "monthly_percent": data["monthly_percent"],
        })
        
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", WEBHOOK_URL, 
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True,
            timeout=10
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Webhook post failed: {e}", file=sys.stderr)
        return False

def main():
    """Main execution."""
    print("📊 Fetching Claude API usage...")
    
    # Try to get tokens from logs
    input_tokens, output_tokens = parse_session_log_file()
    
    # If minimal tokens, try estimation
    if input_tokens + output_tokens < 100:
        estimate = estimate_tokens_from_memory()
        if estimate > 0:
            input_tokens = estimate
            output_tokens = estimate // 3  # Rough ratio
    
    # Calculate costs
    cost_today = calculate_costs(input_tokens, output_tokens)
    cost_month = cost_today * 20  # Rough estimate: 20 business days
    
    # Determine status
    status, alert_triggered, daily_percent, monthly_percent = determine_status(cost_today, cost_month)
    
    # Build log entry
    log_entry = {
        "timestamp": get_timestamp(),
        "date": get_date(),
        "tokens_today": input_tokens,
        "tokens_output_today": output_tokens,
        "cost_today": cost_today,
        "tokens_month": input_tokens * 20,
        "cost_month": cost_month,
        "budget_daily": BUDGET_DAILY,
        "budget_monthly": BUDGET_MONTHLY,
        "daily_percent": daily_percent,
        "monthly_percent": monthly_percent,
        "status": status,
        "alert_triggered": alert_triggered,
        "note": "Tokens estimated from OpenClaw session logs. For official usage, check console.anthropic.com"
    }
    
    # Write to cache
    USAGE_FILE.write_text(json.dumps(log_entry, indent=2))
    print(f"✅ Logged to {USAGE_FILE}")
    print(f"   Status: {status}")
    print(f"   Tokens: {input_tokens:,} in / {output_tokens:,} out")
    print(f"   Cost Today: ${cost_today:.2f} / ${BUDGET_DAILY}")
    print(f"   Cost Month: ${cost_month:.2f} / ${BUDGET_MONTHLY}")
    
    # Post webhook if alert
    if alert_triggered:
        print("🚨 Alert threshold exceeded. Posting webhook...")
        if post_webhook_alert(log_entry):
            print("✅ Webhook posted")
        else:
            print("⚠️  Webhook failed or not configured")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
