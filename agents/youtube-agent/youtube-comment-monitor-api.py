#!/usr/bin/env python3
"""
YouTube Comment Monitor & Auto-Responder
Monitors Concessa Obvius channel, auto-responds to comments, logs everything.
Falls back to demo mode if OAuth authentication fails.
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CHANNEL_ID = "UC32674"  # Concessa Obvius
TOKEN_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-token.json'
LOG_FILE = Path('.cache/youtube-comments.jsonl')
STATE_FILE = Path('.cache/.youtube-monitor-state.json')
BATCH_SIZE = 100

# Comment response templates
RESPONSES = {
    "how_start": {
        "triggers": ["how do i start", "how to begin", "where do i start", "how should i begin"],
        "response": "Start with ONE task that costs you 30 min/day. Write a clear instruction for it. Test for 7 days. Track what changed. That's the starting point."
    },
    "how_long": {
        "triggers": ["how long", "how much time", "took you how long", "timeline"],
        "response": "Setup: 2 weeks. Testing: 2 weeks. First revenue: Week 3. Month 1: You'll understand the system. After that it compounds."
    },
    "what_tools": {
        "triggers": ["what tools", "which tools", "what do you use", "tech stack"],
        "response": "Claude (writing), Blotato (videos), Stripe (payments), Vercel (hosting), OpenClaw (orchestration). Total: $50/month. Revenue: $4,200+."
    },
    "what_cost": {
        "triggers": ["how much does it cost", "cost", "price", "expensive"],
        "response": "$50/month for the stack. ROI in first month. The tools are public. The system I built is what matters."
    },
    "amazing": {
        "triggers": ["amazing", "incredible", "brilliant", "genius", "awesome"],
        "response": "Wait until you build your own system. Then it gets exciting. Now go build instead of just watching."
    },
    "inspiring": {
        "triggers": ["inspiring", "inspired", "motivated", "thank you", "love", "grateful"],
        "response": "Action > inspiration every time. Start building today. That's what separates people."
    }
}

# Demo comments for fallback mode
DEMO_COMMENTS = [
    {"author": "Sarah Chen", "text": "How do I start automating my business? This is exactly what I needed."},
    {"author": "Marcus Johnson", "text": "This is absolutely amazing and inspiring! Can't wait to implement this."},
    {"author": "TechVenture Studios", "text": "Hi! We're interested in a partnership opportunity. Let's talk!"},
    {"author": "Alex Martinez", "text": "Brilliant work. Truly impressed by the execution here."},
    {"author": "Jordan Lee", "text": "What tools do you recommend for someone just starting out?"},
    {"author": "Emma Watson", "text": "How much does this cost to set up? Looks incredible!"},
    {"author": "CryptoMillionMaker", "text": "EARN $5000/DAY WITH CRYPTO!!! Click my link!!!"},
    {"author": "Dr. Patel", "text": "Timeline from idea to first $10k? How long did it take for you?"},
    {"author": "Designer_Dave", "text": "I'm motivated to start building now. Thank you for this!"},
    {"author": "Growth Agency Pro", "text": "Great content. We work with creators on partnerships. Available for collaboration."},
]

def get_youtube_service():
    """Load YouTube service with saved credentials. Returns None if auth fails."""
    if not TOKEN_FILE.exists():
        print("⚠️  Token file not found. Running in DEMO mode.")
        return None
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            creds_data = json.load(f)
        
        creds = Credentials.from_authorized_user_info(creds_data)
        
        # Refresh token if needed
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        
        return build('youtube', 'v3', credentials=creds)
    except Exception as e:
        print(f"⚠️  YouTube API auth failed: {e}")
        print("Falling back to DEMO mode")
        return None

def get_state():
    """Load tracking state"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {
        "last_run": None,
        "processed_comment_ids": [],
        "total_processed": 0
    }

