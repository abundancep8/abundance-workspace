#!/usr/bin/env python3
"""
YouTube Comment Monitor - DEMO MODE
Shows categorization, response generation, and logging WITHOUT needing YouTube API auth.
Perfect for testing the system before completing OAuth setup.
"""

import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/abundance/.openclaw/workspace")
CACHE_DIR = WORKSPACE / ".cache"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"

# Sample comments for demo
DEMO_COMMENTS = [
    {
        "comment_id": "demo_1",
        "video_id": "VID_001",
        "author": "Alice Johnson",
        "text": "This is amazing! Exactly what I needed. Thank you so much!",
        "timestamp": datetime.now().isoformat() + "Z",
        "author_channel_url": "http://example.com/alice"
    },
    {
        "comment_id": "demo_2",
        "video_id": "VID_002",
        "author": "Bob Smith",
        "text": "How much does this cost? And what's the timeline for getting started?",
        "timestamp": datetime.now().isoformat() + "Z",
        "author_channel_url": "http://example.com/bob"
    },
    {
        "comment_id": "demo_3",
        "video_id": "VID_003",
        "author": "Crypto_Bro",
        "text": "Hey! Make money fast with Bitcoin! Click here: bit.ly/crypto123",
        "timestamp": datetime.now().isoformat() + "Z",
        "author_channel_url": "http://example.com/crypto"
    },
    {
        "comment_id": "demo_4",
        "video_id": "VID_004",
        "author": "Marketing Inc",
        "text": "We're interested in a partnership or sponsorship opportunity. Let's collaborate!",
        "timestamp": datetime.now().isoformat() + "Z",
        "author_channel_url": "http://example.com/marketing"
    },
    {
        "comment_id": "demo_5",
        "video_id": "VID_005",
        "author": "Carol White",
        "text": "This is brilliant work! Love the approach. Very inspiring.",
        "timestamp": datetime.now().isoformat() + "Z",
        "author_channel_url": "http://example.com/carol"
    },
    {
        "comment_id": "demo_6",
        "video_id": "VID_006",
        "author": "Dave Brown",
        "text": "Can someone help me understand the tools mentioned? What would you recommend?",
        "timestamp": datetime.now().isoformat() + "Z",
        "author_channel_url": "http://example.com/dave"
    },
    {
        "comment_id": "demo_7",
        "video_id": "VID_007",
        "author": "Eve Garcia",
        "text": "Just watched this, good information. Thank you!",
        "timestamp": datetime.now().isoformat() + "Z",
        "author_channel_url": "http://example.com/eve"
    }
]

# Category patterns
PATTERNS = {
    "question": {
        "keywords": r"(?:how|what|when|where|why|which|can i|do i|should i|help|question|need|looking for|cost|price|timeline|tools|start)",
        "weight": 0.8
    },
    "praise": {
        "keywords": r"(?:amazing|awesome|incredible|inspiring|love|great|brilliant|thanks|thank you|so helpful|exactly what|perfect)",
        "weight": 0.8
    },
    "spam": {
        "keywords": r"(?:crypto|bitcoin|ethereum|nft|mlm|pyramid|forex|trading bot|click here|dm me|link in bio|free money|guaranteed profit|work from home)",
        "weight": 0.9
    },
    "sales": {
        "keywords": r"(?:partnership|collaboration|sponsorship|advertise|promote|affiliate|business opportunity|marketing|promotion|brand deal)",
        "weight": 0.7
    }
}

# Response templates
RESPONSE_TEMPLATES = {
    "question": """Thanks for the question! 🎯

{question_summary}

For detailed answers and resources, visit our help center or feel free to reach out. We're here to help!

—Concessa Team""",
    
    "praise": """Thank you so much for the kind words! 🙏 We're thrilled you found this valuable. Comments like yours keep us motivated to keep creating great content. 

—Concessa Team""",
}


def categorize_comment(text):
    """Categorize a comment based on patterns."""
    text_lower = text.lower()
    scores = {}
    
    for category, pattern_info in PATTERNS.items():
        if re.search(pattern_info["keywords"], text_lower):
            scores[category] = pattern_info["weight"]
        else:
            scores[category] = 0
    
    # Assign category with highest score, or default to "general"
    if scores:
        top_category = max(scores, key=scores.get)
        if scores[top_category] > 0:
            return top_category
    
    return "general"


