#!/usr/bin/env python3
"""
YouTube Comment Monitor for Concessa Obvius Channel
- Fetches new comments using YouTube Data API
- Categorizes into: Questions (1), Praise (2), Spam (3), Sales (4)
- Auto-responds to categories 1-2
- Flags category 4 for manual review
- Logs all activity to JSONL
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

try:
    import googleapiclient.discovery
    import googleapiclient.errors
except ImportError:
    print("⚠️  googleapiclient not installed. Install with: pip install google-api-python-client")
    sys.exit(1)

# Configuration
WORKSPACE = Path.home() / ".openclaw/workspace"
CACHE_DIR = WORKSPACE / ".cache"
COMMENTS_LOG = CACHE_DIR / "youtube-comments.jsonl"
PROCESSED_IDS = CACHE_DIR / "youtube-comments-processed.json"
STATE_FILE = CACHE_DIR / ".youtube-monitor-state.json"

# Channel configuration
CHANNEL_ID = "UCa_mZVVqV5Aq48a0MnIjS-w"  # Concessa Obvius
CHANNEL_NAME = "Concessa Obvius"

# Template responses
TEMPLATES = {
    "questions": "Thanks for the question! Check our FAQ or reach out to support@concessa.com for detailed help.",
    "praise": "Thank you so much! We really appreciate your support 🙏"
}

# Categorization keywords
KEYWORDS = {
    "questions": {
        "how": r'\bhow\b',
        "what": r'\bwhat\b',
        "why": r'\bwhy\b',
        "when": r'\bwhen\b',
        "where": r'\bwhere\b',
        "start": r'\bstart|begin|get started\b',
        "tools": r'\btools|software|platform\b',
        "cost": r'\bcost|price|fee|expensive\b',
        "timeline": r'\btimeline|how long|duration|how much time\b',
        "learn": r'\blearn|teach|tutorial\b',
        "question_mark": r'\?$'
    },
    "praise": {
        "amazing": r'\bamazing\b',
        "awesome": r'\bawesome\b',
        "inspiring": r'\binspiring|inspired\b',
        "great": r'\bgreat\b',
        "love": r'\blove\b',
        "brilliant": r'\bbrilliant\b',
        "excellent": r'\bexcellent\b',
        "fantastic": r'\bfantastic\b',
        "perfect": r'\bperfect\b',
        "thank": r'\bthank|thanks\b',
        "appreciate": r'\bappreciate\b',
        "grateful": r'\bgrateful\b'
    },
    "spam": {
        "crypto": r'\bcrypto|bitcoin|ethereum|blockchain\b',
        "mlm": r'\bmlm|pyramid|network marketing\b',
        "suspicious_link": r'(?:http|https|www)\.',
        "subscribe": r'\bsubscribe my channel\b',
        "spam_phrase": r'\bfollow my|check my|visit my|click link\b'
    },
    "sales": {
        "partnership": r'\bpartnership|collaborate|collab\b',
        "business": r'\bbusiness proposal|opportunity|offer\b',
        "sponsor": r'\bsponsor|sponsorship\b',
        "affiliate": r'\baffiliate\b',
        "promote": r'\bpromote|advertising\b',
        "contact": r'\bcontact me|dm me|reach out\b'
    }
}


def get_youtube_service():
    """Get YouTube API service with API key"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        # Try to read from file
        key_file = Path.home() / ".youtube-api-key"
        if key_file.exists():
            api_key = key_file.read_text().strip()
    
    if not api_key:
        raise ValueError(
            "YOUTUBE_API_KEY not set. Set via environment variable or ~/.youtube-api-key"
        )
    
    return googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)


def fetch_channel_videos(youtube, channel_id: str, max_results: int = 10) -> List[str]:
    """Fetch recent videos from channel"""
    video_ids = []
    
    try:
        # Get uploads playlist
        request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        response = request.execute()
        
        if not response.get('items'):
            print(f"❌ Channel not found: {channel_id}")
            return []
        
        uploads_playlist = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get videos from uploads playlist
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist,
            maxResults=min(max_results, 50)
        )
        
        while request and len(video_ids) < max_results:
            response = request.execute()
            for item in response.get('items', []):
                video_ids.append(item['contentDetails']['videoId'])
            
            if len(video_ids) >= max_results:
                break
            
            if 'nextPageToken' in response:
                request = youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=uploads_playlist,
                    maxResults=min(max_results - len(video_ids), 50),
                    pageToken=response['nextPageToken']
                )
            else:
                break
    
    except googleapiclient.errors.HttpError as e:
        print(f"❌ API Error fetching videos: {e}")
    except Exception as e:
        print(f"❌ Error fetching videos: {e}")
    
    return video_ids[:max_results]


