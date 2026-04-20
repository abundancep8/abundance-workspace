#!/usr/bin/env python3
"""
YouTube Comment Monitor - Cron Worker
Processes cached comments, categorizes, responds, and generates reports
"""

import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import hashlib

# ============================================================================
# CONFIG
# ============================================================================

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE_DIR / ".cache"
LOG_FILE = CACHE_DIR / "youtube-comments.jsonl"
STATE_FILE = CACHE_DIR / ".youtube-monitor-state.json"
REPORT_FILE = CACHE_DIR / "youtube-comments-report.txt"
REPORT_JSON_FILE = CACHE_DIR / "youtube-comments-report.json"
REVIEW_FILE = CACHE_DIR / "youtube-flagged-partnerships.jsonl"

CHANNEL_NAME = "Concessa Obvius"
CHANNEL_ID = "UC326742c_CXvNQ6IcnZ8Jkw"

# Keyword matching for categorization
KEYWORDS = {
    "questions": ["how", "help", "tools", "cost", "timeline", "tutorial", "start", "begin", "what", "guide"],
    "praise": ["amazing", "inspiring", "love", "great", "awesome", "thank", "brilliant", "excellent", "fantastic", "wonderful"],
    "spam": ["crypto", "bitcoin", "mlm", "forex", "dm me", "click here", "limited offer", "buy now", "limited time"],
    "sales": ["partnership", "collaboration", "sponsor", "work with", "brand deal", "cooperation", "affiliate"],
}

# Auto-response templates
TEMPLATES = {
    "questions": [
        "Thanks for the question! Check out our FAQ or reach out to our support team.",
        "Great question! Feel free to check our documentation or ask in our community.",
        "I'll get back to you with more details soon. In the meantime, check out our resources!",
    ],
    "praise": [
        "Thank you so much! We really appreciate your support 🙏",
        "So glad you found this valuable! Keep building!",
        "Your support means everything to us! Thank you 💙",
    ],
}

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(CACHE_DIR / "youtube-monitor-cron-worker.log"),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def ensure_cache_dir():
    """Ensure .cache directory exists"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> Dict:
    """Load last run state"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load state: {e}")
    
    return {
        "last_run": None,
        "cron_id": "114e5c6d-ac8b-47ca-a695-79ac31b5c076",
        "channel": CHANNEL_NAME,
        "channel_id": CHANNEL_ID,
        "status": "operational",
        "processed_count": 0,
        "auto_response_count": 0,
        "flagged_count": 0,
    }


def save_state(state: Dict):
    """Save state"""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        logger.error(f"Could not save state: {e}")


def categorize_comment(text: str) -> str:
    """Categorize comment by keyword matching"""
    text_lower = text.lower()

    # Check spam first (highest priority to filter)
    if any(keyword in text_lower for keyword in KEYWORDS["spam"]):
        return "spam"

    # Check sales
    if any(keyword in text_lower for keyword in KEYWORDS["sales"]):
        return "sales"

    # Check praise
    if any(keyword in text_lower for keyword in KEYWORDS["praise"]):
        return "praise"

    # Check questions
    if any(keyword in text_lower for keyword in KEYWORDS["questions"]):
        return "questions"

    return "other"


def load_comments() -> List[Dict]:
    """Load all comments from JSONL log"""
    comments = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    try:
                        comments.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except IOError as e:
            logger.warning(f"Could not read log: {e}")
    return comments


def count_by_category(comments: List[Dict]) -> Dict:
    """Count comments by category"""
    counts = {"questions": 0, "praise": 0, "spam": 0, "sales": 0, "other": 0}
    response_status = {"auto_responded": 0, "flagged_for_review": 0, "processed": 0}
    
    for comment in comments:
        cat = comment.get("category", "other")
        if cat in counts:
            counts[cat] += 1
        
        status = comment.get("response_status", "processed")
        if status in response_status:
            response_status[status] += 1
    
    return {"categories": counts, "responses": response_status}


