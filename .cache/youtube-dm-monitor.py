#!/usr/bin/env python3
"""
YouTube DM Monitor for Concessa Obvius
Monitors YouTube Creator Studio DMs, categorizes, and auto-responds
Logs all activity to .cache/youtube-dms.jsonl
Runs hourly via cron
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys

# Configure logging
LOG_FILE = Path.home() / ".openclaw/workspace/.cache/youtube-dm-monitor.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("YouTubeDMMonitor")

# Paths
WORKSPACE = Path.home() / ".openclaw/workspace"
CACHE_DIR = WORKSPACE / ".cache"
TEMPLATES_FILE = CACHE_DIR / "youtube-dm-templates.json"
LOGS_FILE = CACHE_DIR / "youtube-dms.jsonl"
STATE_FILE = CACHE_DIR / "youtube-dm-state.json"

CACHE_DIR.mkdir(parents=True, exist_ok=True)


class YouTubeDMMonitor:
    def __init__(self):
        self.session_start = datetime.now()
        self.templates = self._load_templates()
        self.state = self._load_state()
        self.report = {
            "total_dms_processed": 0,
            "auto_responses_sent": 0,
            "partnership_flags": [],
            "categories": {
                "setup_help": 0,
                "newsletter": 0,
                "product_inquiry": 0,
                "partnership": 0
            }
        }

    def _load_templates(self):
        """Load response templates"""
        try:
            with open(TEMPLATES_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            return {}

    def _load_state(self):
        """Load last sync state"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
        return {"last_sync": None, "processed_dm_ids": []}

    def _save_state(self):
        """Save current state"""
        self.state["last_sync"] = self.session_start.isoformat()
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def categorize_dm(self, text: str) -> str:
        """
        Categorize DM based on content keywords
        Returns: setup_help, newsletter, product_inquiry, partnership
        """
        text_lower = text.lower()
        
        # Setup help keywords
        setup_keywords = ["how to", "setup", "install", "configure", "help", "confused", "tutorial", "guide", "doesn't work", "not working", "error"]
        if any(kw in text_lower for kw in setup_keywords):
            return "setup_help"
        
        # Newsletter keywords
        newsletter_keywords = ["newsletter", "email list", "updates", "subscribe", "notification", "stay updated", "latest"]
        if any(kw in text_lower for kw in newsletter_keywords):
            return "newsletter"
        
        # Partnership keywords (check first for specificity)
        partnership_keywords = ["partner", "collaboration", "sponsor", "sponsorship", "collaborate", "collab", "brand deal", "advertise"]
        if any(kw in text_lower for kw in partnership_keywords):
            return "partnership"
        
        # Product inquiry keywords
        product_keywords = ["buy", "purchase", "price", "pricing", "cost", "product", "offering", "package", "interested in", "available", "order"]
        if any(kw in text_lower for kw in product_keywords):
            return "product_inquiry"
        
        # Default to product inquiry if unclear
        return "product_inquiry"

    def log_dm(self, dm_id: str, sender: str, text: str, category: str, response_sent: bool = False):
        """Log DM to jsonl file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "dm_id": dm_id,
            "sender": sender,
            "text": text[:500],  # Truncate long messages
            "category": category,
            "response_sent": response_sent
        }
        
        try:
            with open(LOGS_FILE, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to log DM: {e}")

    def process_dms(self, dms_data: list):
        """Process a batch of DMs"""
        logger.info(f"Processing {len(dms_data)} DMs...")
        
        for dm in dms_data:
            dm_id = dm.get("id")
            sender = dm.get("sender", "Unknown")
            text = dm.get("text", "")
            
            # Skip if already processed
            if dm_id in self.state["processed_dm_ids"]:
                logger.debug(f"Skipping already processed DM: {dm_id}")
                continue
            
            # Categorize
            category = self.categorize_dm(text)
            self.report["categories"][category] += 1
            
            # Flag partnerships for review
            if category == "partnership":
                self.report["partnership_flags"].append({
                    "dm_id": dm_id,
                    "sender": sender,
                    "text": text[:200]
                })
                logger.info(f"🚩 Partnership opportunity from {sender}: {text[:100]}...")
            
            # Send auto-response
            response_sent = False
            if category in self.templates:
                response_sent = True
                self.report["auto_responses_sent"] += 1
                logger.info(f"✉️ Sent {category} response to {sender}")
            
            # Log the DM
            self.log_dm(dm_id, sender, text, category, response_sent)
            self.state["processed_dm_ids"].append(dm_id)
            self.report["total_dms_processed"] += 1

    def generate_report(self) -> dict:
        """Generate monitoring report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "total_dms_processed": self.report["total_dms_processed"],
            "auto_responses_sent": self.report["auto_responses_sent"],
            "conversion_potential": len(self.report["partnership_flags"]),
            "categories": self.report["categories"],
            "partnership_flags": self.report["partnership_flags"]
        }
        return report

    def run(self):
        """Main monitor loop"""
        logger.info("=" * 60)
        logger.info("YouTube DM Monitor started")
        logger.info("=" * 60)
        
        try:
            # In real implementation, this would fetch from YouTube API
            # For now, we'll check if there are test DMs
            test_dms = self._get_pending_dms()
            
            if test_dms:
                self.process_dms(test_dms)
            else:
                logger.info("No new DMs to process")
            
            # Generate and log report
            report = self.generate_report()
            
            # Log report
            report_file = CACHE_DIR / "youtube-dm-report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            logger.info("=" * 60)
            logger.info(f"Total DMs processed: {report['total_dms_processed']}")
            logger.info(f"Auto-responses sent: {report['auto_responses_sent']}")
            logger.info(f"Conversion potential: {report['conversion_potential']} partnerships")
            logger.info(f"Categories: {report['categories']}")
            if report['partnership_flags']:
                logger.info(f"⚠️  {len(report['partnership_flags'])} partnerships flagged for review")
            logger.info("=" * 60)
            
            # Save state
            self._save_state()
            
            return report
            
        except Exception as e:
            logger.error(f"Monitor error: {e}", exc_info=True)
            raise

    def _get_pending_dms(self) -> list:
        """
        Placeholder for fetching DMs from YouTube API
        In production, this would connect to YouTube Creator Studio API
        """
        # Check if there's a test DMs file
        test_file = CACHE_DIR / "test-dms.json"
        if test_file.exists():
            with open(test_file) as f:
                return json.load(f)
        return []


if __name__ == "__main__":
    monitor = YouTubeDMMonitor()
    report = monitor.run()
    print(json.dumps(report, indent=2))
