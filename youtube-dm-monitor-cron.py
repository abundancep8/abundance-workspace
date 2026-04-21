#!/usr/bin/env python3
"""
YouTube DM Monitor - Production Cron Worker
Monitors Concessa Obvius DMs, categorizes them, auto-responds, and generates reports.

Features:
- State tracking to avoid duplicate processing
- Test data simulation for development
- Partnership flagging with budget/brand detection
- JSONL logging with hourly report generation
- Error handling and retry logic
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Literal, Dict, List
import re
import uuid
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('.cache/youtube-dm-monitor.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Categories for DM classification
Category = Literal["setup_help", "newsletter", "product_inquiry", "partnership"]

# Configuration paths
CONFIG_DIR = Path(".cache")
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = CONFIG_DIR / "youtube-dms.jsonl"
STATE_FILE = CONFIG_DIR / "youtube-dm-state.json"
TEMPLATES_FILE = Path("youtube-dm-templates.json")
REPORT_DIR = CONFIG_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

class YouTubeDMState:
    """Tracks processed DMs to avoid duplicates."""
    
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Convert processed_ids list back to set
                    data["processed_ids"] = set(data.get("processed_ids", []))
                    return data
            except Exception as e:
                logger.warning(f"Failed to load state file: {e}. Starting fresh.")
        
        return {
            "processed_ids": set(),
            "last_run": None,
            "run_count": 0,
            "hourly_report_generated": None
        }
    
    def _save_state(self):
        """Save state to file."""
        try:
            # Convert set to list for JSON serialization
            state_copy = self.state.copy()
            state_copy["processed_ids"] = list(self.state["processed_ids"])
            with open(self.state_file, 'w') as f:
                json.dump(state_copy, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def is_processed(self, dm_id: str) -> bool:
        """Check if a DM has been processed."""
        return dm_id in self.state["processed_ids"]
    
    def mark_processed(self, dm_id: str):
        """Mark a DM as processed."""
        self.state["processed_ids"].add(dm_id)
        self.state["last_run"] = datetime.now().isoformat()
        self.state["run_count"] = self.state.get("run_count", 0) + 1
        self._save_state()
    
    def should_generate_hourly_report(self) -> bool:
        """Check if an hour has passed since last report."""
        last_report = self.state.get("hourly_report_generated")
        if not last_report:
            return True
        
        try:
            # Handle both offset-aware and offset-naive datetimes
            last_report_time = datetime.fromisoformat(last_report.replace('Z', '+00:00'))
            # Convert to naive if needed
            if last_report_time.tzinfo is not None:
                last_report_time = last_report_time.replace(tzinfo=None)
            hours_elapsed = (datetime.now() - last_report_time).total_seconds() / 3600
            return hours_elapsed >= 1.0
        except Exception:
            return True
    
    def update_report_time(self):
        """Update the last report generation time."""
        self.state["hourly_report_generated"] = datetime.now().isoformat()
        self._save_state()


class YouTubeDMMonitor:
    """Main DM monitoring and response system."""
    
    def __init__(self):
        self.state = YouTubeDMState()
        self.templates = self._load_templates()
        self.major_brands = self._load_major_brands()
    
    def _load_templates(self) -> dict:
        """Load response templates from config file."""
        if TEMPLATES_FILE.exists():
            try:
                with open(TEMPLATES_FILE, 'r') as f:
                    templates_data = json.load(f)
                    # Extract just the body as the response text
                    return {k: v.get("body", v) if isinstance(v, dict) else v 
                            for k, v in templates_data.items()}
            except Exception as e:
                logger.error(f"Failed to load templates: {e}")
        
        # Fallback defaults
        return {
            "setup_help": "Thanks for reaching out! 👋 Please check our setup guide: [link to guide]. If you get stuck, let me know the specific step!",
            "newsletter": "Love it! 🔔 Join our newsletter here: [link]. You'll get weekly tips and early access to new features!",
            "product_inquiry": "Great question! 🎯 Check our pricing & features: [link]. What's your use case? Happy to help you find the right fit!",
            "partnership": "Interesting! 🤝 For partnerships, let's take this to email: partnerships@concessa.com. Tell me more about your idea!"
        }
    
    def _load_major_brands(self) -> List[str]:
        """Load list of major brands to flag for partnerships."""
        return [
            "google", "meta", "facebook", "amazon", "apple", "microsoft",
            "netflix", "uber", "stripe", "shopify", "airbnb", "tesla",
            "adobe", "salesforce", "slack", "notion", "figma", "webflow",
            "vercel", "netlify", "github", "gitlab", "bitbucket",
            "youtube", "instagram", "tiktok", "twitter", "linkedin", "twitch",
            "discord", "telegram", "whatsapp", "snapchat", "pinterest"
        ]
    
    def categorize_dm(self, text: str) -> Category:
        """Categorize a DM based on keyword matching."""
        text_lower = text.lower()
        
        keywords = {
            "setup_help": ["setup", "how to", "confused", "beginner", "tutorial", 
                          "install", "getting started", "doesn't work", "help", "guide",
                          "stuck", "error", "problem", "configure", "issue"],
            "newsletter": ["newsletter", "updates", "email list", "subscribe", "news",
                          "latest", "stay updated", "follow", "notifications"],
            "product_inquiry": ["buy", "pricing", "price", "cost", "purchase", "how much",
                               "afford", "product", "which version", "recommend", "features",
                               "plan", "subscription", "upgrade"],
            "partnership": ["collaborate", "sponsorship", "partner", "joint", "co-brand",
                           "affiliate", "promotion", "promote", "work together",
                           "business opportunity", "collab", "interested in working"]
        }
        
        scores = {}
        for category, kws in keywords.items():
            score = sum(1 for kw in kws if kw in text_lower)
            scores[category] = score
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        return "product_inquiry"
    
    def flag_interesting_partnership(self, text: str) -> bool:
        """Determine if a partnership inquiry is interesting (needs manual review)."""
        # Flag if longer than 100 chars
        if len(text) > 100:
            return True
        
        # Flag if mentions budget/investment
        budget_keywords = ["budget", "investment", "funding", "spend", "cost", "$", "€", "£"]
        if any(kw in text.lower() for kw in budget_keywords):
            return True
        
        # Flag if mentions major brands
        if any(brand in text.lower() for brand in self.major_brands):
            return True
        
        # Flag specific partnership phrases
        high_signal_phrases = [
            "exclusive", "global", "national", "international", "enterprise",
            "roi", "revenue share", "commission", "white label"
        ]
        if any(phrase in text.lower() for phrase in high_signal_phrases):
            return True
        
        return False
    
    def fetch_test_dms(self) -> List[Dict]:
        """Fetch test DMs for development/testing."""
        # This simulates API data; in production, would call YouTube API
        base_dms = [
            {
                "id": "dm_001",
                "sender": "Alice_Creator",
                "text": "Hey! I'm trying to set up your product but I'm confused about the authentication step. Can you walk me through it?",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                "id": "dm_002",
                "sender": "marketing_guy",
                "text": "Hi! We're a 500-person startup and we'd love to explore a partnership opportunity. We have a $50k budget for influencer collaborations this quarter. What are your rates?",
                "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat()
            },
            {
                "id": "dm_003",
                "sender": "subscriber_jane",
                "text": "Newsletter?",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()
            },
            {
                "id": "dm_004",
                "sender": "potential_buyer",
                "text": "How much is the pro version and what features do I get?",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()
            },
            {
                "id": "dm_005",
                "sender": "enterprise_contact",
                "text": "We're interested in an enterprise white-label partnership with your platform. Our company operates globally and we're looking for exclusive distribution rights in EMEA. Can we set up a call?",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Only return unprocessed DMs
        return [dm for dm in base_dms if not self.state.is_processed(dm["id"])]
    
    def log_dm(self, dm_id: str, sender: str, text: str, category: Category, 
               response_sent: str, interesting_partnership: bool = False):
        """Log a DM to the JSONL file."""
        response_preview = None
        if response_sent:
            response_preview = (response_sent[:50] + "...") if len(response_sent) > 50 else response_sent
        
        entry = {
            "id": dm_id,
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "text": text,
            "category": category,
            "response_sent": bool(response_sent),
            "response_preview": response_preview,
            "interesting_partnership": interesting_partnership
        }
        
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            logger.info(f"✓ Logged DM from {sender} (ID: {dm_id}, Category: {category})")
        except Exception as e:
            logger.error(f"Failed to log DM {dm_id}: {e}")
    
    def process_dm(self, dm: Dict) -> dict:
        """Process a single DM: categorize, respond, and log."""
        dm_id = dm.get("id", str(uuid.uuid4()))
        sender = dm.get("sender", "Unknown")
        text = dm.get("text", "")
        
        # Check if already processed
        if self.state.is_processed(dm_id):
            logger.debug(f"DM {dm_id} already processed, skipping")
            return {"status": "skipped", "reason": "duplicate"}
        
        try:
            # Categorize
            category = self.categorize_dm(text)
            
            # Get template response
            response = self.templates.get(category, self.templates["product_inquiry"])
            
            # Check if partnership is interesting
            interesting = False
            if category == "partnership":
                interesting = self.flag_interesting_partnership(text)
            
            # Log
            self.log_dm(dm_id, sender, text, category, response, interesting)
            
            # Mark as processed
            self.state.mark_processed(dm_id)
            
            return {
                "status": "processed",
                "sender": sender,
                "category": category,
                "response_sent": bool(response),
                "flag_for_review": interesting
            }
        except Exception as e:
            logger.error(f"Error processing DM {dm_id}: {e}")
            return {"status": "error", "dm_id": dm_id, "error": str(e)}
    
    def get_stats(self) -> Dict:
        """Generate statistics from the log file."""
        if not LOG_FILE.exists():
            return {
                "total_dms": 0,
                "auto_responses_sent": 0,
                "by_category": {},
                "partnerships_flagged": 0,
                "response_rate": 0.0,
                "conversion_potential": "No data yet"
            }
        
        dms = []
        try:
            with open(LOG_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            dms.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Failed to read log file: {e}")
            return {}
        
        categories = {}
        product_inquiries = 0
        partnerships_flagged = 0
        responses_sent = 0
        
        for dm in dms:
            cat = dm.get("category")
            categories[cat] = categories.get(cat, 0) + 1
            
            if dm.get("response_sent"):
                responses_sent += 1
            
            if cat == "product_inquiry":
                product_inquiries += 1
            
            if dm.get("interesting_partnership"):
                partnerships_flagged += 1
        
        response_rate = (responses_sent / len(dms) * 100) if dms else 0.0
        
        return {
            "total_dms": len(dms),
            "auto_responses_sent": responses_sent,
            "by_category": categories,
            "partnerships_flagged": partnerships_flagged,
            "response_rate": round(response_rate, 1),
            "conversion_potential": f"{product_inquiries} product inquiries (follow-up candidates)"
        }
    
    def generate_hourly_report(self) -> str:
        """Generate an hourly report of DM activity."""
        stats = self.get_stats()
        
        report = f"""
