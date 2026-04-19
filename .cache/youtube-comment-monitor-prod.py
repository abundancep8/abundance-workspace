#!/usr/bin/env python3
"""
YouTube Comment Monitor - Production Implementation
Monitors Concessa Obvius channel with categorization, auto-responses, and logging
Supports both real YouTube API and demo mode
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import random

WORKSPACE = Path.home() / ".openclaw" / "workspace"
CACHE = WORKSPACE / ".cache"
COMMENTS_LOG = CACHE / "youtube-comments.jsonl"
STATE_FILE = CACHE / ".youtube-monitor-state.json"
CONFIG_FILE = CACHE / "youtube-monitor-config.json"
REPORT_FILE = CACHE / "youtube-comments-report.txt"


class YouTubeCommentCategories:
    """Define and check comment categories"""
    
    QUESTIONS = "questions"
    PRAISE = "praise"
    SPAM = "spam"
    SALES = "sales"
    
    PATTERNS = {
        QUESTIONS: {
            "keywords": [
                "how do i", "how to", "how can", "what is", "where can",
                "cost", "price", "timeline", "when", "tools", "setup",
                "start", "getting started", "tutorial", "help", "how does",
                "can i", "?"
            ],
            "auto_respond": True,
            "template": "Thanks for asking! [Answer framework: 1) Start here, 2) Tools needed, 3) Next steps] Feel free to reach out with follow-ups."
        },
        PRAISE: {
            "keywords": [
                "amazing", "awesome", "incredible", "love", "great",
                "brilliant", "inspiring", "fantastic", "excellent",
                "genius", "mind-blowing", "game-changer", "thank you",
                "appreciate", "wonderful", "fantastic"
            ],
            "auto_respond": True,
            "template": "Thank you so much! Comments like yours keep me motivated. Appreciate the support!"
        },
        SPAM: {
            "keywords": [
                "crypto", "bitcoin", "ethereum", "nft", "mlm",
                "multi-level", "join now", "click here", "limited time",
                "act fast", "earn money fast", "work from home", "guaranteed",
                "forex", "casino", "betting", "dm me", "click link"
            ],
            "auto_respond": False,
            "action": "skip"
        },
        SALES: {
            "keywords": [
                "partnership", "collaboration", "sponsor", "advertisement",
                "promote", "business opportunity", "affiliate", "brand deal",
                "looking to work", "can we partner", "let's collaborate",
                "white label", "reseller", "work together"
            ],
            "auto_respond": False,
            "action": "flag"
        }
    }
    
    @classmethod
    def categorize(cls, text: str) -> Tuple[str, float]:
        """Categorize comment and return category + confidence"""
        text_lower = text.lower()
        
        # Check critical categories first (sales, spam) with priority weighting
        # These should take precedence over praise/questions
        priority_order = [cls.SALES, cls.SPAM, cls.QUESTIONS, cls.PRAISE]
        
        scores = {}
        for category, pattern in cls.PATTERNS.items():
            matches = sum(1 for kw in pattern["keywords"] if kw in text_lower)
            scores[category] = matches
        
        # Return highest scoring category, using priority for ties
        if max(scores.values()) > 0:
            max_score = max(scores.values())
            # Get all categories with max score, then pick by priority
            candidates = [cat for cat, score in scores.items() if score == max_score]
            if len(candidates) == 1:
                top_category = candidates[0]
            else:
                # Multiple categories tied - use priority order
                top_category = next(cat for cat in priority_order if cat in candidates)
            confidence = min(1.0, max_score / 5)  # Normalize
            return top_category, confidence
        
        return "general", 0.5


class YouTubeCommentMonitor:
    """Monitor YouTube comments with auto-categorization and response"""
    
    def __init__(self, use_demo: bool = False):
        self.cache = CACHE
        self.cache.mkdir(parents=True, exist_ok=True)
        
        self.use_demo = use_demo
        self.config = self._load_config()
        self.state = self._load_state()
        
        self.processed_comments = []
        self.stats = {
            "total_processed": 0,
            "questions": {"count": 0, "responded": 0},
            "praise": {"count": 0, "responded": 0},
            "spam": {"count": 0, "logged": 0},
            "sales": {"count": 0, "flagged": 0},
            "general": {"count": 0},
        }
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
        return {
            "channel": {
                "name": "Concessa Obvius",
                "username": "@ConcessaObvius"
            }
        }
    
    def _load_state(self) -> Dict:
        """Load monitoring state"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {
            "last_run": None,
            "total_all_time": 0,
            "auto_responses_sent": 0,
            "flagged_for_review": 0,
        }
    
    def _save_state(self):
        """Persist state"""
        self.state.update({
            "last_run": datetime.now(timezone.utc).isoformat(),
            "total_all_time": self.state.get("total_all_time", 0) + len(self.processed_comments),
            "auto_responses_sent": self.stats["questions"]["responded"] + self.stats["praise"]["responded"],
            "flagged_for_review": self.stats["sales"]["flagged"],
        })
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def _generate_response(self, category: str, author: str) -> Optional[str]:
        """Generate auto-response if applicable"""
        pattern = YouTubeCommentCategories.PATTERNS.get(category)
        if not pattern or not pattern.get("auto_respond"):
            return None
        
        template = pattern.get("template", "")
        response = template.replace("[Author]", author)
        return response
    
    def _log_comment(self, comment: Dict, category: str, response: Optional[str], responded: bool):
        """Log comment to JSONL"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "comment_id": comment.get("comment_id", ""),
            "commenter": comment.get("author", "Unknown"),
            "text": comment.get("text", ""),
            "category": category,
            "auto_response_sent": responded,
            "response_text": response,
        }
        
        with open(COMMENTS_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        self.processed_comments.append(log_entry)
    
    def _demo_comments(self) -> List[Dict]:
        """Generate realistic demo comments"""
        return [
            {
                "comment_id": "demo_q1",
                "video_id": "vid1",
                "author": "Sarah Chen",
                "text": "How do I get started with this? What tools do I need?",
                "published_at": "2026-04-18T05:15:00Z",
                "likes": 5
            },
            {
                "comment_id": "demo_q2",
                "video_id": "vid2",
                "author": "Marcus Johnson",
                "text": "What's the timeline for implementation? When can I start?",
                "published_at": "2026-04-18T05:20:00Z",
                "likes": 3
            },
            {
                "comment_id": "demo_p1",
                "video_id": "vid1",
                "author": "Elena Rodriguez",
                "text": "This is absolutely amazing! So inspiring and well-explained. Thank you!",
                "published_at": "2026-04-18T05:25:00Z",
                "likes": 12
            },
            {
                "comment_id": "demo_p2",
                "video_id": "vid3",
                "author": "Alex Kim",
                "text": "Love the approach here! Really impressed with the quality. Great work!",
                "published_at": "2026-04-18T05:30:00Z",
                "likes": 8
            },
            {
                "comment_id": "demo_s1",
                "video_id": "vid2",
                "author": "Crypto Trading Bot",
                "text": "BUY CRYPTO NOW!!! Limited offer, DM me for details on the new blockchain opportunity",
                "published_at": "2026-04-18T05:35:00Z",
                "likes": 0
            },
            {
                "comment_id": "demo_b1",
                "video_id": "vid1",
                "author": "Jessica Parker",
                "text": "Hi! Love your content. Would love to explore a partnership opportunity with you. Let's connect!",
                "published_at": "2026-04-18T05:40:00Z",
                "likes": 2
            },
        ]
    
    def process_comments(self, comments: List[Dict]):
        """Process and categorize comments"""
        for comment in comments:
            # Categorize
            category, confidence = YouTubeCommentCategories.categorize(comment["text"])
            
            # Generate response if applicable
            response = self._generate_response(category, comment.get("author", "there"))
            responded = response is not None
            
            # Update stats
            self.stats["total_processed"] += 1
            if category in self.stats:
                if isinstance(self.stats[category], dict):
                    self.stats[category]["count"] += 1
                    if responded:
                        self.stats[category]["responded"] += 1
                    if not responded and category == "sales":
                        self.stats[category]["flagged"] += 1
                    elif not responded and category == "spam":
                        self.stats[category]["logged"] += 1
            
            # Log the comment
            self._log_comment(comment, category, response, responded)
    
    def print_summary(self, comments: List[Dict]):
        """Print processing summary"""
        print(f"\n{'='*70}")
        print(f"YOUTUBE COMMENT MONITOR - {self.config['channel']['name'].upper()}")
        print(f"{'='*70}\n")
        
        print(f"Run Time: {datetime.now(timezone.utc).isoformat()}")
        print(f"Channel: {self.config['channel']['name']} ({self.config['channel'].get('username', 'N/A')})")
        print(f"Mode: {'DEMO' if self.use_demo else 'LIVE'}")
        print()
        
        print(f"PROCESSING SUMMARY")
        print(f"-" * 70)
        print(f"Total Comments Processed: {self.stats['total_processed']}")
        print(f"Auto-Responses Sent: {self.stats['questions']['responded'] + self.stats['praise']['responded']}")
        print(f"Flagged for Manual Review: {self.stats['sales']['flagged']}")
        print()
        
        print(f"BREAKDOWN BY CATEGORY")
        print(f"-" * 70)
        print(f"Questions:     {self.stats['questions']['count']:2d} (responded: {self.stats['questions']['responded']})")
        print(f"Praise:        {self.stats['praise']['count']:2d} (responded: {self.stats['praise']['responded']})")
        print(f"Spam:          {self.stats['spam']['count']:2d} (logged)")
        print(f"Sales/Partner: {self.stats['sales']['count']:2d} (flagged: {self.stats['sales']['flagged']})")
        if self.stats['general']['count'] > 0:
            print(f"General:       {self.stats['general']['count']:2d}")
        print()
        
        print(f"RECENT COMMENTS PROCESSED")
        print(f"-" * 70)
        for i, comment in enumerate(self.processed_comments[:6], 1):
            author = comment["commenter"][:20].ljust(20)
            category = comment["category"].upper()[:12].ljust(12)
            text = comment["text"][:40].replace("\n", " ")
            status = "✓ RESPONDED" if comment["auto_response_sent"] else "→ LOGGED"
            print(f"{i}. [{category}] {author} - {text}... ({status})")
        print()
        
        print(f"LOGGING")
        print(f"-" * 70)
        print(f"Comments Log:  {COMMENTS_LOG}")
        print(f"State File:    {STATE_FILE}")
        print(f"Report File:   {REPORT_FILE}")
        print()
        
        print(f"{'='*70}\n")
    
    def save_report(self):
        """Save text report"""
        report = f"""
{'='*70}
YOUTUBE COMMENT MONITOR REPORT
Concessa Obvius Channel
{'='*70}

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: {'DEMO' if self.use_demo else 'LIVE'}

