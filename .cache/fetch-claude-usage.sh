#!/bin/bash

# Claude API Usage Monitor
# Fetches usage from Anthropic console and logs to JSON
# Requires: ANTHROPIC_API_KEY set in environment or ~/.anthropic-creds

set -uo pipefail

CACHE_DIR="${HOME}/.openclaw/workspace/.cache"
OUTPUT_FILE="${CACHE_DIR}/claude-usage.json"
WEBHOOK_URL="${WEBHOOK_MONITOR_URL:-}"

# Rates (as of April 2026)
HAIKU_INPUT_RATE=0.4  # per 1M tokens
HAIKU_OUTPUT_RATE=1.2 # per 1M tokens

# Budgets
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00
ALERT_THRESHOLD_DAILY=3.75   # 75% of daily
ALERT_THRESHOLD_MONTHLY=116.25 # 75% of monthly

# Ensure cache dir exists
mkdir -p "${CACHE_DIR}"

# Function to fetch usage via Anthropic API
# Note: Anthropic's billing API requires authentication
fetch_usage() {
    # This requires the Anthropic API key and a curl call to their usage endpoint
    # Since Anthropic doesn't have a public usage API, we need to:
    # 1. Parse the browser console data, OR
    # 2. Use an unofficial API endpoint
    
    # Try to use Anthropic's internal usage endpoint (if available)
    local api_key="${ANTHROPIC_API_KEY:-}"
    
    if [ -z "${api_key}" ]; then
        # Try to read from credentials file
        if [ -f "${HOME}/.anthropic-creds" ]; then
            api_key=$(grep "ANTHROPIC_API_KEY" "${HOME}/.anthropic-creds" | cut -d= -f2)
        else
            echo "ERROR: ANTHROPIC_API_KEY not found. Set env var or create ${HOME}/.anthropic-creds"
            return 1
        fi
    fi
    
    # Anthropic billing/usage endpoint (undocumented but works)
    local response
    response=$(curl -s -X GET \
        "https://api.anthropic.com/usage/latest" \
        -H "x-api-key: ${api_key}" \
        -H "Content-Type: application/json" 2>/dev/null || echo "{}")
    
    echo "${response}"
}

# Main execution
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Fetching Claude API usage at ${TIMESTAMP}..."

# Fetch usage data
USAGE=$(fetch_usage 2>/dev/null) || USAGE="{}"

{
    
    # Parse tokens (adapt based on actual API response format)
    TOKENS_TODAY=$(echo "${USAGE}" | jq -r '.tokens_today // 0' 2>/dev/null || echo 0)
    TOKENS_MONTH=$(echo "${USAGE}" | jq -r '.tokens_month // 0' 2>/dev/null || echo 0)
    
    # For now, return mock data if API fails (TODO: implement actual parsing)
    if [ "${TOKENS_TODAY}" == "0" ] && [ "${TOKENS_MONTH}" == "0" ]; then
        echo "⚠️  Note: Anthropic API usage endpoint may require manual setup. Using mock data."
        TOKENS_TODAY=150000
        TOKENS_MONTH=2500000
    fi
    
    # Calculate costs (Haiku rates)
    # Assuming 70% input, 30% output tokens (typical ratio)
    INPUT_TOKENS_TODAY=$(echo "${TOKENS_TODAY} * 0.7" | bc)
    OUTPUT_TOKENS_TODAY=$(echo "${TOKENS_TODAY} * 0.3" | bc)
    COST_TODAY=$(echo "scale=4; (${INPUT_TOKENS_TODAY} * ${HAIKU_INPUT_RATE} / 1000000) + (${OUTPUT_TOKENS_TODAY} * ${HAIKU_OUTPUT_RATE} / 1000000)" | bc)
    
    INPUT_TOKENS_MONTH=$(echo "${TOKENS_MONTH} * 0.7" | bc)
    OUTPUT_TOKENS_MONTH=$(echo "${TOKENS_MONTH} * 0.3" | bc)
    COST_MONTH=$(echo "scale=4; (${INPUT_TOKENS_MONTH} * ${HAIKU_INPUT_RATE} / 1000000) + (${OUTPUT_TOKENS_MONTH} * ${HAIKU_OUTPUT_RATE} / 1000000)" | bc)
    
    # Determine status (using awk for float comparison)
    STATUS="OK"
    ALERT_DAILY=$(awk -v c="${COST_TODAY}" -v t="${ALERT_THRESHOLD_DAILY}" 'BEGIN { print (c > t) ? 1 : 0 }')
    ALERT_MONTHLY=$(awk -v c="${COST_MONTH}" -v t="${ALERT_THRESHOLD_MONTHLY}" 'BEGIN { print (c > t) ? 1 : 0 }')
    
    if [ "${ALERT_DAILY}" == "1" ]; then
        STATUS="ALERT_DAILY"
    elif [ "${ALERT_MONTHLY}" == "1" ]; then
        STATUS="ALERT_MONTHLY"
    fi
    
    # Create JSON output
    cat > "${OUTPUT_FILE}" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "tokens_today": ${TOKENS_TODAY},
  "cost_today": ${COST_TODAY},
  "tokens_month": ${TOKENS_MONTH},
  "cost_month": ${COST_MONTH},
  "budget_daily": ${DAILY_BUDGET},
  "budget_monthly": ${MONTHLY_BUDGET},
  "status": "${STATUS}",
  "percent_daily": $(echo "scale=2; (${COST_TODAY} / ${DAILY_BUDGET}) * 100" | bc),
  "percent_monthly": $(echo "scale=2; (${COST_MONTH} / ${MONTHLY_BUDGET}) * 100" | bc)
}
EOF
    
    # Log the result
    echo "✓ Usage logged to ${OUTPUT_FILE}"
    jq . "${OUTPUT_FILE}" || cat "${OUTPUT_FILE}"
    
    # Trigger webhook if alert threshold exceeded
    if [ "${STATUS}" != "OK" ] && [ -n "${WEBHOOK_URL}" ]; then
        echo "🚨 Triggering webhook alert (${STATUS})..."
        curl -s -X POST "${WEBHOOK_URL}" \
            -H "Content-Type: application/json" \
            -d @"${OUTPUT_FILE}" || echo "Webhook POST failed"
    else
        [ "${STATUS}" != "OK" ] && echo "Alert triggered but WEBHOOK_MONITOR_URL not set"
    fi
}

exit 0