def save_state(state):
    """Save tracking state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_recent_comments(youtube, max_results=20):
    """Fetch recent comments from channel"""
    if not youtube:
        return None
    
    try:
        request = youtube.commentThreads().list(
            part='snippet,replies',
            allThreadsRelatedToChannelId=CHANNEL_ID,
            maxResults=max_results,
            order='relevance',
            textFormat='plainText'
        )
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        print(f"❌ Error fetching comments: {e}")
        return None

def generate_demo_comments(count=3):
    """Generate synthetic comments for demo mode"""
    state = get_state()
    demo = random.sample(DEMO_COMMENTS, min(count, len(DEMO_COMMENTS)))
    
    result = []
    for i, comment in enumerate(demo):
        comment_id = f"demo_{int(time.time())}_{i}"
        
        # Skip if already processed
        if comment_id in state['processed_comment_ids']:
            continue
        
        result.append({
            'id': comment_id,
            'author': comment['author'],
            'text': comment['text']
        })
    
    return result

def categorize_comment(text):
    """Categorize comment and return response"""
    text_lower = text.lower()
    
    # Check for spam
    spam_keywords = ['crypto', 'bitcoin', 'mlm', '$5000', 'click here', 'earn money', 'guaranteed']
    for keyword in spam_keywords:
        if keyword in text_lower:
            return {
                "category": "spam",
                "response": None,
                "should_auto_reply": False
            }
    
    # Check for sales/partnership
    sales_keywords = ['partnership', 'collaboration', 'interested in', 'let\'s talk', 'we work with', 'work together']
    for keyword in sales_keywords:
        if keyword in text_lower:
            return {
                "category": "sales",
                "response": None,
                "should_auto_reply": False
            }
    
    # Check for questions and praise
    for category, data in RESPONSES.items():
        for trigger in data['triggers']:
            if trigger in text_lower:
                return {
                    "category": category,
                    "response": data['response'],
                    "should_auto_reply": True
                }
    
    # Default: questions without keywords
    if any(q in text_lower for q in ['how', 'what', 'when', 'where', 'why', '?']):
        return {
            "category": "question_general",
            "response": "Great question! Check the pinned comment for more resources, or reply here and I'll help.",
            "should_auto_reply": True
        }
    
    # Default: flag for review
    return {
        "category": "other",
        "response": None,
        "should_auto_reply": False
    }

def reply_to_comment(youtube, comment_id, reply_text, is_demo=False):
    """Reply to a comment"""
    if is_demo:
        # In demo mode, just log the action
        return True
    
    if not youtube:
        return False
    
    try:
        request = youtube.comments().insert(
            part='snippet',
            body={
                'snippet': {
                    'textOriginal': reply_text,
                    'parentId': comment_id
                }
            }
        )
        response = request.execute()
        return True
    except Exception as e:
        print(f"⚠️ Could not reply to comment {comment_id}: {e}")
        return False

def process_comments(demo_mode=False):
    """Main loop: fetch comments, categorize, reply, log"""
    print("=" * 60)
    print(f"YouTube Comment Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Channel: {CHANNEL_ID}")
    if demo_mode:
        print("Mode: DEMO (synthetic comments)")
    print("=" * 60)
    
    # Load state
    state = get_state()
    
    # Get comments
    if demo_mode:
        comments_raw = generate_demo_comments(count=random.randint(1, 4))
    else:
        youtube = get_youtube_service()
        if youtube is None:
            print("Falling back to DEMO mode...")
            comments_raw = generate_demo_comments(count=random.randint(1, 4))
            demo_mode = True
        else:
            comments_raw = get_recent_comments(youtube, max_results=20)
    
    if not comments_raw:
        print("✅ No new comments to process")
        state['last_run'] = datetime.now().isoformat()
        save_state(state)
        return True
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "mode": "demo" if demo_mode else "production",
        "total_processed": 0,
        "auto_replied": 0,
        "flagged_for_review": 0,
        "categories": {
            "questions": 0,
            "praise": 0,
            "spam": 0,
            "sales": 0,
            "other": 0
        },
        "comments": []
    }
    
    youtube = None if demo_mode else get_youtube_service()
    
    for comment_data in comments_raw:
        # Extract fields
        if demo_mode:
            comment_id = comment_data['id']
            author = comment_data['author']
            text = comment_data['text']
        else:
            comment_id = comment_data['id']
            author = comment_data['author']
            text = comment_data['text']
        
        # Skip if already processed
        if comment_id in state['processed_comment_ids']:
            continue
        
        # Categorize
        categorization = categorize_comment(text)
        category = categorization['category']
        
        # Count category
        if 'question' in category:
            stats['categories']['questions'] += 1
        elif 'amazing' in category or 'inspiring' in category:
            stats['categories']['praise'] += 1
        elif category == 'spam':
            stats['categories']['spam'] += 1
        elif category == 'sales':
            stats['categories']['sales'] += 1
        else:
            stats['categories']['other'] += 1
        
        # Log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "comment_id": comment_id,
            "author": author,
            "text": text[:200],
            "category": category,
            "auto_replied": categorization['should_auto_reply'],
            "response_sent": None
        }
        
        # Reply if applicable
        if categorization['should_auto_reply']:
            success = reply_to_comment(youtube, comment_id, categorization['response'], is_demo=demo_mode)
            if success:
                prefix = "✅ [DEMO]" if demo_mode else "✅"
                print(f"{prefix} Replied to {author}: {category}")
                stats['auto_replied'] += 1
                log_entry['response_sent'] = categorization['response']
            else:
                print(f"⚠️ Failed to reply to {author}")
        else:
            if category == 'spam':
                prefix = "🚫" if demo_mode else "🚫"
                print(f"{prefix} Blocked spam from {author}")
            else:
                prefix = "🚩 [DEMO]" if demo_mode else "🚩"
                print(f"{prefix} Flagged for review: {author} ({category})")
            stats['flagged_for_review'] += 1
        
        stats['comments'].append(log_entry)
        stats['total_processed'] += 1
        
        # Track processed ID
        state['processed_comment_ids'].append(comment_id)
        state['total_processed'] += 1
    
    # Log stats
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(stats) + '\n')
    
    # Save state
    state['last_run'] = datetime.now().isoformat()
    save_state(state)
    
    # Report
    print()
    print("─" * 60)
    print(f"✅ Processed: {stats['total_processed']}")
    print(f"✅ Auto-replied: {stats['auto_replied']}")
    print(f"🚩 Flagged: {stats['flagged_for_review']}")
    print()
    print("Categories:")
    for cat, count in stats['categories'].items():
        if count > 0:
            print(f"  • {cat.title()}: {count}")
    print("─" * 60)
    
    return True

if __name__ == "__main__":
    success = process_comments(demo_mode=False)
    exit(0 if success else 1)
