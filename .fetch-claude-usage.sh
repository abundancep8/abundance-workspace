#!/bin/bash
# fetch-claude-usage.sh
# Fetch Claude API usage from Anthropic Console and log to ~/.cache/claude-usage.json
# Requires: Authentication via browser session OR Anthropic API key

set -e

CACHE_FILE="$HOME/.cache/claude-usage.json"
WEBHOOK_URL="${WEBHOOK_MONITOR_URL:-}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Cost rates for Claude Haiku
INPUT_RATE=0.4    # $ per 1M tokens
OUTPUT_RATE=1.2   # $ per 1M tokens

# Budgets
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00
ALERT_THRESHOLD_DAILY=0.75  # 75% = $3.75
ALERT_THRESHOLD_MONTHLY=0.75

# --- Option 1: Fetch via Browser (requires authenticated session) ---
fetch_via_browser() {
  echo "[$(date)] Attempting to fetch usage from Anthropic Console via browser..."
  
  # Note: This would require browser automation to scrape the page
  # For now, this is a placeholder that would need to be implemented
  # with Playwright or similar when session is available
  
  echo "ERROR: Browser-based fetching not yet implemented."
  echo "See SETUP_NEEDED.md for options."
  return 1
}

# --- Option 2: Fetch via Anthropic API (if endpoint exists) ---
fetch_via_api() {
  if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set"
    return 1
  fi
  
  echo "[$(date)] Fetching usage from Anthropic API..."
  
  # TODO: Replace with actual Anthropic API endpoint when available
  # This is a placeholder for when Anthropic releases a usage API
  
  curl -s -X GET "https://api.anthropic.com/v1/usage" \
    -H "x-api-key: $ANTHROPIC_API_KEY" || {
    echo "ERROR: API request failed"
    return 1
  }
}

# --- Check Budget Thresholds ---
check_budget() {
  local cost_today=$1
  local cost_month=$2
  local alert_level=""
  
  local alert_daily=$(echo "$DAILY_BUDGET * $ALERT_THRESHOLD_DAILY" | bc)
  local alert_monthly=$(echo "$MONTHLY_BUDGET * $ALERT_THRESHOLD_MONTHLY" | bc)
  
  if (( $(echo "$cost_today > $alert_daily" | bc -l) )); then
    alert_level="daily_warning"
  fi
  
  if (( $(echo "$cost_month > $alert_monthly" | bc -l) )); then
    alert_level="monthly_warning"
  fi
  
  if [ -n "$WEBHOOK_URL" ] && [ -n "$alert_level" ]; then
    send_webhook_alert "$cost_today" "$cost_month" "$alert_level"
  fi
  
  echo "$alert_level"
}

# --- Send Webhook Alert ---
send_webhook_alert() {
  local cost_today=$1
  local cost_month=$2
  local alert_level=$3
  
  echo "[$(date)] Sending webhook alert: $alert_level"
  
  payload=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "alert_level": "$alert_level",
  "cost_today": $cost_today,
  "cost_month": $cost_month,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET
}
EOF
  )
  
  curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$payload" || echo "[$(date)] WARNING: Webhook send failed"
}

# --- Main ---
main() {
  # Try authentication methods in order
  if fetch_via_api > /dev/null 2>&1; then
    # API method succeeded
    usage_data=$(fetch_via_api)
    tokens_today=$(echo "$usage_data" | jq -r '.tokens_today // 0')
    tokens_month=$(echo "$usage_data" | jq -r '.tokens_month // 0')
  elif fetch_via_browser > /dev/null 2>&1; then
    # Browser method succeeded
    usage_data=$(fetch_via_browser)
    tokens_today=$(echo "$usage_data" | jq -r '.tokens_today // 0')
    tokens_month=$(echo "$usage_data" | jq -r '.tokens_month // 0')
  else
    # No auth available
    echo "[$(date)] ERROR: No authentication method available"
    echo "See SETUP_NEEDED.md for setup instructions"
    
    # Log auth error
    cat > "$CACHE_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "status": "auth_required",
  "note": "No authentication available. See SETUP_NEEDED.md",
  "tokens_today": 0,
  "cost_today": 0,
  "tokens_month": 0,
  "cost_month": 0,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET,
  "alert_triggered": false
}
EOF
    exit 1
  fi
  
  # Calculate costs
  cost_today=$(echo "scale=2; $tokens_today * $INPUT_RATE / 1000000" | bc)
  cost_month=$(echo "scale=2; $tokens_month * $OUTPUT_RATE / 1000000" | bc)
  
  # Check thresholds
  alert_status=$(check_budget "$cost_today" "$cost_month")
  alert_triggered=$([ -n "$alert_status" ] && echo "true" || echo "false")
  
  # Log to cache
  cat > "$CACHE_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "tokens_today": $tokens_today,
  "cost_today": $cost_today,
  "tokens_month": $tokens_month,
  "cost_month": $cost_month,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET,
  "alert_triggered": $alert_triggered,
  "alert_status": "$alert_status",
  "status": "ok"
}
EOF
  
  if [ "$alert_triggered" = "true" ]; then
    echo "[$(date)] ALERT: Budget threshold exceeded! ($alert_status)"
  else
    echo "[$(date)] Usage logged (no alerts)"
  fi
}

main "$@"
