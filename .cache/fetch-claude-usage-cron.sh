#!/bin/bash
# Claude API Usage Fetcher - Cron Job
# Fetches token usage from OpenClaw sessions and calculates costs
# Logs to .cache/claude-usage.json with budget alerts
# 
# Usage: ./fetch-claude-usage-cron.sh
# Cron: 0 * * * * ~/.openclaw/workspace/.cache/fetch-claude-usage-cron.sh

set -e

CACHE_DIR="${HOME}/.openclaw/workspace/.cache"
USAGE_FILE="${CACHE_DIR}/claude-usage.json"

# Ensure cache dir exists
mkdir -p "${CACHE_DIR}"

# Pricing rates (April 2026)
INPUT_RATE_PER_MILLION=0.4      # $0.4 per 1M input tokens
OUTPUT_RATE_PER_MILLION=1.2     # $1.2 per 1M output tokens

# Budgets
BUDGET_DAILY=5.00
BUDGET_MONTHLY=155.00
ALERT_THRESHOLD=0.75  # 75%

# Get timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TODAY=$(date +"%Y-%m-%d")

# Helper: calculate cost
calculate_cost() {
  local input_tokens=$1
  local output_tokens=$2
  
  local input_cost=$(echo "scale=4; $input_tokens * $INPUT_RATE_PER_MILLION / 1000000" | bc 2>/dev/null || echo "0")
  local output_cost=$(echo "scale=4; $output_tokens * $OUTPUT_RATE_PER_MILLION / 1000000" | bc 2>/dev/null || echo "0")
  local total=$(echo "scale=4; $input_cost + $output_cost" | bc 2>/dev/null || echo "0")
  
  echo "$total"
}

# Helper: fetch session token usage
fetch_session_tokens() {
  # Query recent sessions (last 24 hours)
  local sessions_output=$(openclaw sessions list --kinds agent --activeMinutes 1440 --limit 50 2>/dev/null || echo "[]")
  
  echo "$sessions_output"
}

# Main execution
main() {
  echo "📊 Fetching Claude API usage from OpenClaw sessions..."
  
  # Get session data
  local sessions_json=$(fetch_session_tokens)
  
  # Parse token usage from recent sessions
  # Note: This requires parsing OpenClaw session output
  # For now, use a simple estimation based on running sessions
  
  local total_input_tokens=0
  local total_output_tokens=0
  
  # Extract token counts from session history (simplified)
  # In production, this would be more sophisticated
  if command -v jq &> /dev/null; then
    # If we have session metrics, parse them
    total_input_tokens=$(echo "$sessions_json" | jq '[.[].tokens.input // 0] | add' 2>/dev/null || echo "0")
    total_output_tokens=$(echo "$sessions_json" | jq '[.[].tokens.output // 0] | add' 2>/dev/null || echo "0")
  fi
  
  # Calculate costs
  local cost_today=$(calculate_cost "$total_input_tokens" "$total_output_tokens")
  local cost_month=$(echo "scale=4; $cost_today * 20" | bc 2>/dev/null || echo "0")  # Rough monthly
  
  # Determine status
  local daily_percent=$(echo "scale=1; $cost_today / $BUDGET_DAILY * 100" | bc 2>/dev/null || echo "0")
  local monthly_percent=$(echo "scale=1; $cost_month / $BUDGET_MONTHLY * 100" | bc 2>/dev/null || echo "0")
  
  local status="OK"
  local alert_triggered=false
  
  local daily_threshold=$(echo "scale=2; $BUDGET_DAILY * $ALERT_THRESHOLD" | bc 2>/dev/null || echo "$BUDGET_DAILY")
  local monthly_threshold=$(echo "scale=2; $BUDGET_MONTHLY * $ALERT_THRESHOLD" | bc 2>/dev/null || echo "$BUDGET_MONTHLY")
  
  if (( $(echo "$cost_today > $daily_threshold" | bc -l 2>/dev/null || echo "0") )); then
    status="ALERT_DAILY (${daily_percent}%)"
    alert_triggered=true
  elif (( $(echo "$cost_month > $monthly_threshold" | bc -l 2>/dev/null || echo "0") )); then
    status="ALERT_MONTHLY (${monthly_percent}%)"
    alert_triggered=true
  else
    status="OK (Daily: ${daily_percent}% | Monthly: ${monthly_percent}%)"
  fi
  
  # Build JSON output
  local json_output=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "date": "$TODAY",
  "tokens_today": $total_input_tokens,
  "tokens_output_today": $total_output_tokens,
  "cost_today": $cost_today,
  "tokens_month": $(echo "$total_input_tokens * 20" | bc),
  "cost_month": $cost_month,
  "budget_daily": $BUDGET_DAILY,
  "budget_monthly": $BUDGET_MONTHLY,
  "daily_percent": $daily_percent,
  "monthly_percent": $monthly_percent,
  "status": "$status",
  "alert_triggered": $alert_triggered,
  "note": "Token counts aggregated from OpenClaw sessions. See console.anthropic.com for official usage."
}
EOF
)
  
  # Write to cache
  echo "$json_output" > "${USAGE_FILE}"
  
  echo "✅ Logged to ${USAGE_FILE}"
  echo "   Status: $status"
  echo "   Cost Today: \$$cost_today / \$$BUDGET_DAILY"
  echo "   Cost Month: \$$cost_month / \$$BUDGET_MONTHLY"
  
  # Trigger webhook if alert
  if [ "$alert_triggered" = "true" ] && [ -n "$WEBHOOK_MONITOR_URL" ]; then
    echo "🚨 Alert threshold exceeded. Posting webhook..."
    
    local webhook_payload=$(cat <<EOF
{
  "alert_type": "$(echo $status | cut -d' ' -f1)",
  "timestamp": "$TIMESTAMP",
  "cost_today": $cost_today,
  "budget_daily": $BUDGET_DAILY,
  "daily_percent": $daily_percent,
  "cost_month": $cost_month,
  "budget_monthly": $BUDGET_MONTHLY,
  "monthly_percent": $monthly_percent
}
EOF
)
    
    curl -s -X POST "$WEBHOOK_MONITOR_URL" \
      -H "Content-Type: application/json" \
      -d "$webhook_payload" && echo "✅ Webhook sent" || echo "❌ Webhook failed"
  fi
  
  return 0
}

main "$@"
