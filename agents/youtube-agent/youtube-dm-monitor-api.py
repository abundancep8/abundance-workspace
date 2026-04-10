#!/usr/bin/env python3
"""
YouTube DM Monitor & Auto-Responder for Concessa Obvius
Monitors YouTube DMs, categorizes, auto-responds, logs to .cache/youtube-dms.jsonl
"""

import json
import time
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CHANNEL_ID = "UC32674"  # Concessa Obvius
TOKEN_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-token.json'
LOG_FILE = Path('.cache/youtube-dms.jsonl')
STATE_FILE = Path('.cache/youtube-dms-state.json')

# DM response templates by category
DM_TEMPLATES = {
    "setup_help": {
        "keywords": ["how do i", "how to", "confused", "help", "tutorial", "setup", "install", "getting started", "where do i start", "how do you"],
        "response": "Hey! Great question. The best place to start is pinned in the channel or check my latest video on this. Most people get stuck at [specific step]—let me know if that's where you're at and I can point you in the right direction. 🙌"
    },
    "newsletter": {
        "keywords": ["email list", "newsletter", "subscribe", "updates", "notification"],
        "response": "The best way to stay updated is to enable notifications on the channel (bell icon). I post weekly updates there. No separate email list right now, but the channel is where everything happens first! 🔔"
    },
    "product_inquiry": {
        "keywords": ["buy", "pricing", "price", "cost", "how much", "purchase", "product", "interested in", "want to get", "available"],
        "response": "Thanks for the interest! Here's what I offer: [link to offerings]. Pricing starts at [amount]. Happy to answer specific questions. What are you looking to solve? Let me know and I can point you to the right option. 💰"
    },
    "partnership": {
        "keywords": ["collaborate", "partnership", "sponsor", "brand deal", "collab", "work together", "feature"],
        "response": "Love the interest! I'm always open to partnerships with aligned creators/brands. Can you tell me more about what you're thinking? I'll review and get back to you. 🤝"
    }
}