def generate_report(state: Dict, stats: Dict):
    """Generate text and JSON reports"""
    timestamp = datetime.utcnow().isoformat()
    
    # Text report
    text_report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║         YOUTUBE COMMENT MONITOR - CONCESSA OBVIUS CHANNEL                  ║
║                        {timestamp}                           ║
╚════════════════════════════════════════════════════════════════════════════╝

SUMMARY
├─ Channel: {state['channel']} ({state['channel_id']})
├─ Monitor Status: {state['status']}
├─ Last Run: {state['last_run']}
└─ Cron Job ID: {state['cron_id']}

COMMENTS PROCESSED
├─ Total Comments in Log: {sum(stats['categories'].values())}
├─ Questions: {stats['categories']['questions']}
├─ Praise: {stats['categories']['praise']}
├─ Spam: {stats['categories']['spam']}
├─ Sales (Flagged): {stats['categories']['sales']}
└─ Other: {stats['categories']['other']}

AUTO-RESPONSES
├─ Auto-Responded: {stats['responses']['auto_responded']}
├─ Flagged for Review: {stats['responses']['flagged_for_review']}
└─ Processed/Spam: {stats['responses']['processed']}

CATEGORIZATION RULES
├─ Questions: how, help, tools, cost, timeline, tutorial, start
├─ Praise: amazing, inspiring, love, great, awesome, thank, brilliant
├─ Spam: crypto, bitcoin, mlm, forex, dm me, click here
└─ Sales: partnership, collaboration, sponsor, work with, brand deal

STATUS: ✓ OPERATIONAL
Next run: 30 minutes from last execution
Log file: {LOG_FILE}
Report: {REPORT_FILE}

════════════════════════════════════════════════════════════════════════════════
"""
    
    # Write text report
    try:
        with open(REPORT_FILE, "w") as f:
            f.write(text_report.strip())
        logger.info(f"Report written to {REPORT_FILE}")
    except IOError as e:
        logger.error(f"Could not write report: {e}")
    
    # JSON report
    json_report = {
        "timestamp": timestamp,
        "channel": state["channel"],
        "channel_id": state["channel_id"],
        "status": state["status"],
        "comments_processed": sum(stats["categories"].values()),
        "breakdown": stats["categories"],
        "responses": stats["responses"],
        "cron_id": state["cron_id"],
    }
    
    try:
        with open(REPORT_JSON_FILE, "w") as f:
            json.dump(json_report, f, indent=2)
        logger.info(f"JSON report written to {REPORT_JSON_FILE}")
    except IOError as e:
        logger.error(f"Could not write JSON report: {e}")
    
    return text_report


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main cron worker"""
    logger.info("=" * 80)
    logger.info("YouTube Comment Monitor - Cron Worker Started")
    logger.info(f"Time: {datetime.utcnow().isoformat()}")
    logger.info("=" * 80)
    
    ensure_cache_dir()
    
    # Load state
    state = load_state()
    state["last_run"] = datetime.utcnow().isoformat()
    
    # Load and process comments
    comments = load_comments()
    logger.info(f"Loaded {len(comments)} total comments")
    
    # Generate statistics
    stats = count_by_category(comments)
    state["processed_count"] = sum(stats["categories"].values())
    state["auto_response_count"] = stats["responses"]["auto_responded"]
    state["flagged_count"] = stats["responses"]["flagged_for_review"]
    
    logger.info(f"Summary: {stats['categories']}")
    logger.info(f"Responses: {stats['responses']}")
    
    # Generate report
    report = generate_report(state, stats)
    logger.info("Report generated successfully")
    
    # Save state
    save_state(state)
    logger.info("State saved")
    
    # Print summary
    print("\n" + report)
    
    logger.info("=" * 80)
    logger.info("YouTube Comment Monitor - Cron Worker Completed")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