def generate_response(category, comment_text):
    """Generate auto-response if applicable."""
    if category == "question":
        # Extract question summary
        question_match = re.search(r"^[^?]+\??", comment_text)
        question_summary = (question_match.group(0) if question_match else comment_text[:100]).strip()
        return RESPONSE_TEMPLATES["question"].format(question_summary=question_summary)
    
    elif category == "praise":
        return RESPONSE_TEMPLATES["praise"]
    
    return None


def log_comment(comment_data, category, response_id=None):
    """Log comment to JSONL file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "comment_id": comment_data["comment_id"],
        "video_id": comment_data["video_id"],
        "commenter": comment_data["author"],
        "text": comment_data["text"],
        "category": category,
        "response_status": "auto_replied" if response_id else "flagged" if category == "sales" else "logged",
        "response_id": response_id,
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry


def main():
    """Run demo."""
    print(f"\n{'='*70}")
    print(f"🎬 YouTube Comment Monitor - DEMO MODE")
    print(f"{'='*70}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Pacific)")
    print(f"Channel: Concessa Obvius (Demo with {len(DEMO_COMMENTS)} sample comments)")
    print(f"{'='*70}\n")
    
    auto_response_count = 0
    flagged_count = 0
    spam_count = 0
    general_count = 0
    question_count = 0
    praise_count = 0
    
    for i, comment in enumerate(DEMO_COMMENTS, 1):
        category = categorize_comment(comment["text"])
        response_id = None
        
        print(f"📝 Comment {i}: {comment['author']}")
        print(f"   Category: {category.upper()}")
        print(f"   Text: \"{comment['text'][:60]}...\"")
        
        # Categorize
        if category == "question":
            question_count += 1
        elif category == "praise":
            praise_count += 1
        elif category == "spam":
            spam_count += 1
        elif category == "sales":
            pass
        else:
            general_count += 1
        
        # Auto-respond to questions and praise
        if category in ["question", "praise"]:
            response_text = generate_response(category, comment["text"])
            if response_text:
                response_id = "DEMO_RESPONSE_" + str(i)
                auto_response_count += 1
                print(f"   ✓ Auto-response generated")
                print(f"   Response preview: \"{response_text[:80]}...\"")
        
        # Flag sales for manual review
        if category == "sales":
            flagged_count += 1
            print(f"   ⚠️  FLAGGED FOR REVIEW")
        
        # Log comment
        log_comment(comment, category, response_id)
        
        print()
    
    # Generate report
    print(f"{'='*70}")
    print(f"📊 Demo Processing Report")
    print(f"{'='*70}\n")
    
    print(f"📈 Comment Breakdown:")
    print(f"   • Questions: {question_count}")
    print(f"   • Praise: {praise_count}")
    print(f"   • Spam: {spam_count}")
    print(f"   • Sales/Partnerships: {flagged_count}")
    print(f"   • General: {general_count}")
    print(f"   • TOTAL PROCESSED: {len(DEMO_COMMENTS)}\n")
    
    print(f"🤖 Automation Stats:")
    print(f"   • Auto-responses sent: {auto_response_count}")
    print(f"   • Flagged for review: {flagged_count}")
    print(f"   • Logged (no response): {len(DEMO_COMMENTS) - auto_response_count - flagged_count}\n")
    
    print(f"📁 Logged to: {LOG_FILE}")
    print(f"   (This is where real comments will be stored after OAuth setup)\n")
    
    print(f"{'='*70}")
    print(f"✅ Demo Complete!")
    print(f"{'='*70}\n")
    
    print(f"📋 View logged comments:")
    print(f"   cat {LOG_FILE} | jq .\n")
    
    print(f"🔐 To activate with real YouTube comments:")
    print(f"   python3 scripts/youtube-setup-auth.py")
    print(f"   (This will open a browser to authorize access)\n")
    
    print(f"🚀 Then run the live monitor:")
    print(f"   python3 scripts/youtube-comment-monitor.py\n")


if __name__ == "__main__":
    main()
