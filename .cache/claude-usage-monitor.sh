#!/bin/bash
# Claude API Usage Monitor
# Fetches usage data and logs cost tracking
# Requirements: ANTHROPIC_API_KEY or browser-based auth

set -e

CACHE_FILE="$HOME/.openclaw/workspace/.cache/claude-usage.json"
WEBHOOK_URL="${WEBHOOK_URL:-}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Pricing rates (as of 2026)
INPUT_RATE=0.4      # $0.4 per 1M input tokens
OUTPUT_RATE=1.2     # $1.2 per 1M output tokens

# Budget thresholds
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00
DAILY_ALERT_THRESHOLD=3.75    # 75% of $5.00
MONTHLY_ALERT_THRESHOLD=116.25 # 75% of $155.00

# Function to fetch usage from API
fetch_usage_from_api() {
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "❌ ANTHROPIC_API_KEY not set. Cannot fetch usage via API." >&2
        return 1
    fi
    
    # Note: As of now, Anthropic doesn't have a public API endpoint for usage data
    # This would need to be implemented when/if Anthropic releases such an endpoint
    # For now, we'll need to use browser automation or manual updates
    
    echo "⚠️  No public API endpoint available for usage data." >&2
    return 1
}

# Function to calculate cost
calculate_cost() {
    local input_tokens=$1
    local output_tokens=$2
    local input_cost=$(echo "scale=4; $input_tokens * $INPUT_RATE / 1000000" | bc)
    local output_cost=$(echo "echo "scale=4; $output_tokens * $OUTPUT_RATE / 1000000" | bc)
    echo "$(echo "$input_cost + $output_cost" | bc)"
}

# Function to log usage
log_usage() {
    local tokens_today=$1
    local tokens_month=$2
    local input_tokens_today=$3
    local output_tokens_today=$4
    local input_tokens_month=$5
    local output_tokens_month=$6
    
    local cost_today=$(calculate_cost $input_tokens_today $output_tokens_today)
    local cost_month=$(calculate_cost $input_tokens_month $output_tokens_month)
    
    local status="ok"
    local alert_triggered=0
    
    # Check if we've exceeded thresholds
    if (( $(echo "$cost_today > $DAILY_ALERT_THRESHOLD" | bc -l) )); then
        status="warning_daily"
        alert_triggered=1
    fi
    
    if (( $(echo "$cost_month > $MONTHLY_ALERT_THRESHOLD" | bc -l) )); then
        status="warning_monthly"
        alert_triggered=1
    fi
    
    # Create log entry
    local log_entry=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "tokens_today": $tokens_today,
  "input_tokens_today": $input_tokens_today,
  "output_tokens_today": $output_tokens_today,
  "cost_today": $cost_today,
  "tokens_month": $tokens_month,
  "input_tokens_month": $input_tokens_month,
  "output_tokens_month": $output_tokens_month,
  "cost_month": $cost_month,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET,
  "percent_daily": $(echo "scale=1; $cost_today * 100 / $DAILY_BUDGET" | bc),
  "percent_monthly": $(echo "scale=1; $cost_month * 100 / $MONTHLY_BUDGET" | bc),
  "status": "$status"
}
EOF
)
    
    # Write to cache
    mkdir -p "$(dirname "$CACHE_FILE")"
    echo "$log_entry" > "$CACHE_FILE"
    
    echo "✅ Logged to $CACHE_FILE"
    echo "$log_entry" | jq .
    
    # Trigger webhook if needed
    if [ $alert_triggered -eq 1 ] && [ -n "$WEBHOOK_URL" ]; then
        echo "🔔 Triggering webhook alert..."
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "$log_entry" \
            -s -o /dev/null && echo "✅ Webhook sent" || echo "❌ Webhook failed"
    fi
}

# Main execution
echo "📊 Claude API Usage Monitor"
echo "⏰ $TIMESTAMP"
echo ""

# Try API first
if fetch_usage_from_api; then
    echo "✅ Fetched from API"
else
    echo "⚠️  API method unavailable. Please update usage manually:"
    echo ""
    echo "  export USAGE_DATA_DAILY='input=123456 output=789012'"
    echo "  export USAGE_DATA_MONTH='input=1234567 output=7890123'"
    echo "  $0"
    echo ""
    
    # Check for manual input
    if [ -z "$USAGE_DATA_DAILY" ] || [ -z "$USAGE_DATA_MONTH" ]; then
        echo "❌ No usage data provided. Exiting."
        exit 1
    fi
    
    # Parse environment variables
    IFS=' ' read -r -a DAILY_PARTS <<< "$USAGE_DATA_DAILY"
    IFS=' ' read -r -a MONTH_PARTS <<< "$USAGE_DATA_MONTH"
    
    INPUT_TODAY=${DAILY_PARTS[0]#input=}
    OUTPUT_TODAY=${DAILY_PARTS[1]#output=}
    INPUT_MONTH=${MONTH_PARTS[0]#input=}
    OUTPUT_MONTH=${MONTH_PARTS[1]#output=}
    
    TOTAL_TODAY=$((INPUT_TODAY + OUTPUT_TODAY))
    TOTAL_MONTH=$((INPUT_MONTH + OUTPUT_MONTH))
    
    log_usage $TOTAL_TODAY $TOTAL_MONTH $INPUT_TODAY $OUTPUT_TODAY $INPUT_MONTH $OUTPUT_MONTH
fi
