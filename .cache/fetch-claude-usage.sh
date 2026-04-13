#!/bin/bash
# Fetch Claude API usage from Anthropic console and log metrics
# Usage: ./fetch-claude-usage.sh

set -e

CACHE_FILE="${HOME}/.openclaw/workspace/.cache/claude-usage.json"
WEBHOOK_URL="${WEBHOOK_MONITOR_URL:-}"

# Budget thresholds (in USD)
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00
DAILY_ALERT_THRESHOLD=3.75  # 75% of daily
MONTHLY_ALERT_THRESHOLD=116.25  # 75% of monthly

# Pricing rates (per 1M tokens)
INPUT_RATE=0.4
OUTPUT_RATE=1.2

# Timestamps
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TODAY=$(date +"%Y-%m-%d")
MONTH=$(date +"%Y-%m")

# ============================================================================
# METHOD 1: Try to use Anthropic API if available
# ============================================================================
if [ -n "$ANTHROPIC_API_KEY" ]; then
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Attempting to fetch usage via Anthropic API..."
  
  # Note: As of 2026, Anthropic may not have a public usage API endpoint.
  # This is a placeholder for when such an endpoint becomes available.
  # Check: https://docs.anthropic.com for updates.
  
  # Example (when API endpoint exists):
  # USAGE_DATA=$(curl -s "https://api.anthropic.com/v1/usage" \
  #   -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  #   -H "Content-Type: application/json")
  
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  Anthropic API usage endpoint not yet available."
fi

# ============================================================================
# METHOD 2: Browser automation (requires authenticated session)
# ============================================================================
# This would require:
# 1. Storing Anthropic session cookies
# 2. Using browser automation to visit console.anthropic.com/account/usage
# 3. Parsing the rendered usage data
# 4. Extracting input/output token counts

# ============================================================================
# METHOD 3: Manual export (most reliable for now)
# ============================================================================
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 📋 Manual usage export instructions:"
echo "  1. Visit: https://console.anthropic.com/account/usage"
echo "  2. Note your usage for today and this month"
echo "  3. Or: Download usage CSV from the console"
echo "  4. Update ~/.openclaw/workspace/.cache/claude-usage.json manually"

# ============================================================================
# Fallback: Load from environment or previous cache
# ============================================================================
if [ -f "$CACHE_FILE" ]; then
  PREV_STATUS=$(jq -r '.status' "$CACHE_FILE" 2>/dev/null || echo "unknown")
  if [ "$PREV_STATUS" != "awaiting_authentication" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Using cached data from last run..."
    cat "$CACHE_FILE"
    exit 0
  fi
fi

# ============================================================================
# Log placeholder until authentication is set up
# ============================================================================
cat > "$CACHE_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "tokens_today": 0,
  "cost_today": 0.0,
  "tokens_month": 0,
  "cost_month": 0.0,
  "budget_daily": $DAILY_BUDGET,
  "budget_monthly": $MONTHLY_BUDGET,
  "status": "awaiting_authentication",
  "note": "Anthropic console requires login. To automate: 1) Await Anthropic API usage endpoint, 2) Set up browser session caching, or 3) Export CSV monthly.",
  "last_check": "$TIMESTAMP"
}
EOF

echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  Usage logging initialized but requires authentication."
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Cache: $CACHE_FILE"

exit 0
