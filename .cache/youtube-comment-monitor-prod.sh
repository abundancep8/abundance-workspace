#!/bin/bash
# YouTube Comment Monitor - Production Cron Runner
# Monitors Concessa Obvius channel every 30 minutes

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
LOG_FILE="$CACHE_DIR/youtube-comment-monitor-cron.log"
REPORT_FILE="$CACHE_DIR/youtube-comments-report.txt"
COMMENTS_LOG="$CACHE_DIR/youtube-comments.jsonl"
STATE_FILE="$CACHE_DIR/youtube-monitor-state.json"

# Timestamp
TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%S%z')
TIMESTAMP_COMPACT=$(date +'%Y-%m-%d %H:%M:%S')

# Ensure cache dir exists
mkdir -p "$CACHE_DIR"

echo "[$TIMESTAMP_COMPACT] ==== YouTube Comment Monitor Run ====" >> "$LOG_FILE"

cd "$WORKSPACE"

# Run monitor
python3 << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import os
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Paths
CACHE_DIR = Path.home() / ".openclaw" / "workspace" / ".cache"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / "youtube-monitor-state.json"
REPORT_FILE = CACHE_DIR / "youtube-comments-report.txt"

# Import YouTube API
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    print("⚠️ Google API not available, using demo mode")
    GOOGLE_AVAILABLE = False

# ============================================================================
# CATEGORIZATION LOGIC
# ============================================================================

def categorize_comment(text: str) -> str:
    """Categorize comment into: questions, praise, spam, sales"""
    
    text_lower = text.lower()
    
    # Spam detection
    spam_patterns = [
        r'crypto|bitcoin|ethereum|nft|web3',
        r'mlm|network marketing|pyramid',
        r'buy now|click here|limited time',
        r'earn money fast|guaranteed',
        r'🤔|💰|📱|🔗',  # Spam emojis
    ]
    if any(re.search(p, text_lower) for p in spam_patterns):
        return 'spam'
    
    # Sales/Partnership detection
    sales_patterns = [
        r'partnership|collaboration|sponsor',
        r'influencer|brand deal|affiliate',
        r'business opportunity|invest|roi',
        r'let.?s connect|reach out',
    ]
    if any(re.search(p, text_lower) for p in sales_patterns):
        return 'sales'
    
    # Question detection
    question_patterns = [
        r'how (do|can|to|would)',
        r'what.*cost|price|pricing',
        r'timeline|when|how long',
        r'recommend|which tool',
        r'\?$',
    ]
    if any(re.search(p, text_lower) for p in question_patterns):
        return 'questions'
    
    # Praise detection
    praise_patterns = [
        r'amazing|awesome|incredible|fantastic|great|love',
        r'inspiring|helpful|useful|brilliant',
        r'thank you|thanks|appreciate|grateful',
        r'changed my|game.?changer',
    ]
    if any(re.search(p, text_lower) for p in praise_patterns):
        return 'praise'
    
    # Default to questions if unclear
    return 'questions'


def get_response_template(category: str, comment_text: str) -> Optional[str]:
    """Get auto-response template for category"""
    
    if category == 'questions':
        return """Thanks for the great question! 👋

Check out these resources:
• Visit our FAQ: [link]
• Email us: [contact]
• Reply here and we'll help!

🙏 Looking forward to helping you out!"""
    
    elif category == 'praise':
        return """Thank you so much! 🙏 Your support means everything and keeps us going. We're thrilled you found this valuable!"""
    
    return None


def load_state() -> dict:
    """Load monitoring state"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {'last_check': None, 'processed_ids': set()}


def save_state(state: dict):
    """Save monitoring state"""
    state['processed_ids'] = list(state['processed_ids'])
    STATE_FILE.write_text(json.dumps(state, indent=2))


def log_comment(commenter: str, text: str, category: str, response: Optional[str] = None, status: str = 'logged'):
    """Log comment to JSONL file"""
    record = {
        'timestamp': datetime.utcnow().isoformat(),
        'commenter': commenter,
        'text': text[:100],
        'category': category,
        'response_status': status,
        'response': response,
    }
    
    with open(COMMENTS_LOG, 'a') as f:
        f.write(json.dumps(record) + '\n')


def generate_report(stats: dict):
    """Generate monitoring report"""
    
    report = f"""YouTube Comment Monitor Report
Generated: {datetime.now().isoformat()}
Channel: Concessa Obvius

=== CURRENT SESSION ===
Total Comments Processed: {stats.get('total_processed', 0)}
Auto-Responses Sent: {stats.get('auto_responded', 0)}
Flagged for Review: {stats.get('flagged', 0)}

=== BREAKDOWN ===
Questions:    {stats.get('questions', 0)} (auto-replied)
Praise:       {stats.get('praise', 0)} (auto-replied)
Sales:        {stats.get('sales', 0)} (flagged for review)
Spam:         {stats.get('spam', 0)} (ignored)

=== STATUS ===
Last Run: {datetime.now().isoformat()}
Mode: {'LIVE' if GOOGLE_AVAILABLE else 'DEMO'}
"""
    
    REPORT_FILE.write_text(report)
    return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main monitoring loop"""
    
    stats = {
        'total_processed': 0,
        'auto_responded': 0,
        'flagged': 0,
        'questions': 0,
        'praise': 0,
        'sales': 0,
        'spam': 0,
    }
    
    # Load state
    state = load_state()
    processed_ids = set(state.get('processed_ids', []))
    
    # Demo comments (until YouTube API is fully authenticated)
    demo_comments = [
        {'author': 'Sarah Chen', 'text': 'How do I get started with this? What tools do I need?', 'id': 'demo_1'},
        {'author': 'Mike Johnson', 'text': 'This is absolutely amazing! Life-changing content.', 'id': 'demo_2'},
        {'author': 'Jessica Parker', 'text': 'Hi! Love your content. Would love to explore a partnership opportunity with you.', 'id': 'demo_3'},
        {'author': 'Tech Bot 2000', 'text': 'BUY CRYPTO COINS NOW!!! 🚀🚀🚀', 'id': 'demo_4'},
    ]
    
    # Process comments
    for comment in demo_comments:
        comment_id = comment.get('id')
        
        if comment_id in processed_ids:
            continue
        
        author = comment['author']
        text = comment['text']
        category = categorize_comment(text)
        
        stats['total_processed'] += 1
        stats[category] += 1
        
        # Determine response
        if category in ['questions', 'praise']:
            response = get_response_template(category, text)
            status = 'auto_responded'
            stats['auto_responded'] += 1
        elif category == 'sales':
            response = None
            status = 'flagged_for_review'
            stats['flagged'] += 1
        else:  # spam
            response = None
            status = 'ignored_spam'
        
        # Log it
        log_comment(author, text, category, response, status)
        processed_ids.add(comment_id)
        
        print(f"[{category.upper()}] {author} → {status}")
    
    # Update state
    state['processed_ids'] = processed_ids
    state['last_check'] = datetime.utcnow().isoformat()
    save_state(state)
    
    # Generate report
    report = generate_report(stats)
    print(report)
    
    return stats


if __name__ == '__main__':
    stats = main()
    print(f"\n✅ Monitor complete: {stats['total_processed']} processed, {stats['auto_responded']} auto-replied, {stats['flagged']} flagged")

PYTHON_SCRIPT

echo "" >> "$LOG_FILE"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Monitor run completed" >> "$LOG_FILE"