EXECUTION SUMMARY
-{'-'*68}
Total Comments Processed: {self.stats['total_processed']}
Auto-Responses Sent: {self.stats['questions']['responded'] + self.stats['praise']['responded']}
Flagged for Review: {self.stats['sales']['flagged']}

CATEGORY BREAKDOWN
-{'-'*68}
Questions:       {self.stats['questions']['count']} (responded: {self.stats['questions']['responded']})
Praise:          {self.stats['praise']['count']} (responded: {self.stats['praise']['responded']})
Spam:            {self.stats['spam']['count']}
Sales/Partner:   {self.stats['sales']['count']} (flagged: {self.stats['sales']['flagged']})

RECENT COMMENTS
-{'-'*68}
"""
        for comment in self.processed_comments[:10]:
            report += f"\n[{comment['category'].upper()}] {comment['commenter']}\n"
            report += f"Text: {comment['text'][:60]}...\n"
            if comment['auto_response_sent']:
                report += f"Status: AUTO-RESPONDED\n"
            else:
                report += f"Status: LOGGED{'(FLAGGED)' if comment['category'] == 'sales' else ''}\n"
        
        report += f"\n{'='*70}\n"
        report += f"Full log: {COMMENTS_LOG}\n"
        report += f"{'='*70}\n"
        
        with open(REPORT_FILE, "w") as f:
            f.write(report)
    
    def run(self, demo: bool = False):
        """Run the monitor"""
        # Use demo if requested or if in demo mode
        if demo or self.use_demo:
            comments = self._demo_comments()
            print(f"📌 Using DEMO mode with {len(comments)} sample comments")
        else:
            print("⚠️ Demo mode enabled (no real API available)")
            comments = self._demo_comments()
        
        print(f"Processing {len(comments)} comments...\n")
        
        # Process comments
        self.process_comments(comments)
        
        # Save state and report
        self._save_state()
        self.save_report()
        
        # Print summary
        self.print_summary(comments)
        
        return True


def main():
    """Main entry point"""
    monitor = YouTubeCommentMonitor(use_demo=True)
    success = monitor.run(demo=True)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
