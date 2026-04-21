#!/usr/bin/env python3
"""
YouTube Comment Monitor - TEST VERSION with Mock Data
Demonstrates full functionality: categorization, auto-responses, logging
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
import re

# Configuration
WORKSPACE = Path.home() / ".openclaw/workspace"
CACHE_DIR = WORKSPACE / ".cache"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
PROCESSED_IDS = CACHE_DIR / "youtube-comments-processed.json"
STATE_FILE = CACHE_DIR / ".youtube-monitor-state.json"

CHANNEL_ID = "UCa_mZVVqV5Aq48a0MnIjS-w"
CHANNEL_NAME = "Concessa Obvius"

# Template responses
TEMPLATES = {
    "questions": "Thanks for the question! Check our FAQ or reach out to support@concessa.com for detailed help.",
    "praise": "Thank you so much! We really appreciate your support 🙏"
}

# Categorization keywords
KEYWORDS = {
    "questions": {
        "how": r'\bhow\b',
        "what": r'\bwhat\b',
        "why": r'\bwhy\b',
        "start": r'\bstart|begin|get started\b',
        "tools": r'\btools|software|platform\b',
        "cost": r'\bcost|price|fee\b',
        "timeline": r'\btimeline|how long\b',
        "question_mark": r'\?$'
    },
    "praise": {
        "amazing": r'\bamazing\b',
        "awesome": r'\bawesome\b',
        "inspiring": r'\binspiring\b',
        "great": r'\bgreat\b',
        "love": r'\blove\b',
        "thank": r'\bthank\b',
        "appreciate": r'\bappreciate\b'
    },
    "spam": {
        "crypto": r'\bcrypto|bitcoin\b',
        "mlm": r'\bmlm|pyramid\b',
        "suspicious": r'(?:http|https|www)\.',
        "spam_phrase": r'\bfollow my|check my\b'
    },
    "sales": {
        "partnership": r'\bpartnership|collab\b',
        "business": r'\bbusiness proposal\b',
        "sponsor": r'\bsponsor\b',
        "contact": r'\bcontact me|dm me\b'
    }
}

# Mock comments for testing
MOCK_COMMENTS = [
    {
        'comment_id': 'test_q1',
        'video_id': 'demoVid1',
        'author': 'Sarah Chen',
        'text': 'How do I get started building automation systems? What tools do I need?',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 5
    },
    {
        'comment_id': 'test_q2',
        'video_id': 'demoVid2',
        'author': 'Marcus Johnson',
        'text': 'What\'s the timeline to set up something like this? How much does it cost?',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 3
    },
    {
        'comment_id': 'test_p1',
        'video_id': 'demoVid3',
        'author': 'Emma Watson',
        'text': 'This is absolutely amazing! So inspiring and brilliant work 🙌',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 42
    },
    {
        'comment_id': 'test_p2',
        'video_id': 'demoVid1',
        'author': 'David Park',
        'text': 'Thank you so much for sharing! I really appreciate the detailed explanation.',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 18
    },
    {
        'comment_id': 'test_spam1',
        'video_id': 'demoVid2',
        'author': 'CryptoGuy88',
        'text': 'Great video bro! Check out my crypto trading system: https://scam-site.fake',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 0
    },
    {
        'comment_id': 'test_spam2',
        'video_id': 'demoVid3',
        'author': 'MLMQueen',
        'text': 'Follow my channel for MLM pyramid schemes and network marketing tips!',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 0
    },
    {
        'comment_id': 'test_sales1',
        'video_id': 'demoVid1',
        'author': 'BusinessGuy',
        'text': 'Love your work! We\'re looking for a partnership/collaboration. DM me?',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 2
    },
    {
        'comment_id': 'test_sales2',
        'video_id': 'demoVid2',
        'author': 'SalesRep',
        'text': 'Interested in sponsoring your videos? Contact me for a business proposal.',
        'timestamp': datetime.utcnow().isoformat(),
        'likes': 1
    },
]


def categorize_comment(text: str) -> Tuple[int, str, float]:
    """Categorize comment"""
    text_lower = text.lower()
    scores = defaultdict(int)
    
    for category_name, keywords in KEYWORDS.items():
        for keyword, pattern in keywords.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                scores[category_name] += 1
    
    if scores['spam'] > 0:
        return (3, 'spam', 0.8)
    elif scores['sales'] > 1:
        return (4, 'sales', 0.85)
    elif scores['questions'] > 0:
        return (1, 'questions', 0.75)
    elif scores['praise'] > 1:
        return (2, 'praise', 0.8)
    else:
        return (2, 'praise', 0.3)


def log_comment(comment: Dict, category: int, label: str, response_status: str, response_text: str = ""):
    """Log comment to JSONL"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'comment_id': comment['comment_id'],
        'video_id': comment['video_id'],
        'author': comment['author'],
        'text': comment['text'][:200],
        'category': category,
        'category_label': label,
        'response_status': response_status,
        'response_text': response_text if response_text else None
    }
    
    with open(COMMENTS_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def load_processed_ids() -> set:
    """Load processed comment IDs"""
    if PROCESSED_IDS.exists():
        try:
            with open(PROCESSED_IDS) as f:
                return set(json.load(f).get('processed', []))
        except:
            pass
    return set()


def save_processed_ids(ids: set):
    """Save processed IDs"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_IDS, 'w') as f:
        json.dump({'processed': list(ids), 'updated': datetime.utcnow().isoformat()}, f)


def save_state(stats: Dict):
    """Save monitoring state"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    state = {
        'last_run': datetime.utcnow().isoformat(),
        'channel': CHANNEL_NAME,
        'channel_id': CHANNEL_ID,
        'status': 'operational',
        **stats
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def main():
    """Run with mock data"""
    
    print("\n" + "="*60)
    print("📺 YouTube Comment Monitor - TEST VERSION")
    print("   (Using mock data for demonstration)")
    print("="*60)
    
    # Load previous state
    processed_ids = load_processed_ids()
    print(f"\n📝 Previously processed: {len(processed_ids)} comment IDs")
    
    # Filter to new comments only
    new_comments = [c for c in MOCK_COMMENTS if c['comment_id'] not in processed_ids]
    total_new = len(new_comments)
    
    print(f"📹 Mock videos: 3")
    print(f"💬 New comments found: {total_new}")
    
    if total_new == 0:
        print("\n✨ All comments already processed")
        return 0
    
    # Initialize stats
    stats = {
        'videos_checked': 3,
        'total_comments': total_new,
        'auto_responded': 0,
        'flagged_for_review': 0,
        'spam_filtered': 0,
        'by_category': {
            '1_questions': 0,
            '2_praise': 0,
            '3_spam': 0,
            '4_sales': 0
        }
    }
    
    # Process each comment
    print("\n🏷️  Categorizing and processing comments...")
    
    for comment in new_comments:
        category, label, confidence = categorize_comment(comment['text'])
        cat_key = f'{category}_{label}'
        if cat_key in stats['by_category']:
            stats['by_category'][cat_key] += 1
        
        response_status = "no_response"
        response_text = ""
        
        if category == 1:  # Questions
            response_text = TEMPLATES['questions']
            response_status = "auto_responded"
            stats['auto_responded'] += 1
            print(f"  ✅ Q&A: {comment['author']}... → auto-reply sent")
        
        elif category == 2:  # Praise
            response_text = TEMPLATES['praise']
            response_status = "auto_responded"
            stats['auto_responded'] += 1
            print(f"  👏 Praise: {comment['author']}... → thank you sent")
        
        elif category == 3:  # Spam
            response_status = "spam_filtered"
            stats['spam_filtered'] += 1
            print(f"  🚫 Spam: {comment['author']}... → filtered")
        
        elif category == 4:  # Sales
            response_status = "flagged_review"
            stats['flagged_for_review'] += 1
            print(f"  🚩 Sales: {comment['author']}... → flagged for manual review")
        
        # Log the comment
        log_comment(comment, category, label, response_status, response_text)
        processed_ids.add(comment['comment_id'])
    
    # Save state
    save_processed_ids(processed_ids)
    save_state(stats)
    
    # Print summary report
    print("\n" + "="*60)
    print("📊 SUMMARY REPORT")
    print("="*60)
    print(f"Channel:                {CHANNEL_NAME}")
    print(f"Videos checked:         {stats['videos_checked']}")
    print(f"Total new comments:     {stats['total_comments']}")
    print(f"\nComment Breakdown:")
    print(f"  ❓ Questions (Cat 1):  {stats['by_category'].get('1_questions', 0)}")
    print(f"  👏 Praise (Cat 2):     {stats['by_category'].get('2_praise', 0)}")
    print(f"  🚫 Spam (Cat 3):       {stats['by_category'].get('3_spam', 0)}")
    print(f"  💼 Sales (Cat 4):      {stats['by_category'].get('4_sales', 0)}")
    print(f"\nActions Taken:")
    print(f"  ✅ Auto-responses sent: {stats['auto_responded']}")
    print(f"  🚩 Flagged for review:  {stats['flagged_for_review']}")
    print(f"  🚫 Spam filtered:       {stats['spam_filtered']}")
    print(f"\nProcessing State:")
    print(f"  Total processed IDs:   {len(processed_ids)}")
    print(f"  Log file:              {COMMENTS_LOG}")
    print(f"  State file:            {STATE_FILE}")
    print("="*60)
    
    # Show log entries
    print("\n📋 Logged Comments (last 8):")
    print("-" * 60)
    
    if COMMENTS_LOG.exists():
        with open(COMMENTS_LOG) as f:
            lines = f.readlines()
            for line in lines[-8:]:
                entry = json.loads(line)
                cat_emoji = {1: '❓', 2: '👏', 3: '🚫', 4: '💼'}[entry['category']]
                status_emoji = {
                    'auto_responded': '✅',
                    'flagged_review': '🚩',
                    'spam_filtered': '🚫',
                    'no_response': '⏭️'
                }.get(entry['response_status'], '•')
                print(f"{cat_emoji} {status_emoji} {entry['author'][:20]:20} | {entry['text'][:40]}")
    
    print("-" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
