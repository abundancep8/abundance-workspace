#!/bin/bash
# YouTube Comment Monitor - Deployment Script
# Sets up the monitor for production use

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE="${HOME}/.openclaw/workspace"
CACHE_DIR="${WORKSPACE}/.cache"
LOG_DIR="${CACHE_DIR}/logs"

echo "🚀 YouTube Comment Monitor - Deployment"
echo "========================================"
echo ""

# Check Python
echo "✓ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "  Using: $PYTHON_VERSION"
echo ""

# Create directories
echo "✓ Creating directories..."
mkdir -p "$LOG_DIR"
mkdir -p "${CACHE_DIR}/comments"
chmod 700 "$LOG_DIR"
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
cd "$SCRIPT_DIR"
if pip3 install -r requirements.txt --quiet; then
    echo "  Dependencies installed"
else
    echo "⚠️  Some dependencies may have failed to install"
fi
echo ""

# Check config
echo "✓ Checking configuration..."
CONFIG_FILE="${CACHE_DIR}/youtube-monitor-config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "  ✓ Config file found"
    # Validate JSON
    if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
        echo "  ✓ Config is valid JSON"
    else
        echo "  ❌ Config file is invalid JSON"
        exit 1
    fi
else
    echo "  ⚠️  Config file not found at $CONFIG_FILE"
    echo "     Creating template..."
    cat > "$CONFIG_FILE" << 'EOF'
{
  "channel": {
    "name": "Concessa Obvius",
    "username": "@ConcessaObvius",
    "check_interval_minutes": 30
  },
  "categories": {
    "1_questions": {
      "name": "Questions",
      "keywords": ["how", "what", "where", "when", "cost", "price"]
    },
    "2_praise": {
      "name": "Praise",
      "keywords": ["amazing", "awesome", "great", "love", "thank"]
    },
    "3_spam": {
      "name": "Spam",
      "keywords": ["crypto", "bitcoin", "mlm", "click here", "earn money"]
    },
    "4_sales": {
      "name": "Sales",
      "keywords": ["partnership", "collaboration", "sponsor", "deal"]
    }
  }
}
EOF
    echo "  ✓ Template created"
fi
echo ""

# Check credentials
echo "✓ Checking YouTube API credentials..."
CREDS_FILE="${CACHE_DIR}/youtube-credentials.json"
if [ -f "$CREDS_FILE" ]; then
    echo "  ✓ Credentials file found"
else
    echo "  ⚠️  Credentials file not found at $CREDS_FILE"
    echo "     You need to set up YouTube API authentication:"
    echo "     1. Go to https://console.cloud.google.com"
    echo "     2. Create OAuth 2.0 credentials"
    echo "     3. Download JSON and place at $CREDS_FILE"
    echo "     OR set YOUTUBE_API_KEY environment variable"
fi
echo ""

# Test import
echo "✓ Testing module import..."
if python3 -c "import youtube_comment_monitor; print('  ✓ Module imports successfully')" 2>/dev/null; then
    true
else
    echo "  ❌ Module import failed"
    exit 1
fi
echo ""

# Run tests
echo "✓ Running tests..."
if python3 test_monitor.py > /tmp/monitor_test.log 2>&1; then
    echo "  ✓ All tests passed"
else
    echo "  ⚠️  Some tests failed (see /tmp/monitor_test.log)"
fi
echo ""

# Setup cron
echo "✓ Setting up cron job..."
CRON_CMD="*/30 * * * * cd ${CACHE_DIR} && python3 -m youtube_comment_monitor.run --workspace ${WORKSPACE} >> ${LOG_DIR}/youtube-monitor-cron.log 2>&1"

# Check if already in crontab
if (crontab -l 2>/dev/null | grep -q "youtube_comment_monitor.run"); then
    echo "  ✓ Cron job already scheduled"
else
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "  ✓ Cron job scheduled (every 30 minutes)"
fi
echo ""

# Summary
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "📍 Key Files:"
echo "  • Module: ${SCRIPT_DIR}"
echo "  • Config: ${CONFIG_FILE}"
echo "  • Logs: ${LOG_DIR}"
echo "  • Data: ${CACHE_DIR}/youtube-comments.jsonl"
echo "  • State: ${CACHE_DIR}/.youtube-monitor-state.json"
echo ""
echo "🧪 Test:"
echo "  python3 ${SCRIPT_DIR}/test_monitor.py"
echo ""
echo "🚀 Manual Run:"
echo "  python3 ${SCRIPT_DIR}/run.py --workspace ${WORKSPACE}"
echo ""
echo "📊 View Logs:"
echo "  tail -f ${LOG_DIR}/youtube-monitor-\$(date +%Y%m%d).log"
echo ""
echo "✨ Setup complete! Monitor will run automatically every 30 minutes."
echo ""
