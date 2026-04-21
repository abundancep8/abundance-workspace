#!/bin/bash
# Quick monitor for Claude API usage
# Shows current usage, costs, and alerts

USAGE_FILE=~/.openclaw/workspace/.cache/claude-usage.json
CONSOLE_URL="https://console.anthropic.com/account/usage"

if [ ! -f "$USAGE_FILE" ]; then
  echo "❌ No usage data found. Run fetch-claude-usage.py first."
  exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Claude API Usage Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v jq &> /dev/null; then
  # Pretty print with jq
  status=$(jq -r '.status' "$USAGE_FILE")
  date=$(jq -r '.date' "$USAGE_FILE")
  tokens_in=$(jq -r '.tokens_today' "$USAGE_FILE")
  tokens_out=$(jq -r '.tokens_output_today' "$USAGE_FILE")
  cost_today=$(jq -r '.cost_today' "$USAGE_FILE")
  cost_month=$(jq -r '.cost_month' "$USAGE_FILE")
  budget_daily=$(jq -r '.budget_daily' "$USAGE_FILE")
  budget_monthly=$(jq -r '.budget_monthly' "$USAGE_FILE")
  daily_percent=$(jq -r '.daily_percent' "$USAGE_FILE")
  monthly_percent=$(jq -r '.monthly_percent' "$USAGE_FILE")
  alert=$(jq -r '.alert_triggered' "$USAGE_FILE")
  timestamp=$(jq -r '.timestamp' "$USAGE_FILE")
else
  # Fallback: raw cat
  cat "$USAGE_FILE"
  exit 0
fi

echo "📅 Date: $date"
echo "🕒 Updated: $timestamp"
echo ""

echo "💰 Daily Budget"
printf "   Cost: \$%-6.2f / \$%.2f " "$cost_today" "$budget_daily"
if (( $(echo "$daily_percent > 75" | bc -l) )); then
  echo "⚠️  ($daily_percent%)"
else
  echo "✅ ($daily_percent%)"
fi

echo ""
echo "📈 Monthly Budget"
printf "   Cost: \$%-6.2f / \$%.2f " "$cost_month" "$budget_monthly"
if (( $(echo "$monthly_percent > 75" | bc -l) )); then
  echo "⚠️  ($monthly_percent%)"
else
  echo "✅ ($monthly_percent%)"
fi

echo ""
echo "🧮 Token Usage"
echo "   Input:  $tokens_in tokens"
echo "   Output: $tokens_out tokens"
echo "   Total:  $((tokens_in + tokens_out)) tokens"

echo ""
if [ "$alert" = "true" ]; then
  echo "🚨 STATUS: $status"
else
  echo "✅ STATUS: $status"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 Note: This shows estimated costs from OpenClaw logs."
echo "         For official usage: $CONSOLE_URL"
echo ""