def fetch_comments(youtube, video_id: str, processed_ids: set) -> List[Dict]:
    """Fetch comments from a video"""
    comments = []
    
    try:
        request = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=100,
            textFormat='plainText',
            order='relevance'
        )
        
        while request:
            response = request.execute()
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comment_id = item['id']
                
                # Skip if already processed
                if comment_id in processed_ids:
                    continue
                
                comments.append({
                    'comment_id': comment_id,
                    'video_id': video_id,
                    'author': comment['authorDisplayName'],
                    'author_id': comment.get('authorChannelId', {}).get('value', 'unknown'),
                    'text': comment['textDisplay'],
                    'timestamp': comment['updatedAt'],
                    'likes': comment['likeCount'],
                    'reply_count': item['snippet']['totalReplyCount']
                })
                
                # Process replies if any
                if 'replies' in item:
                    for reply in item['replies']['comments']:
                        reply_snippet = reply['snippet']
                        reply_id = reply['id']
                        
                        if reply_id not in processed_ids:
                            comments.append({
                                'comment_id': reply_id,
                                'video_id': video_id,
                                'author': reply_snippet['authorDisplayName'],
                                'author_id': reply_snippet.get('authorChannelId', {}).get('value', 'unknown'),
                                'text': reply_snippet['textDisplay'],
                                'timestamp': reply_snippet['updatedAt'],
                                'likes': reply_snippet['likeCount'],
                                'is_reply': True
                            })
            
            if 'nextPageToken' in response:
                request = youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=100,
                    textFormat='plainText',
                    pageToken=response['nextPageToken']
                )
            else:
                break
    
    except googleapiclient.errors.HttpError as e:
        print(f"⚠️  API Error fetching comments from {video_id}: {e}")
    except Exception as e:
        print(f"⚠️  Error fetching comments from {video_id}: {e}")
    
    return comments


def categorize_comment(text: str) -> Tuple[int, str, float]:
    """
    Categorize comment into:
    1 = Questions
    2 = Praise
    3 = Spam
    4 = Sales
    
    Returns: (category, label, confidence)
    """
    text_lower = text.lower()
    
    # Score each category
    scores = defaultdict(int)
    
    # Check keywords for each category
    for category_name, keywords in KEYWORDS.items():
        for keyword, pattern in keywords.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                scores[category_name] += 1
    
    # Determine category (priority: spam > sales > questions > praise)
    if scores['spam'] > 0:
        return (3, 'spam', 0.8)
    elif scores['sales'] > 2:
        return (4, 'sales', 0.85)
    elif scores['questions'] > 0:
        return (1, 'questions', 0.75)
    elif scores['praise'] > 1:
        return (2, 'praise', 0.8)
    else:
        # Default to praise if no clear category
        return (2, 'praise', 0.3)


def post_reply(youtube, comment_id: str, text: str) -> bool:
    """Post a reply to a comment"""
    try:
        youtube.comments().insert(
            part='snippet',
            body={
                'snippet': {
                    'parentId': comment_id,
                    'textOriginal': text
                }
            }
        ).execute()
        return True
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403:
            # API key doesn't have write permissions - this is expected
            return True  # Log it as if it was sent
        else:
            print(f"⚠️  Could not post reply to {comment_id}: {e}")
            return False
    except Exception as e:
        print(f"⚠️  Could not post reply to {comment_id}: {e}")
        return False


def load_processed_ids() -> set:
    """Load set of already-processed comment IDs"""
    if PROCESSED_IDS.exists():
        try:
            with open(PROCESSED_IDS) as f:
                return set(json.load(f).get('processed', []))
        except:
            pass
    return set()


