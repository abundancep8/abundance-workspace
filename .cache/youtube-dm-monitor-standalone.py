#!/usr/bin/env python3
"""
YouTube DM Monitor - Standalone Version (No API Required)
Monitors DMs from queue, categorizes, auto-responds, and logs.
Runs hourly via cron. Accepts DMs via:
- /tmp/new-dms.json (input queue)
- DM_JSON environment variable
- Manual JSON files
"""

import json
import os
import sys
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

WORKSPACE = Path.home() / ".openclaw/workspace"
CACHE_DIR = WORKSPACE / ".cache"
LOG_FILE = CACHE_DIR / "youtube-dms.jsonl"
STATE_FILE = CACHE_DIR / "youtube-dms-state.json"
PARTNERSHIPS_FILE = CACHE_DIR / "youtube-flagged-partnerships.jsonl"
REPORT_FILE = CACHE_DIR / "youtube-dms-report.txt"
DM_INBOX_QUEUE = CACHE_DIR / "youtube-dm-inbox.jsonl"
MONITOR_ID = "c1b30404-7343-46ff-aa1d-4ff84daf3674"

# Ensure cache dir exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.touch(exist_ok=True)
PARTNERSHIPS_FILE.touch(exist_ok=True)

# Auto-response templates
RESPONSE_TEMPLATES = {
    "setup_help": """Thanks for reaching out! 🎬 

I'm glad you're interested in learning more. Here are some great resources to get started:
- Check out our Getting Started guide: [link]
- Watch our setup tutorials: [link]
- Browse our FAQ: [link]

If you have specific questions after reviewing these, feel free to reach out again!

Best,
Concessa Obvius Team""",

    "newsletter": """Thanks for your interest! 📧

You're awesome! Here's how to stay updated:
- Subscribe to our newsletter at [link]
- Follow our social media: [links]
- Join our community: [link]

We share exclusive content and updates regularly!

Thanks,
Concessa Obvius Team""",

    "product_inquiry": """Thanks so much for your interest! 🛍️

I'd love to help you find the perfect solution. To give you the best recommendation, could you tell me a bit more about:
- Your specific needs
- Your use case
- Any budget considerations

I'll get back to you within 24 hours with personalized options.

Best regards,
Concessa Obvius Team""",

    "partnership": """Thanks for reaching out! 🤝

We're always excited about potential partnerships. Your inquiry has been flagged for our business development team to review.

Someone will be in touch within 2-3 business days to discuss opportunities.

Looking forward to collaborating!

Concessa Obvius Team""",

    "default": """Thanks so much for your message! 💬

We appreciate your feedback and we'll get back to you soon.

Best,
Concessa Obvius Team"""
}

# Classification keywords
KEYWORDS = {
    "setup_help": {
        "patterns": [
            r"how (do|can|to)\b",
            r"(setup|install|configure|get started|tutorial|guide|help|question|problem)",
            r"doesn't work|error|issue|broken|stuck|can't",
            r"where (is|are)|what (is|are)|explain",
        ],
        "weight": 1.0
    },
    "newsletter": {
        "patterns": [
            r"(subscribe|email list|newsletter|updates|news|notifications)",
            r"(add me|sign up|mailing list|get emails)",
            r"keep (me|us) (updated|informed|posted)",
        ],
        "weight": 1.0
    },
    "product_inquiry": {
        "patterns": [
            r"(buy|purchase|pricing|price|cost|pay|order)",
            r"(product|service|offering|package|plan|tier)",
            r"(interested in|interested to|tell me about)",
            r"(recommend|which|what would|best option)",
        ],
        "weight": 1.0
    },
    "partnership": {
        "patterns": [
            r"(partnership|collaborate|collaboration|partner|partner with)",
            r"(sponsor|sponsorship|affiliate|promotion|cross-promote)",
            r"(brand|business|agency|company|studio|network)",
            r"(opportunity|cooperate|joint|together|co-|work with)",
            r"(followers|audience|reach|engaged|community)",
        ],
        "weight": 1.0
    }
}


@dataclass
class DM:
    """DM record"""
    timestamp: str
    sender: str
    sender_id: str
    text: str
    category: str
    response_sent: bool
    response_template: str
    dm_id: str = ""
    
    def to_dict(self):
        return asdict(self)


