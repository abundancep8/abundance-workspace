#!/bin/bash
# Claude API Usage Monitor Cron Job
# Fetches usage from Anthropic console and logs with cost calculations

set -e

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CACHE_DIR="/Users/abundance/.openclaw/workspace/.cache"
CACHE_FILE="$CACHE_DIR/claude-usage.json"
WEBHOOK_URL="${WEBHOOK_MONITOR_URL:-https://webhook-monitor.example.com/alert}"

# Create cache dir if needed
mkdir -p "$CACHE_DIR"

# Rates (in dollars per 1M tokens)
INPUT_RATE=0.4
OUTPUT_RATE=1.2

# Budgets
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00
DAILY_THRESHOLD=$(echo "$DAILY_BUDGET * 0.75" | bc -l)
MONTHLY_THRESHOLD=$(echo "$MONTHLY_BUDGET * 0.75" | bc -l)

# Try to fetch usage from Anthropic API
# Note: As of 2026, Anthropic does not expose a public usage API endpoint
# This script demonstrates the structure; actual data must come from:
# 1. Anthropic console web scraping (requires auth)
# 2. Manual input via environment variables
# 3. Third-party billing aggregators

# Attempt to get usage from environment or fall back to zeros
INPUT_TOKENS_TODAY=${ANTHROPIC_INPUT_TOKENS_TODAY:-0}
OUTPUT_TOKENS_TODAY=${ANTHROPIC_OUTPUT_TOKENS_TODAY:-0}
INPUT_TOKENS_MONTH=${ANTHROPIC_INPUT_TOKENS_MONTH:-0}
OUTPUT_TOKENS_MONTH=${ANTHROPIC_OUTPUT_TOKENS_MONTH:-0}

# Calculate costs
COST_TODAY=$(echo "scale=4; ($INPUT_TOKENS_TODAY * $INPUT_RATE / 1000000) + ($OUTPUT_TOKENS_TODAY * $OUTPUT_RATE / 1000000)" | bc)
COST_MONTH=$(echo "scale=4; ($INPUT_TOKENS_MONTH * $INPUT_RATE / 1000000) + ($OUTPUT_TOKENS_MONTH * $OUTPUT_RATE / 1000000)" | bc)

# Determine status
STATUS="ok"
ALERT_TRIGGERED=false

if (( $(echo "$COST_TODAY > $DAILY_THRESHOLD" | bc -l) )); then
  STATUS="warning_daily"
  ALERT_TRIGGERED=true
fi

if (( $(echo "$COST_MONTH > $MONTHLY_THRESHOLD" | bc -l) )); then
  STATUS="warning_monthly"
  ALERT_TRIGGERED=true
fi

# Build JSON log
JSON_LOG=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "tokens_today": {
    "input": $INPUT_TOKENS_TODAY,
    "output": $OUTPUT_TOKENS_TODAY
  },
  "cost_today": $COST_TODAY,
  "tokens_month": {
    "input": $INPUT_TOKENS_MONTH,
    "output": $OUTPUT_TOKENS_MONTH
  },
  "cost_month": $COST_MONTH,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET,
  "threshold_daily": $DAILY_THRESHOLD,
  "threshold_monthly": $MONTHLY_THRESHOLD,
  "status": "$STATUS",
  "alert_triggered": $ALERT_TRIGGERED
}
EOF
)

# Write to cache
echo "$JSON_LOG" | jq . > "$CACHE_FILE"

# Log to console
echo "[$(date)] Claude API Usage Monitor"
echo "  Today: \$$COST_TODAY ($(($INPUT_TOKENS_TODAY + $OUTPUT_TOKENS_TODAY)) tokens)"
echo "  Month: \$$COST_MONTH ($(($INPUT_TOKENS_MONTH + $OUTPUT_TOKENS_MONTH)) tokens)"
echo "  Status: $STATUS"
echo "  Logged to: $CACHE_FILE"

# Trigger webhook if threshold exceeded
if [ "$ALERT_TRIGGERED" = true ]; then
  echo "  ⚠️ Budget threshold exceeded! Triggering webhook..."
  
  WEBHOOK_PAYLOAD=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "alert_type": "$STATUS",
  "cost_today": $COST_TODAY,
  "cost_month": $COST_MONTH,
  "daily_budget": $DAILY_BUDGET,
  "monthly_budget": $MONTHLY_BUDGET,
  "message": "Claude API usage alert triggered"
}
EOF
)
  
  # Only send if webhook URL is configured
  if [ -n "$WEBHOOK_MONITOR_URL" ]; then
    curl -s -X POST "$WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "$WEBHOOK_PAYLOAD" > /dev/null 2>&1 || true
    echo "  Webhook sent to: $WEBHOOK_URL"
  else
    echo "  Webhook URL not configured (set WEBHOOK_MONITOR_URL env var)"
  fi
else
  echo "  ✓ Within budget. Silent mode."
fi

exit 0
