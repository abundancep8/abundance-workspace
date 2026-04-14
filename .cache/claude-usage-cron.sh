#!/bin/bash

# Claude API Usage Monitor - Cron Script
# Fetches usage from Anthropic console and logs to .cache/claude-usage.json
# Triggers webhook if thresholds exceeded

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
OUTPUT_FILE="$CACHE_DIR/claude-usage.json"
WEBHOOK_URL="${WEBHOOK_MONITOR_URL:-}"

# Ensure cache dir exists
mkdir -p "$CACHE_DIR"

# Pricing rates (per 1M tokens)
INPUT_RATE=0.4
OUTPUT_RATE=1.2

# Budget thresholds
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00
DAILY_ALERT_THRESHOLD=3.75  # 75% of daily
MONTHLY_ALERT_THRESHOLD=116.25  # 75% of monthly

# Timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# NOTE: Anthropic doesn't have a public usage API.
# This script requires manual data entry or browser automation with stored credentials.
# For now, we'll create a placeholder that can be filled via:
# 1. Manual API calls if Anthropic adds an API endpoint
# 2. Browser automation with headless Chrome + stored credentials
# 3. Parsing usage from email notifications

# Attempt to read from environment or config file
if [ -f "$CACHE_DIR/claude-usage-config.json" ]; then
  # Config file with last known values
  CONFIG=$(cat "$CACHE_DIR/claude-usage-config.json")
else
  # Fallback: manual input or placeholder
  CONFIG='{"tokens_today": 0, "tokens_today_input": 0, "tokens_today_output": 0, "tokens_month": 0, "tokens_month_input": 0, "tokens_month_output": 0}'
fi

# Parse config
TOKENS_TODAY_INPUT=$(echo "$CONFIG" | jq -r '.tokens_today_input // 0')
TOKENS_TODAY_OUTPUT=$(echo "$CONFIG" | jq -r '.tokens_today_output // 0')
TOKENS_MONTH_INPUT=$(echo "$CONFIG" | jq -r '.tokens_month_input // 0')
TOKENS_MONTH_OUTPUT=$(echo "$CONFIG" | jq -r '.tokens_month_output // 0')

# Calculate totals and costs
TOKENS_TODAY=$((TOKENS_TODAY_INPUT + TOKENS_TODAY_OUTPUT))
TOKENS_MONTH=$((TOKENS_MONTH_INPUT + TOKENS_MONTH_OUTPUT))

COST_TODAY=$(awk -v input="$TOKENS_TODAY_INPUT" -v output="$TOKENS_TODAY_OUTPUT" -v ir="$INPUT_RATE" -v or="$OUTPUT_RATE" \
  'BEGIN {printf "%.2f", (input * ir / 1000000) + (output * or / 1000000)}')

COST_MONTH=$(awk -v input="$TOKENS_MONTH_INPUT" -v output="$TOKENS_MONTH_OUTPUT" -v ir="$INPUT_RATE" -v or="$OUTPUT_RATE" \
  'BEGIN {printf "%.2f", (input * ir / 1000000) + (output * or / 1000000)}')

# Determine status
STATUS="normal"
ALERT_REASON=""

if (( $(echo "$COST_TODAY > $DAILY_ALERT_THRESHOLD" | bc -l) )); then
  STATUS="warning"
  ALERT_REASON="Daily spend at ${COST_TODAY}% of \$${DAILY_BUDGET} budget"
fi

if (( $(echo "$COST_MONTH > $MONTHLY_ALERT_THRESHOLD" | bc -l) )); then
  STATUS="warning"
  ALERT_REASON="Monthly spend at ${COST_MONTH}% of \$${MONTHLY_BUDGET} budget"
fi

# Create output JSON
OUTPUT_JSON=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "tokens_today": $TOKENS_TODAY,
  "tokens_today_breakdown": {
    "input": $TOKENS_TODAY_INPUT,
    "output": $TOKENS_TODAY_OUTPUT
  },
  "cost_today": $COST_TODAY,
  "tokens_month": $TOKENS_MONTH,
  "tokens_month_breakdown": {
    "input": $TOKENS_MONTH_INPUT,
    "output": $TOKENS_MONTH_OUTPUT
  },
  "cost_month": $COST_MONTH,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET,
  "status": "$STATUS",
  "alert_reason": "$ALERT_REASON"
}
EOF
)

# Log to file
echo "$OUTPUT_JSON" | jq . > "$OUTPUT_FILE"
echo "[$(date)] Logged Claude usage: status=$STATUS, cost_today=\$$COST_TODAY, cost_month=\$$COST_MONTH"

# Trigger webhook if alert
if [ "$STATUS" = "warning" ] && [ -n "$WEBHOOK_URL" ]; then
  WEBHOOK_PAYLOAD=$(cat <<EOF
{
  "event": "claude_usage_alert",
  "timestamp": "$TIMESTAMP",
  "status": "$STATUS",
  "alert_reason": "$ALERT_REASON",
  "cost_today": $COST_TODAY,
  "cost_month": $COST_MONTH,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET
}
EOF
)
  
  curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$WEBHOOK_PAYLOAD" || echo "[$(date)] Webhook POST failed"
fi