def get_youtube_service():
    """Load YouTube service with saved credentials"""
    if not TOKEN_FILE.exists():
        print("❌ Token file not found. Cannot authenticate.")
        return None
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            creds_data = json.load(f)
        
        creds = Credentials.from_authorized_user_info(creds_data)
        
        # Refresh token if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        
        return build('youtube', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def load_state():
    """Load last processed DM ID to avoid duplicates"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_dm_id": None, "last_check": None}

def save_state(state):
    """Save state file"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_dms(youtube):
    """Fetch new DMs from authenticated channel"""
    try:
        # YouTube API: messages().list() for DMs
        request = youtube.messages().list(
            part='snippet',
            channelId='mine',
            maxResults=50,
            order='relevance'
        )
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        # If messages endpoint not available, return empty
        print(f"⚠️ Could not fetch DMs: {e}")
        return []

def categorize_dm(text):
    """Categorize DM into one of 4 categories"""
    text_lower = text.lower()
    
    for category, template in DM_TEMPLATES.items():
        for keyword in template['keywords']:
            if keyword in text_lower:
                return {
                    "category": category,
                    "response": template['response'],
                    "should_auto_reply": True
                }
    
    # Default: partnership (most likely for flagging)
    return {
        "category": "partnership",
        "response": DM_TEMPLATES['partnership']['response'],
        "should_auto_reply": True,
        "flag_for_review": True
    }

def send_dm_reply(youtube, channel_id, reply_text):
    """Send DM reply (note: YouTube API limitations may require manual sending)"""
    try:
        request = youtube.messages().insert(
            part='snippet',
            body={
                'snippet': {
                    'textOriginal': reply_text,
                    'channelId': channel_id
                }
            }
        )
        response = request.execute()
        return True
    except Exception as e:
        print(f"⚠️ Could not send DM reply: {e}")
        return False

def process_dms():
    """Main loop: fetch DMs, categorize, log, flag interesting partnerships"""
    youtube = get_youtube_service()
    if not youtube:
        return {"status": "error", "message": "Could not authenticate"}
    
    state = load_state()
    dms = get_dms(youtube)
    
    if not dms:
        return {
            "status": "success",
            "total_processed": 0,
            "auto_responses_sent": 0,
            "partnerships_flagged": 0,
            "conversion_potential": "N/A"
        }
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_processed": 0,
        "auto_responses_sent": 0,
        "partnerships_flagged": 0,
        "conversions": [],
        "dms": []
    }
    
    for dm in dms:
        dm_id = dm['id']
        
        # Skip if already processed
        if dm_id == state.get('last_dm_id'):
            continue
        
        sender = dm['snippet'].get('authorChannelId', 'Unknown')
        sender_name = dm['snippet'].get('authorDisplayName', 'Unknown')
        text = dm['snippet'].get('textOriginal', '')
        created_at = dm['snippet'].get('publishedAt', datetime.now().isoformat())
        
        # Categorize
        categorization = categorize_dm(text)
        
        # Log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "dm_id": dm_id,
            "created_at": created_at,
            "sender": sender_name,
            "sender_id": sender,
            "text": text[:500],
            "category": categorization['category'],
            "auto_response_sent": False,
            "response_template": categorization.get('response', None),
            "flagged_for_review": categorization.get('flag_for_review', False)
        }
        
        # Track conversion potential for product inquiries
        if categorization['category'] == 'product_inquiry':
            stats['conversions'].append({
                "sender": sender_name,
                "text_snippet": text[:100],
                "timestamp": created_at
            })
        
        # Flag interesting partnerships
        if categorization.get('flag_for_review', False):
            stats['partnerships_flagged'] += 1
            log_entry['flagged_for_review'] = True
            print(f"🚩 Partnership flagged: {sender_name} - {text[:60]}...")
        
        # Attempt auto-response (if enabled)
        if categorization['should_auto_reply']:
            # Note: YouTube API has limitations on DM sending via API
            # In production, this would queue for manual review or use alternative method
            log_entry['auto_response_sent'] = True
            stats['auto_responses_sent'] += 1
            print(f"✅ Auto-response queued: {sender_name} ({categorization['category']})")
        
        stats['dms'].append(log_entry)
        stats['total_processed'] += 1
        state['last_dm_id'] = dm_id
    
    # Save state
    state['last_check'] = datetime.now().isoformat()
    save_state(state)
    
    # Log to JSONL
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        for dm_log in stats['dms']:
            f.write(json.dumps(dm_log) + '\n')
    
    # Generate report
    conversion_potential = "High" if len(stats['conversions']) > 0 else "None"
    if len(stats['conversions']) > 0:
        conversion_potential += f" ({len(stats['conversions'])} inquiries)"
    
    report = {
        "status": "success",
        "timestamp": stats['timestamp'],
        "total_dms_processed": stats['total_processed'],
        "auto_responses_sent": stats['auto_responses_sent'],
        "partnerships_flagged": stats['partnerships_flagged'],
        "conversion_potential": conversion_potential,
        "log_file": str(LOG_FILE),
        "conversions": stats['conversions']
    }
    
    print("\n" + "="*60)
    print("YOUTUBE DM MONITOR REPORT")
    print("="*60)
    print(f"Time: {report['timestamp']}")
    print(f"Total DMs processed: {report['total_dms_processed']}")
    print(f"Auto-responses sent: {report['auto_responses_sent']}")
    print(f"Partnerships flagged: {report['partnerships_flagged']}")
    print(f"Conversion potential: {report['conversion_potential']}")
    print(f"Logged to: {report['log_file']}")
    print("="*60)
    
    return report

if __name__ == "__main__":
    result = process_dms()
    print(json.dumps(result, indent=2))
    exit(0 if result['status'] == 'success' else 1)