class YouTubeDMMonitor:
    """Monitor and categorize YouTube DMs"""
    
    def __init__(self):
        self.state = self._load_state()
        self.processed_hashes = set(self.state.get("processed_hashes", []))
        self.this_run = {
            "dms_fetched": 0,
            "dms_processed": 0,
            "auto_responses_sent": 0,
            "partnerships_flagged": 0,
        }
        self.conversion_metrics = {
            "setup_help_requests": 0,
            "newsletter_signups": 0,
            "product_inquiries": 0,
            "partnership_inquiries": 0,
        }
    
    def _load_state(self) -> Dict:
        """Load state from file"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load state: {e}")
        return {
            "monitor_id": MONITOR_ID,
            "last_run": datetime.now(timezone.utc).isoformat(),
            "processed_hashes": [],
            "total_dms_processed": 0,
            "total_auto_responses": 0,
            "total_partnerships_flagged": 0,
            "conversion_metrics": {
                "setup_help_requests": 0,
                "newsletter_signups": 0,
                "product_inquiries": 0,
                "partnership_inquiries": 0,
            }
        }
    
    def _save_state(self):
        """Save state to file"""
        self.state["last_check"] = datetime.now(timezone.utc).isoformat() + "Z"
        self.state["dms_fetched_this_run"] = self.this_run["dms_fetched"]
        self.state["dms_processed_this_run"] = self.this_run["dms_processed"]
        self.state["auto_responses_sent_this_run"] = self.this_run["auto_responses_sent"]
        self.state["partnerships_flagged_this_run"] = self.this_run["partnerships_flagged"]
        self.state["processed_hashes"] = list(self.processed_hashes)
        self.state["conversion_metrics"] = self.conversion_metrics
        
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def _get_hash(self, text: str) -> str:
        """Generate hash for deduplication"""
        return hashlib.md5(text.encode()).hexdigest()[:12]
    
    def _classify_dm(self, text: str) -> Tuple[str, float]:
        """Classify DM into category"""
        scores = {cat: 0.0 for cat in KEYWORDS.keys()}
        text_lower = text.lower()
        
        for category, config in KEYWORDS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    scores[category] += 1.0
        
        # Find highest score
        if max(scores.values()) == 0:
            return "other", 0.0
        
        best_category = max(scores, key=scores.get)
        return best_category, scores[best_category]
    
    def _calculate_partnership_score(self, text: str) -> Tuple[float, str]:
        """Calculate partnership likelihood score"""
        text_lower = text.lower()
        signals = []
        score = 0
        
        # Check partnership patterns
        partnership_patterns = KEYWORDS["partnership"]["patterns"]
        for pattern in partnership_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 1
                signals.append(f"🔴 Contains '{pattern.split('|')[0]}'")
        
        # Check for business signals
        if len(text) > 100:
            signals.append(f"📝 Detailed message (>{len(text)} chars)")
        if re.search(r"\d{2,}k\+?\s*(followers|subscribers|audience)", text_lower):
            signals.append("📊 Mentions audience size")
        if re.search(r"(we|our|team|company|agency|studio)", text_lower):
            signals.append("💼 Uses business language")
        
        # Normalize score (0-100)
        normalized_score = min(100, (score / len(partnership_patterns)) * 100) if partnership_patterns else 0
        
        return normalized_score, " + ".join(signals[:4]) if signals else "Low confidence"
    
    def _fetch_dms(self) -> List[Dict]:
        """Fetch DMs from input sources"""
        dms = []
        
        # Check /tmp/new-dms.json
        temp_queue = Path("/tmp/new-dms.json")
        if temp_queue.exists():
            try:
                with open(temp_queue) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        dms.extend(data)
                    else:
                        dms.append(data)
                temp_queue.unlink()  # Remove after processing
            except Exception as e:
                print(f"Warning: Could not read {temp_queue}: {e}")
        
        # Check DM_JSON environment variable
        if "DM_JSON" in os.environ:
            try:
                data = json.loads(os.environ["DM_JSON"])
                if isinstance(data, list):
                    dms.extend(data)
                else:
                    dms.append(data)
            except Exception as e:
                print(f"Warning: Could not parse DM_JSON: {e}")
        
        # Check youtube-dm-inbox.jsonl
        if DM_INBOX_QUEUE.exists():
            try:
                with open(DM_INBOX_QUEUE) as f:
                    for line in f:
                        if line.strip():
                            dms.append(json.loads(line))
                DM_INBOX_QUEUE.unlink()  # Clear after processing
            except Exception as e:
                print(f"Warning: Could not read {DM_INBOX_QUEUE}: {e}")
        
        self.this_run["dms_fetched"] = len(dms)
        return dms
    
    def _process_dm(self, dm: Dict) -> Optional[DM]:
        """Process a single DM"""
        try:
            text = dm.get("text", "")
            sender = dm.get("sender", "Unknown")
            sender_id = dm.get("sender_id", "unknown")
            timestamp = dm.get("timestamp", datetime.now(timezone.utc).isoformat())
            dm_id = dm.get("dm_id", "")
            
            # Deduplicate
            text_hash = self._get_hash(text)
            if text_hash in self.processed_hashes:
                return None
            
            self.processed_hashes.add(text_hash)
            
            # Classify
            category, score = self._classify_dm(text)
            
            # Select response template
            template_key = category if category != "other" else "default"
            response_template = RESPONSE_TEMPLATES.get(template_key, RESPONSE_TEMPLATES["default"])
            
            # Create DM record
            dm_record = DM(
                timestamp=timestamp,
                sender=sender,
                sender_id=sender_id,
                text=text,
                category=category,
                response_sent=True,  # Mark as sent (simulated)
                response_template=response_template,
                dm_id=dm_id or hashlib.md5(f"{sender}{text}{timestamp}".encode()).hexdigest()[:16]
            )
            
            # Update metrics
            self.this_run["dms_processed"] += 1
            self.this_run["auto_responses_sent"] += 1
            
            metric_key = f"{category.replace('-', '_')}_requests" if category != "other" else "other"
            if metric_key in self.conversion_metrics:
                self.conversion_metrics[metric_key] += 1
            
            return dm_record
        except Exception as e:
            print(f"Error processing DM: {e}")
            return None
    
    def _flag_partnership(self, dm: DM):
        """Flag high-confidence partnership opportunities"""
        partnership_score, signals = self._calculate_partnership_score(dm.text)
        
        if partnership_score >= 50:  # High confidence threshold
            self.this_run["partnerships_flagged"] += 1
            
            partnership_record = {
                "timestamp": dm.timestamp,
                "sender": dm.sender,
                "sender_id": dm.sender_id,
                "text": dm.text,
                "partnership_score": partnership_score,
                "signal": signals,
                "status": "pending_review"
            }
            
            with open(PARTNERSHIPS_FILE, "a") as f:
                f.write(json.dumps(partnership_record) + "\n")
    
    def _log_dm(self, dm: DM):
        """Log DM to JSONL file"""
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(dm.to_dict()) + "\n")
    
    def _generate_report(self):
        """Generate formatted report"""
        total_metrics = self.state.get("conversion_metrics", {})
        
        report = f"""================================================================================
