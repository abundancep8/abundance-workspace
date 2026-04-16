#!/bin/bash
# Setup Claude API Usage Monitoring Cron Job
# Runs fetch-claude-usage-cron.py hourly and manages webhook alerts

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
SCRIPT_PATH="$CACHE_DIR/fetch-claude-usage-enhanced.py"
LOG_FILE="$CACHE_DIR/claude-usage-cron.log"

# Create cron entry identifier
CRON_COMMENT="fetch-claude-api-usage"

# Ensure script is executable
chmod +x "$SCRIPT_PATH"

# Function to install cron job
install_cron() {
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$CRON_COMMENT"; then
        echo "✓ Cron job already installed"
        return 0
    fi
    
    # Create temporary cron file
    TEMP_CRON=$(mktemp)
    
    # Copy existing crontab
    crontab -l 2>/dev/null > "$TEMP_CRON" || true
    
    # Add new job (runs hourly)
    echo "0 * * * * cd $WORKSPACE && python3 $SCRIPT_PATH >> $LOG_FILE 2>&1 # $CRON_COMMENT" >> "$TEMP_CRON"
    
    # Install new crontab
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"
    
    echo "✓ Cron job installed (hourly)"
}

# Function to uninstall cron job
uninstall_cron() {
    if ! crontab -l 2>/dev/null | grep -q "$CRON_COMMENT"; then
        echo "✓ Cron job not installed"
        return 0
    fi
    
    TEMP_CRON=$(mktemp)
    crontab -l 2>/dev/null | grep -v "$CRON_COMMENT" > "$TEMP_CRON"
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"
    
    echo "✓ Cron job removed"
}

# Function to run immediately
run_now() {
    echo "Running fetch-claude-usage..."
    python3 "$SCRIPT_PATH"
}

# Function to view logs
view_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo "No logs yet"
        return
    fi
    tail -20 "$LOG_FILE"
}

# Function to test webhook
test_webhook() {
    WEBHOOK_URL="${WEBHOOK_MONITOR_URL:-}"
    if [ -z "$WEBHOOK_URL" ]; then
        echo "⚠️  WEBHOOK_MONITOR_URL not set"
        return 1
    fi
    
    TEST_DATA=$(cat <<EOF
{
  "alert_type": "claude_usage",
  "status": "TEST",
  "cost_today": 1.23,
  "cost_month": 45.67,
  "percent_daily": 24.6,
  "percent_monthly": 29.5,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
)
    
    echo "Testing webhook: $WEBHOOK_URL"
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA" \
        -w "\n" \
        -s
}

# Function to show status
show_status() {
    echo "=== Claude Usage Monitor ==="
    echo "Workspace: $WORKSPACE"
    echo "Script: $SCRIPT_PATH"
    echo "Usage file: $CACHE_DIR/claude-usage.json"
    echo ""
    
    if [ -f "$CACHE_DIR/claude-usage.json" ]; then
        echo "=== Current Usage ==="
        cat "$CACHE_DIR/claude-usage.json" | jq '{date, cost_today, cost_month, percent_daily, percent_monthly, status}'
    fi
    
    echo ""
    echo "=== Cron Status ==="
    if crontab -l 2>/dev/null | grep -q "$CRON_COMMENT"; then
        echo "✓ Cron job installed"
        echo "Schedule: Hourly (0 * * * *)"
    else
        echo "✗ Cron job not installed"
    fi
    
    echo ""
    echo "=== Webhook ==="
    if [ -n "$WEBHOOK_MONITOR_URL" ]; then
        echo "✓ Webhook configured: $WEBHOOK_MONITOR_URL"
    else
        echo "⚠️  Webhook not configured (WEBHOOK_MONITOR_URL)"
    fi
}

# Main
case "${1:-status}" in
    install)
        install_cron
        ;;
    uninstall)
        uninstall_cron
        ;;
    run)
        run_now
        ;;
    logs)
        view_logs
        ;;
    test-webhook)
        test_webhook
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {install|uninstall|run|logs|test-webhook|status}"
        exit 1
        ;;
esac
