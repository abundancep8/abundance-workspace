#!/usr/bin/env python3
"""
YouTube Comment Monitor - Demo Mode
Shows how the categorization and logging works without needing API credentials.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import re

LOG_FILE = Path(".cache/youtube-comments.jsonl")

# Sample comments for demo
SAMPLE_COMMENTS = [
    {
        "author": "Sarah Tech",
        "text": "How do I start learning this? What tools do you recommend?",
        "category": "question"
    },
    {
        "author": "Alex Creator",
        "text": "This is absolutely amazing! So inspiring, thank you for sharing! 🙌",
        "category": "praise"
    },
    {
        "author": "CryptoSam",
        "text": "Get rich quick with our crypto scheme! DM me DM me!",
        "category": "spam"
    },
    {
        "author": "Jordan Marketing",
        "text": "Love your content! Would love to discuss a partnership/collaboration opportunity.",
        "category": "sales"
    },
    {
        "author": "Mike Dev",
        "text": "Timeline for the next release? Cost to implement?",
        "category": "question"
    },
    {
        "author": "Emma Fan",
        "text": "This is incredible work. Truly the best content on this topic. Excellent presentation!",
        "category": "praise"
    },
    {
        "author": "SpamBot",
        "text": "LIMITED OFFER! Get rich fast! Limited offer! Subscribe my channel now!",
        "category": "spam"
    },
    {
        "author": "Lisa Sales",
        "text": "Hi! We'd love to promote this. Are you interested in a brand deal or sponsorship?",
        "category": "sales"
    }
]

# Categorization rules
CATEGORIES = {
    "question": {
        "patterns": [
            r"how\s+(do|can|to)\s+", r"what\s+(is|are|do|should)", r"where\s+(is|can|to)",
            r"when\s+(should|can|do)", r"why\s+(not|don't|can't)", r"\?",
            r"tools?", r"cost", r"price", r"timeline", r"start"
        ],
        "response": "Thank you for your question! We appreciate your interest. Here are some resources that might help: [Insert relevant link]. Feel free to reach out with any other questions!"
    },
    "praise": {
        "patterns": [
            r"amazing", r"inspiring", r"incredible", r"awesome", r"love\s+this",
            r"thank\s+you", r"grateful", r"best", r"excellent", r"wonderful",
            r"great\s+work", r"impressed", r"❤️", r"👏", r"🙌"
        ],
        "response": "Thank you so much for the kind words! We're thrilled you found this valuable. Your support means everything to us! 💜"
    },
    "spam": {
        "patterns": [
            r"crypto", r"bitcoin", r"nft", r"mlm", r"multi.level", r"forex",
            r"get rich", r"earn.*fast", r"click.*link", r"dm.*dm", r"dm me",
            r"buy now", r"limited offer", r"subscribe.*channel"
        ],
        "response": None
    },
    "sales": {
        "patterns": [
            r"partnership", r"collaboration", r"sponsor", r"advertis",
            r"promote", r"affiliate", r"business\s+opportunity", r"would\s+love\s+to\s+work",
            r"interested\s+in\s+partnering", r"brand\s+deal"
        ],
        "response": None
    }
}

def categorize_comment(text: str) -> str:
    """Categorize comment by type"""
    text_lower = text.lower()
    
    for category, config in CATEGORIES.items():
        patterns = config["patterns"]
        if any(re.search(pattern, text_lower) for pattern in patterns):
            return category
    
    return "other"

def run_demo():
    """Run demo with sample comments"""
    print("\n" + "="*70)
    print("YOUTUBE COMMENT MONITOR - DEMO MODE")
    print("="*70)
    print("\nThis demo shows how the categorization and logging works.\n")
    
    # Clear demo logs if they exist
    demo_log = Path(".cache/youtube-comments-demo.jsonl")
    if demo_log.exists():
        demo_log.unlink()
    
    # Process sample comments
    total = len(SAMPLE_COMMENTS)
    auto_responses = 0
    flagged_review = 0
    
    print(f"Processing {total} sample comments:\n")
    print("-" * 70)
    
    for comment in SAMPLE_COMMENTS:
        detected_category = categorize_comment(comment["text"])
        expected_category = comment["category"]
        match = "✓" if detected_category == expected_category else "✗"
        
        print(f"\n{match} Author: {comment['author']}")
        print(f"  Text: {comment['text']}")
        print(f"  Category: {detected_category} (expected: {expected_category})")
        
        # Determine response
        response_status = "skipped"
        if detected_category == "question":
            response = CATEGORIES["question"]["response"]
            response_status = "auto_response_ready"
            auto_responses += 1
            print(f"  Response: {response[:60]}...")
        elif detected_category == "praise":
            response = CATEGORIES["praise"]["response"]
            response_status = "auto_response_ready"
            auto_responses += 1
            print(f"  Response: {response[:60]}...")
        elif detected_category == "spam":
            response_status = "spam_ignored"
            print(f"  Response: [IGNORED - SPAM]")
        elif detected_category == "sales":
            response_status = "flagged_review"
            flagged_review += 1
            print(f"  Response: [FLAGGED FOR MANUAL REVIEW]")
        
        # Log to demo file
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "comment_id": f"demo_{len(SAMPLE_COMMENTS)}",
            "commenter": comment["author"],
            "text": comment["text"],
            "category": detected_category,
            "response_status": response_status
        }
        
        with open(demo_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    # Print report
    print("\n" + "="*70)
    print("REPORT")
    print("="*70)
    print(f"Total Comments Processed:  {total}")
    print(f"Auto-Responses Ready:      {auto_responses}")
    print(f"Flagged for Review:        {flagged_review}")
    print(f"Spam/Other Ignored:        {total - auto_responses - flagged_review}")
    print(f"Log File:                  {demo_log}")
    print("="*70)
    
    # Show logged data
    print("\nLogged Comments (JSONL format):\n")
    with open(demo_log) as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            print(f"{i}. {data['commenter']} [{data['category']}]")
            print(f"   {data['text'][:65]}...")
            print(f"   Status: {data['response_status']}\n")
    
    print("\nTo view the raw JSON:")
    print(f"  cat {demo_log} | jq .")
    print("\nTo get just flagged reviews:")
    print(f"  grep flagged_review {demo_log} | jq .")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Review the categorization accuracy above
2. If satisfied, set up real YouTube API:
   - Read: .cache/youtube-monitor-setup.md
   - Get API key from Google Cloud Console
   - Set: export YOUTUBE_API_KEY="your-key"
3. Run the real monitor:
   - python3 .cache/youtube_monitor.py
4. Configure cron for every 30 minutes:
   - See youtube-monitor-setup.md for cron command
5. Monitor the logs:
   - tail -f .cache/youtube-monitor.log

Questions? Check setup guide or run:
  python3 .cache/youtube_monitor.py --help
""")

if __name__ == "__main__":
    run_demo()
