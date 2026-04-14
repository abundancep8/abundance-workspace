#!/bin/bash
# update-usage-manual.sh - Manually update Claude API usage from console
# 
# Instructions:
# 1. Visit: https://console.anthropic.com/account/usage
# 2. Run this script and enter the usage values when prompted
# 3. Or: pass values as environment variables
#
# Usage:
#   ./update-usage-manual.sh
#   # or
#   INPUT_TODAY=123456 OUTPUT_TODAY=789012 INPUT_MONTH=1234567 OUTPUT_MONTH=7890123 ./update-usage-manual.sh

set -e

WORKSPACE="${1:-.}"
CACHE_DIR="$WORKSPACE/.cache"
mkdir -p "$CACHE_DIR"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Claude API Usage Monitor - Manual Update${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Pricing
INPUT_RATE=0.4      # per 1M tokens
OUTPUT_RATE=1.2     # per 1M tokens

# Budgets
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00

# Try to get values from environment or prompt
if [ -z "$INPUT_TODAY" ]; then
  echo -e "${YELLOW}📊 Please visit: https://console.anthropic.com/account/usage${NC}"
  echo ""
  read -p "Input tokens TODAY: " INPUT_TODAY
  INPUT_TODAY=${INPUT_TODAY:-0}
fi

if [ -z "$OUTPUT_TODAY" ]; then
  read -p "Output tokens TODAY: " OUTPUT_TODAY
  OUTPUT_TODAY=${OUTPUT_TODAY:-0}
fi

if [ -z "$INPUT_MONTH" ]; then
  read -p "Input tokens THIS MONTH: " INPUT_MONTH
  INPUT_MONTH=${INPUT_MONTH:-0}
fi

if [ -z "$OUTPUT_MONTH" ]; then
  read -p "Output tokens THIS MONTH: " OUTPUT_MONTH
  OUTPUT_MONTH=${OUTPUT_MONTH:-0}
fi

# Validate inputs are numbers
for var in INPUT_TODAY OUTPUT_TODAY INPUT_MONTH OUTPUT_MONTH; do
  val=${!var}
  if ! [[ "$val" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}❌ Invalid input: $var=$val (must be a number)${NC}"
    exit 1
  fi
done

# Calculate totals and costs
TOKENS_TODAY=$((INPUT_TODAY + OUTPUT_TODAY))
TOKENS_MONTH=$((INPUT_MONTH + OUTPUT_MONTH))

COST_TODAY=$(awk "BEGIN {printf \"%.4f\", ($INPUT_TODAY * $INPUT_RATE + $OUTPUT_TODAY * $OUTPUT_RATE) / 1000000}")
COST_MONTH=$(awk "BEGIN {printf \"%.4f\", ($INPUT_MONTH * $INPUT_RATE + $OUTPUT_MONTH * $OUTPUT_RATE) / 1000000}")

DAILY_LIMIT=$(awk "BEGIN {printf \"%.2f\", $DAILY_BUDGET * 0.75}")
MONTHLY_LIMIT=$(awk "BEGIN {printf \"%.2f\", $MONTHLY_BUDGET * 0.75}")

# Status
STATUS="ok"
DAILY_EXCEEDED=0
MONTHLY_EXCEEDED=0

if (( $(echo "$COST_TODAY > $DAILY_LIMIT" | bc -l) )); then
  STATUS="warning"
  DAILY_EXCEEDED=1
fi

if (( $(echo "$COST_MONTH > $MONTHLY_LIMIT" | bc -l) )); then
  STATUS="warning"
  MONTHLY_EXCEEDED=1
fi

# Log data
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

LOG_DATA=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "tokens_today": $TOKENS_TODAY,
  "tokens_today_breakdown": {
    "input": $INPUT_TODAY,
    "output": $OUTPUT_TODAY
  },
  "cost_today": "$COST_TODAY",
  "cost_today_usd": $COST_TODAY,
  "tokens_month": $TOKENS_MONTH,
  "tokens_month_breakdown": {
    "input": $INPUT_MONTH,
    "output": $OUTPUT_MONTH
  },
  "cost_month": "$COST_MONTH",
  "cost_month_usd": $COST_MONTH,
  "budget_daily": "$DAILY_BUDGET",
  "budget_daily_usd": $DAILY_BUDGET,
  "budget_monthly": "$MONTHLY_BUDGET",
  "budget_monthly_usd": $MONTHLY_BUDGET,
  "daily_limit_75pct": "$DAILY_LIMIT",
  "monthly_limit_75pct": "$MONTHLY_LIMIT",
  "daily_exceeded": $DAILY_EXCEEDED,
  "monthly_exceeded": $MONTHLY_EXCEEDED,
  "status": "$STATUS"
}
EOF
)

echo "$LOG_DATA" | jq . > "$CACHE_DIR/claude-usage.json" 2>/dev/null || echo "$LOG_DATA" > "$CACHE_DIR/claude-usage.json"

# Display summary
echo ""
echo -e "${GREEN}✅ Usage updated!${NC}"
echo ""
echo "📈 TODAY:"
echo "  Input:  $INPUT_TODAY tokens"
echo "  Output: $OUTPUT_TODAY tokens"
echo "  Total:  $TOKENS_TODAY tokens"
echo -e "  Cost:   ${GREEN}\$$COST_TODAY${NC} / \$$DAILY_BUDGET daily budget"
echo ""
echo "📊 THIS MONTH:"
echo "  Input:  $INPUT_MONTH tokens"
echo "  Output: $OUTPUT_MONTH tokens"
echo "  Total:  $TOKENS_MONTH tokens"
echo -e "  Cost:   ${GREEN}\$$COST_MONTH${NC} / \$$MONTHLY_BUDGET monthly budget"
echo ""

if [ "$STATUS" = "warning" ]; then
  echo -e "${YELLOW}⚠️  WARNING: Budget threshold exceeded!${NC}"
  if [ "$DAILY_EXCEEDED" -eq 1 ]; then
    PCT=$(awk "BEGIN {printf \"%.0f\", ($COST_TODAY / $DAILY_BUDGET * 100)}")
    echo "  Daily: $PCT% of budget ($COST_TODAY > $DAILY_LIMIT)"
  fi
  if [ "$MONTHLY_EXCEEDED" -eq 1 ]; then
    PCT=$(awk "BEGIN {printf \"%.0f\", ($COST_MONTH / $MONTHLY_BUDGET * 100)}")
    echo "  Monthly: $PCT% of budget ($COST_MONTH > $MONTHLY_LIMIT)"
  fi
else
  echo -e "${GREEN}✅ Within budget${NC}"
fi

echo ""
echo -e "${BLUE}📝 Logged to:${NC} $CACHE_DIR/claude-usage.json"

exit 0
