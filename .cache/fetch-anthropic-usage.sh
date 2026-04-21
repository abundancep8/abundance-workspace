#!/bin/bash

##
# Fetch Claude API usage from Anthropic console and update monitor
#
# This script:
# 1. Opens the Anthropic dashboard
# 2. Extracts usage data (requires manual parsing OR browser automation)
# 3. Feeds data to claude-usage-monitor.js
#
# Setup:
#  - Get your Anthropic API key at: https://console.anthropic.com/account/keys
#  - View usage at: https://console.anthropic.com/account/usage
#
# Manual mode:
#  ./fetch-anthropic-usage.sh --input-today 1000 --output-today 5000 --input-month 50000 --output-month 250000
#
##

set -euo pipefail

WORKSPACE="${WORKSPACE:-.}"
CACHE_DIR="$WORKSPACE/.cache"
MONITOR="$CACHE_DIR/claude-usage-monitor.js"

# Parse arguments
INPUT_TODAY=0
OUTPUT_TODAY=0
INPUT_MONTH=0
OUTPUT_MONTH=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --input-today)
      INPUT_TODAY="$2"
      shift 2
      ;;
    --output-today)
      OUTPUT_TODAY="$2"
      shift 2
      ;;
    --input-month)
      INPUT_MONTH="$2"
      shift 2
      ;;
    --output-month)
      OUTPUT_MONTH="$2"
      shift 2
      ;;
    --auto)
      # Auto-fetch mode (requires browser or API key)
      ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
      if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "Error: --auto mode requires ANTHROPIC_API_KEY environment variable"
        exit 1
      fi
      echo "Auto-fetch not yet implemented. Please use manual mode with token counts."
      exit 1
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate input
if [ "$INPUT_TODAY" -eq 0 ] && [ "$OUTPUT_TODAY" -eq 0 ] && [ "$INPUT_MONTH" -eq 0 ] && [ "$OUTPUT_MONTH" -eq 0 ]; then
  echo "Usage:"
  echo "  $0 --input-today N --output-today N --input-month N --output-month N"
  echo ""
  echo "Example:"
  echo "  $0 --input-today 125000 --output-today 45000 --input-month 500000 --output-month 200000"
  echo ""
  echo "To find your usage:"
  echo "  1. Visit: https://console.anthropic.com/account/usage"
  echo "  2. Look for 'Today' and 'This Month' sections"
  echo "  3. Note input & output token counts"
  exit 1
fi

# Run monitor with data
node "$MONITOR" \
  --today-input "$INPUT_TODAY" \
  --today-output "$OUTPUT_TODAY" \
  --month-input "$INPUT_MONTH" \
  --month-output "$OUTPUT_MONTH"

echo "✓ Usage updated"