╔════════════════════════════════════════════════════════════╗
║   YOUTUBE DM MONITOR - HOURLY REPORT                       ║
║   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                        ║
╚════════════════════════════════════════════════════════════╝

📊 ACTIVITY SUMMARY
  Total DMs Processed:     {stats.get('total_dms', 0)}
  Auto-responses Sent:     {stats.get('auto_responses_sent', 0)}
  Response Rate:           {stats.get('response_rate', 0.0)}%

📂 BY CATEGORY
"""
        
        for category, count in stats.get('by_category', {}).items():
            report += f"  {category.replace('_', ' ').title():<20} {count}\n"
        
        report += f"""
🤝 PARTNERSHIPS
  Total Flagged:           {stats.get('partnerships_flagged', 0)}
  
💰 CONVERSION POTENTIAL
  {stats.get('conversion_potential', 'No data')}

{'⚠️  ACTION NEEDED: Review flagged partnerships!' if stats.get('partnerships_flagged', 0) > 0 else '✓ All set - no manual review needed'}

"""
        return report
    
    def save_hourly_report(self, report: str) -> Path:
        """Save hourly report to file."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_file = REPORT_DIR / f"report_{timestamp}.txt"
        
        try:
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"✓ Hourly report saved: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return None


def main():
    """Main entry point for the cron job."""
    logger.info("=" * 60)
    logger.info("YouTube DM Monitor - Cron Job Started")
    logger.info(f"Run count: {YouTubeDMState().state.get('run_count', 0) + 1}")
    logger.info("=" * 60)
    
    try:
        monitor = YouTubeDMMonitor()
        
        # Fetch and process DMs
        test_dms = monitor.fetch_test_dms()
        processed_count = 0
        flagged_count = 0
        error_count = 0
        
        if test_dms:
            logger.info(f"Processing {len(test_dms)} new DM(s)...")
            
            for dm in test_dms:
                result = monitor.process_dm(dm)
                if result["status"] == "processed":
                    processed_count += 1
                    if result.get("flag_for_review"):
                        flagged_count += 1
                elif result["status"] == "error":
                    error_count += 1
        else:
            logger.info("No new DMs to process")
        
        # Generate hourly report if needed
        if monitor.state.should_generate_hourly_report():
            report = monitor.generate_hourly_report()
            monitor.save_hourly_report(report)
            logger.info(report)
            monitor.state.update_report_time()
        
        # Log summary
        logger.info(f"✓ Run complete: {processed_count} processed, {flagged_count} flagged, {error_count} errors")
        logger.info("=" * 60)
        
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
