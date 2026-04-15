#!/usr/bin/env python3
"""
YouTube DM Monitor - Auto-respond and log all DMs
Monitors Concessa Obvius DMs, categorizes them, and sends template responses.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
import re

# Categories for DM classification
Category = Literal["setup_help", "newsletter", "product_inquiry", "partnership"]

TEMPLATES = {
    "setup_help": """Hey! 👋 Thanks for reaching out about setup. I've got detailed guides that should help:

📚 Full setup guide: [link to guide]
🎥 Step-by-step video: [link to video]
💬 Common issues: [link to FAQ]

If you get stuck on a specific step, reply with what's giving you trouble and I'll help!""",

    "newsletter": """Thanks for wanting to stay in the loop! 🔔

✉️ **Join the newsletter:** [link]
📱 You'll get:
- Weekly tips & updates
- Early access to new features
- Exclusive member content

See you there!""",

    "product_inquiry": """Great question! 🎯

📦 **Product info & pricing:** [link]
💰 We have options for every budget
❓ Let me know:
- What's your use case?
- Budget range?
- Team size?

Happy to help you find the perfect fit!""",

    "partnership": """Ooh, interesting! 🤝 I love hearing partnership ideas.

For collab/sponsorship inquiries, let's take this to email so we can dive deeper:
📧 [partnership@concessa.com]

Tell me a bit about what you have in mind and we'll explore it!"""
}

KEYWORDS = {
    "setup_help": ["setup", "how to", "confused", "beginner", "tutorial", "install", "getting started", "doesn't work", "help", "guide"],
    "newsletter": ["newsletter", "updates", "email list", "subscribe", "news", "latest", "stay updated", "follow"],
    "product_inquiry": ["buy", "pricing", "price", "cost", "purchase", "how much", "afford", "product", "which version", "recommend", "features"],
    "partnership": ["collaborate", "sponsorship", "partner", "joint", "co-brand", "affiliate", "promotion", "promote", "work together", "business opportunity"]
}

class YouTubeDMMonitor:
    def __init__(self, log_file: str = ".cache/youtube-dms.jsonl"):
        self.log_file = log_file
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
    def categorize_dm(self, text: str) -> Category:
        """Categorize a DM based on keyword matching."""
        text_lower = text.lower()
        
        # Score each category based on keyword matches
        scores = {}
        for category, keywords in KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = score
        
        # Return category with highest score, default to product_inquiry
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "product_inquiry"
    
    def log_dm(self, sender: str, text: str, category: Category, response_sent: str, interesting_partnership: bool = False):
        """Log a DM to the JSONL file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "text": text,
            "category": category,
            "response_sent": response_sent,
            "interesting_partnership": interesting_partnership
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"✓ Logged DM from {sender} ({category})")
    
    def process_dm(self, sender: str, text: str) -> dict:
        """Process a single DM: categorize, respond, and log."""
        # Categorize
        category = self.categorize_dm(text)
        
        # Get template response
        response = TEMPLATES[category]
        
        # Check if partnership is interesting (for manual review flag)
        interesting = False
        if category == "partnership":
            # Simple heuristic: partnerships with specific companies or large mentions are interesting
            interesting = len(text) > 100 or any(word in text.lower() for word in ["brand", "major", "large", "budget"])
        
        # Log
        self.log_dm(sender, text, category, response, interesting)
        
        return {
            "sender": sender,
            "category": category,
            "response": response,
            "flag_for_review": interesting
        }
    
    def get_stats(self) -> dict:
        """Generate report stats from the log file."""
        if not os.path.exists(self.log_file):
            return {
                "total_dms": 0,
                "auto_responses_sent": 0,
                "by_category": {},
                "partnerships_flagged": 0,
                "conversion_potential": "No data yet"
            }
        
        dms = []
        with open(self.log_file, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        dms.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        categories = {}
        product_inquiries = 0
        partnerships_flagged = 0
        
        for dm in dms:
            cat = dm.get("category")
            categories[cat] = categories.get(cat, 0) + 1
            
            if cat == "product_inquiry":
                product_inquiries += 1
            if dm.get("interesting_partnership"):
                partnerships_flagged += 1
        
        return {
            "total_dms": len(dms),
            "auto_responses_sent": len([d for d in dms if d.get("response_sent")]),
            "by_category": categories,
            "partnerships_flagged": partnerships_flagged,
            "conversion_potential": f"{product_inquiries} product inquiries to follow up on"
        }

# Demo/Test Mode
if __name__ == "__main__":
    monitor = YouTubeDMMonitor()
    
    # Example DMs (for testing)
    test_dms = [
        ("Alice_Creator", "Hey! I'm trying to set up your product but I'm confused about the first step. Can you help?"),
        ("marketing_guy", "Hi! We'd love to collaborate on a sponsorship. What are your rates?"),
        ("subscriber_jane", "Are you planning a newsletter? I'd love to stay updated on new releases!"),
        ("potential_buyer", "Hi, how much does the pro version cost and what's the difference from the free plan?"),
    ]
    
    print("📊 YouTube DM Monitor Test\n")
    
    for sender, text in test_dms:
        result = monitor.process_dm(sender, text)
        print(f"  From: {result['sender']}")
        print(f"  Category: {result['category']}")
        if result['flag_for_review']:
            print(f"  🚩 Flagged for manual review")
        print()
    
    # Print stats
    stats = monitor.get_stats()
    print("\n📈 REPORT")
    print(f"Total DMs processed: {stats['total_dms']}")
    print(f"Auto-responses sent: {stats['auto_responses_sent']}")
    print(f"By category: {stats['by_category']}")
    print(f"Partnerships flagged: {stats['partnerships_flagged']}")
    print(f"Conversion potential: {stats['conversion_potential']}")