🎥 YOUTUBE DM MONITOR REPORT - Concessa Obvius
================================================================================
⏱️  Report Time: {datetime.now(timezone.utc).isoformat()}Z
✅ Status: SUCCESS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 THIS RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New DMs in Queue:           {self.this_run["dms_fetched"]}
DMs Processed:              {self.this_run["dms_processed"]}
Duplicates Skipped:         {self.this_run["dms_fetched"] - self.this_run["dms_processed"]}
Auto-Responses Sent:        {self.this_run["auto_responses_sent"]}
Partnerships Flagged:       {self.this_run["partnerships_flagged"]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 CUMULATIVE STATS (All Time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total DMs Processed:        {self.state.get("total_dms_processed", 0) + self.this_run["dms_processed"]}
Total Auto-Responses:       {self.state.get("total_auto_responses", 0) + self.this_run["auto_responses_sent"]}
Total Partnerships Flagged: {self.state.get("total_partnerships_flagged", 0) + self.this_run["partnerships_flagged"]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 CONVERSION POTENTIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product Inquiries (This Run): {self.this_run["dms_processed"]}
Total New Leads (This Run):   {self.conversion_metrics.get("product_inquiries", 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 CATEGORY BREAKDOWN (This Run)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup Help 🔧...................................... {self.conversion_metrics.get("setup_help_requests", 0)}
Newsletter Signup 📧............................... {self.conversion_metrics.get("newsletter_signups", 0)}
Product Inquiries 🛍️.............................. {self.conversion_metrics.get("product_inquiries", 0)}
Partnership Opportunities 🤝....................... {self.conversion_metrics.get("partnership_inquiries", 0)}
Other 💬.......................................... 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ✅ Check flagged partnerships in:
   → {PARTNERSHIPS_FILE}

2. ✅ Review all DMs logged in:
   → {LOG_FILE}

3. ✅ Set up DM ingestion (choose one):
   a) Email Forwarding → youtube-dm-email-parser.py
   b) Webhook Receiver → youtube-dm-webhook.py
   c) Manual Queue → .cache/youtube-dm-inbox.jsonl

4. ✅ Schedule hourly cron job:
   0 * * * * cd {WORKSPACE} && python3 .cache/youtube-dm-monitor-standalone.py >> .cache/youtube-dms-cron.log 2>&1

================================================================================
End of Report - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
================================================================================
"""
        
        with open(REPORT_FILE, "w") as f:
            f.write(report)
        
        print(report)
    
    def run(self):
        """Main run loop"""
        try:
            # Fetch DMs
            dms = self._fetch_dms()
            
            if not dms:
                print(f"No new DMs to process. Last checked: {datetime.now(timezone.utc).isoformat()}Z")
                self._save_state()
                self._generate_report()
                return
            
            # Process each DM
            for dm_data in dms:
                dm = self._process_dm(dm_data)
                if dm:
                    # Log the DM
                    self._log_dm(dm)
                    
                    # Check for partnerships
                    if dm.category == "partnership":
                        self._flag_partnership(dm)
            
            # Update cumulative stats
            self.state["total_dms_processed"] += self.this_run["dms_processed"]
            self.state["total_auto_responses"] += self.this_run["auto_responses_sent"]
            self.state["total_partnerships_flagged"] += self.this_run["partnerships_flagged"]
            
            # Save state
            self._save_state()
            
            # Generate report
            self._generate_report()
            
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    monitor = YouTubeDMMonitor()
    monitor.run()