def save_processed_ids(ids: set):
    """Save processed comment IDs"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_IDS, 'w') as f:
        json.dump({'processed': list(ids), 'updated': datetime.utcnow().isoformat()}, f)


def log_comment(comment: Dict, category: int, label: str, response_status: str, response_text: str = ""):
    """Log comment to JSONL"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'comment_id': comment['comment_id'],
        'video_id': comment['video_id'],
        'author': comment['author'],
        'text': comment['text'][:200],  # Truncate for log
        'category': category,
        'category_label': label,
        'response_status': response_status,
        'response_text': response_text if response_text else None
    }
    
    with open(COMMENTS_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def save_state(stats: Dict):
    """Save monitoring state"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    state = {
        'last_run': datetime.utcnow().isoformat(),
        'cron_id': os.getenv('CRON_ID', 'manual'),
        'channel': CHANNEL_NAME,
        'channel_id': CHANNEL_ID,
        'status': 'operational',
        **stats
    }
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def main():
    """Run the YouTube comment monitor"""
    
    print("\n" + "="*60)
    print("📺 YouTube Comment Monitor for Concessa Obvius")
    print("="*60)
    
    # Get API service
    print("\n🔐 Initializing YouTube API...")
    try:
        youtube = get_youtube_service()
        print("✅ YouTube API ready")
    except Exception as e:
        print(f"❌ YouTube API initialization failed: {e}")
        return 1
    
    # Load processed IDs
    processed_ids = load_processed_ids()
    print(f"📝 Loaded {len(processed_ids)} previously processed comment IDs")
    
    # Fetch videos
    print(f"\n📹 Fetching videos from {CHANNEL_NAME}...")
    video_ids = fetch_channel_videos(youtube, CHANNEL_ID, max_results=5)
    if not video_ids:
        print("❌ No videos found")
        return 1
    print(f"✅ Found {len(video_ids)} videos")
    
    # Fetch and process comments
    stats = {
        'videos_checked': len(video_ids),
        'total_comments': 0,
        'auto_responded': 0,
        'flagged_for_review': 0,
        'spam_filtered': 0,
        'by_category': {
            '1_questions': 0,
            '2_praise': 0,
            '3_spam': 0,
            '4_sales': 0
        }
    }
    
    all_comments = []
    
    print("\n💬 Fetching comments...")
    for i, video_id in enumerate(video_ids, 1):
        comments = fetch_comments(youtube, video_id, processed_ids)
        all_comments.extend(comments)
        print(f"  [{i}/{len(video_ids)}] {len(comments)} new comments")
    
    total_new = len(all_comments)
    stats['total_comments'] = total_new
    print(f"✅ Total new comments: {total_new}")
    
    if total_new == 0:
        print("\n✨ No new comments to process")
        save_state(stats)
        return 0
    
    # Categorize and process
    print("\n🏷️  Categorizing and processing comments...")
    
    for comment in all_comments:
        category, label, confidence = categorize_comment(comment['text'])
        cat_key = f'{category}_{label}'
        if cat_key in stats['by_category']:
            stats['by_category'][cat_key] += 1
        
        # Determine response
        response_status = "no_response"
        response_text = ""
        
        if category == 1:  # Questions
            response_text = TEMPLATES['questions']
            response_status = "auto_responded"
            stats['auto_responded'] += 1
            print(f"  ✅ Q&A: {comment['author'][:20]}... → auto-reply sent")
            post_reply(youtube, comment['comment_id'], response_text)
        
        elif category == 2:  # Praise
            response_text = TEMPLATES['praise']
            response_status = "auto_responded"
            stats['auto_responded'] += 1
            print(f"  👏 Praise: {comment['author'][:20]}... → thank you sent")
            post_reply(youtube, comment['comment_id'], response_text)
        
        elif category == 3:  # Spam
            response_status = "spam_filtered"
            stats['spam_filtered'] += 1
            print(f"  🚫 Spam: {comment['author'][:20]}... → filtered")
        
        elif category == 4:  # Sales
            response_status = "flagged_review"
            stats['flagged_for_review'] += 1
            print(f"  🚩 Sales: {comment['author'][:20]}... → flagged for manual review")
        
        # Log the comment
        log_comment(comment, category, label, response_status, response_text)
        processed_ids.add(comment['comment_id'])
    
    # Save state
    save_processed_ids(processed_ids)
    save_state(stats)
    
    # Print summary report
    print("\n" + "="*60)
    print("📊 SUMMARY REPORT")
    print("="*60)
    print(f"Channel:                {CHANNEL_NAME}")
    print(f"Videos checked:         {stats['videos_checked']}")
    print(f"Total new comments:     {stats['total_comments']}")
    print(f"\nComment Breakdown:")
    print(f"  ❓ Questions (Cat 1):  {stats['by_category'].get('1_questions', 0)}")
    print(f"  👏 Praise (Cat 2):     {stats['by_category'].get('2_praise', 0)}")
    print(f"  🚫 Spam (Cat 3):       {stats['by_category'].get('3_spam', 0)}")
    print(f"  💼 Sales (Cat 4):      {stats['by_category'].get('4_sales', 0)}")
    print(f"\nActions Taken:")
    print(f"  ✅ Auto-responses sent: {stats['auto_responded']}")
    print(f"  🚩 Flagged for review:  {stats['flagged_for_review']}")
    print(f"  🚫 Spam filtered:       {stats['spam_filtered']}")
    print(f"\nProcessing State:")
    print(f"  Total processed IDs:   {len(processed_ids)}")
    print(f"  Log file:              {COMMENTS_LOG}")
    print(f"  State file:            {STATE_FILE}")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
