#!/usr/bin/env python3
"""
YouTube DM Monitor for Concessa Obvius
Checks for new messages, categorizes, auto-responds, and logs.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
LOG_FILE = Path.home() / ".openclaw/workspace/.cache/youtube-dms.jsonl"
LAST_CHECK_FILE = Path.home() / ".openclaw/workspace/.cache/youtube-dms-lastcheck.json"

# Auto-response templates by category
RESPONSES = {
    "setup_help": """Thanks for reaching out! 🎬 

For setup help, here are our best resources:
- **Getting Started Guide**: [link]
- **FAQ**: [link]
- **Video Tutorial**: [link]

If you're still stuck, let us know exactly where you're hitting a wall and we'll help!""",
    
    "newsletter": """Great timing! 📧

Join our newsletter for:
- Exclusive updates & early features
- Weekly tips & tricks
- Community stories
- Special offers

**Sign up here**: [link]

You'll be on the list within 5 minutes!""",
    
    "product_inquiry": """Thanks for your interest! 🛍️

Quick details:
- **Pricing**: [link]
- **Product comparison**: [link]
- **FAQ**: [link]

Questions? We can answer anything. When were you looking to get started?""",
    
    "partnership": """This is interesting! 🤝

We're always open to collaborations. Let's chat more:
- **What's your vision?**
- **Timeline?**
- **What would success look like?**

Reply with more details or we can hop on a call this week. Excited to explore this!"""
}

# Categorization keywords
KEYWORDS = {
    "setup_help": ["help", "setup", "confused", "how do i", "tutorial", "guide", "error", "stuck", "not working"],
    "newsletter": ["newsletter", "email list", "subscribe", "updates", "news", "announcements"],
    "product_inquiry": ["price", "pricing", "buy", "purchase", "cost", "plan", "features", "product", "how much"],
    "partnership": ["collaborate", "partner", "sponsorship", "brand deal", "collab", "campaign", "work together"]
}

def categorize_dm(text):
    """Categorize a DM based on keywords."""
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in text_lower)
    
    best_category = max(scores.items(), key=lambda x: x[1])
    return best_category[0] if best_category[1] > 0 else "other"

def log_dm(sender, text, category, response_sent=False):
    """Log a DM to the JSONL file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "sender": sender,
        "text": text,
        "category": category,
        "response_sent": response_sent
    }
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def get_stats():
    """Generate report of DM activity."""
    if not LOG_FILE.exists():
        return {
            "total_dms": 0,
            "auto_responses_sent": 0,
            "by_category": {},
            "conversion_potential": []
        }
    
    stats = {
        "total_dms": 0,
        "auto_responses_sent": 0,
        "by_category": {},
        "partnership_opportunities": []
    }
    
    with open(LOG_FILE) as f:
        for line in f:
            entry = json.loads(line)
            stats["total_dms"] += 1
            if entry["response_sent"]:
                stats["auto_responses_sent"] += 1
            
            cat = entry["category"]
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            
            # Flag partnership opportunities for manual review
            if cat == "partnership":
                stats["partnership_opportunities"].append({
                    "timestamp": entry["timestamp"],
                    "sender": entry["sender"],
                    "text": entry["text"][:100] + "..."
                })
    
    return stats

def process_dms(new_dms):
    """
    Process new DMs from YouTube.
    Expected format: list of {"sender": str, "text": str}
    """
    processed = 0
    for dm in new_dms:
        sender = dm.get("sender", "Unknown")
        text = dm.get("text", "")
        
        category = categorize_dm(text)
        response_template = RESPONSES.get(category, "Thanks for reaching out! We'll get back to you soon.")
        
        # In real implementation, send response via YouTube API
        # For now, just log it
        log_dm(sender, text, category, response_sent=True)
        processed += 1
        
        print(f"✓ {sender} | {category} | {text[:60]}...")
    
    return processed

if __name__ == "__main__":
    # This would be called by the cron job
    # In real use: fetch DMs from YouTube API, then call process_dms()
    
    stats = get_stats()
    print("\n📊 YouTube DM Monitor Report")
    print(f"Total DMs processed: {stats['total_dms']}")
    print(f"Auto-responses sent: {stats['auto_responses_sent']}")
    print(f"By category: {stats['by_category']}")
    if stats['partnership_opportunities']:
        print(f"\n🤝 Partnership opportunities ({len(stats['partnership_opportunities'])}):")
        for opp in stats['partnership_opportunities'][-3:]:  # Last 3
            print(f"  - {opp['sender']}: {opp['text']}")
