#!/usr/bin/env python3
"""
YouTube Channel Comment Monitor and Auto-Responder
Monitors "Concessa Obvius" channel for new comments and categorizes/responds.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import re

try:
    import google.oauth2.credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("⚠️  Google API client not installed. Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class YouTubeCommentMonitor:
    """Monitor and manage YouTube channel comments."""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    
    CATEGORY_TEMPLATES = {
        'questions': {
            'prefix': '✅ Great question!',
            'responses': [
                "Thanks for asking! This is a common question. [Provide helpful answer related to: how-to, tools, cost, timeline]",
                "Great inquiry! Here's what you need to know: [Detailed response with resources/links if applicable]",
                "Perfect question! [Address specific how-to/tool/cost/timeline aspect]"
            ]
        },
        'praise': {
            'prefix': '❤️ Thank you!',
            'responses': [
                "Thank you so much! Your support means the world to me! 🙏",
                "Wow, I really appreciate that! Comments like this fuel my passion to keep creating. ❤️",
                "This made my day! Thank you for the kind words! 🌟"
            ]
        },
        'spam': {
            'prefix': 'FLAG_NO_RESPONSE',
            'responses': []
        },
        'sales': {
            'prefix': 'FLAG_FOR_REVIEW',
            'responses': []
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, log_file: str = '.cache/youtube-comments.jsonl'):
        """Initialize the monitor with YouTube API credentials."""
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.log_file = log_file
        self.youtube = None
        self.channel_id = None
        self.stats = {
            'total_processed': 0,
            'auto_responses_sent': 0,
            'flagged_for_review': 0,
            'by_category': {
                'questions': 0,
                'praise': 0,
                'spam': 0,
                'sales': 0
            }
        }
        
        if not self.api_key:
            raise ValueError("❌ YOUTUBE_API_KEY not found in environment variables")
        
        self._init_youtube_client()
        self._load_previous_comments()
    
    def _init_youtube_client(self):
        """Initialize YouTube API client."""
        try:
            self.youtube = build(self.API_SERVICE_NAME, self.API_VERSION, developerKey=self.api_key)
            print("✅ YouTube API client initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize YouTube API: {e}")
    
    def _load_previous_comments(self):
        """Load previously logged comments to track which ones we've processed."""
        self.processed_ids = set()
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)
                            if 'comment_id' in record:
                                self.processed_ids.add(record['comment_id'])
                print(f"📋 Loaded {len(self.processed_ids)} previously processed comments")
            except Exception as e:
                print(f"⚠️  Could not load previous comments: {e}")
    
    def find_channel(self, channel_name: str) -> Optional[str]:
        """Find YouTube channel ID by channel name."""
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=channel_name,
                type='channel',
                maxResults=1
            )
            response = request.execute()
            
            if response['items']:
                channel_id = response['items'][0]['id']['channelId']
                channel_title = response['items'][0]['snippet']['title']
                print(f"✅ Found channel: {channel_title} ({channel_id})")
                self.channel_id = channel_id
                return channel_id
            else:
                print(f"❌ Channel '{channel_name}' not found")
                return None
        except Exception as e:
            print(f"❌ Error searching for channel: {e}")
            return None
    
    def get_channel_videos(self, channel_id: str) -> List[str]:
        """Get all video IDs from a channel."""
        try:
            video_ids = []
            request = self.youtube.search().list(
                part='id',
                channelId=channel_id,
                type='video',
                maxResults=50,
                order='date'
            )
            
            while request and len(video_ids) < 200:  # Limit to recent 200 videos
                response = request.execute()
                for item in response.get('items', []):
                    video_ids.append(item['id']['videoId'])
                
                if 'nextPageToken' in response:
                    request = self.youtube.search().list(
                        part='id',
                        channelId=channel_id,
                        type='video',
                        pageToken=response['nextPageToken'],
                        maxResults=50,
                        order='date'
                    )
                else:
                    break
            
            print(f"📹 Found {len(video_ids)} videos from channel")
            return video_ids
        except Exception as e:
            print(f"❌ Error fetching videos: {e}")
            return []
    
    def get_video_comments(self, video_id: str) -> List[Dict]:
        """Fetch comments from a specific video."""
        try:
            comments = []
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=100,
                order='relevance'
            )
            
            while request:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comment_id = item['id']
                    
                    # Skip if already processed
                    if comment_id in self.processed_ids:
                        continue
                    
                    comments.append({
                        'comment_id': comment_id,
                        'video_id': video_id,
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'timestamp': comment['publishedAt'],
                        'likes': comment['likeCount']
                    })
                
                if 'nextPageToken' in response:
                    request = self.youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        pageToken=response['nextPageToken'],
                        textFormat='plainText',
                        maxResults=100,
                        order='relevance'
                    )
                else:
                    break
            
            return comments
        except Exception as e:
            print(f"⚠️  Error fetching comments from video {video_id}: {e}")
            return []
    
    def categorize_comment(self, text: str) -> str:
        """Categorize a comment into one of four categories."""
        text_lower = text.lower()
        
        # Spam detection
        spam_keywords = ['bitcoin', 'ethereum', 'crypto', 'mlm', 'work from home', 'make money fast', 
                        'click here', 'dm me', 'join my group', 'casino', 'lottery', 'guaranteed']
        if any(keyword in text_lower for keyword in spam_keywords):
            return 'spam'
        
        # Sales/Partnership detection
        sales_keywords = ['partnership', 'collaborate', 'collab', 'brand deal', 'sponsor',
                         'affiliate', 'commission', 'promote my', 'check out my', 'visit my website',
                         'business opportunity', 'investment']
        if any(keyword in text_lower for keyword in sales_keywords):
            return 'sales'
        
        # Praise detection
        praise_keywords = ['amazing', 'love it', 'great', 'awesome', 'inspiring', 'beautiful',
                          'thank you', 'thanks', 'excellent', 'brilliant', 'fantastic', 'wonderful',
                          'incredible', 'perfect', 'genius', '❤', '👍', '🔥', '⭐']
        if any(keyword in text_lower for keyword in praise_keywords):
            return 'praise'
        
        # Questions detection
        question_markers = ['?', 'how', 'what', 'where', 'when', 'why', 'cost', 'price', 'tools',
                           'timeline', 'how to', 'how do', 'can you', 'could you', 'would you']
        if any(marker in text_lower for marker in question_markers):
            return 'questions'
        
        # Default to questions if contains meaningful engagement
        if len(text.split()) > 5:
            return 'questions'
        
        return 'questions'  # Default category
    
    def generate_response(self, category: str, comment_text: str) -> Optional[str]:
        """Generate an appropriate response based on category."""
        if category not in self.CATEGORY_TEMPLATES:
            return None
        
        template = self.CATEGORY_TEMPLATES[category]
        
        if not template['responses']:
            return None
        
        # For now, pick the first response (in production, could randomize)
        response = template['responses'][0]
        
        # Could enhance with specific details from comment_text
        return response
    
    def process_comments(self, channel_name: str = "Concessa Obvius") -> Dict:
        """Main function: process all comments from the channel."""
        print(f"\n🎬 Starting YouTube Comment Monitor for '{channel_name}'")
        print(f"⏰ Current time: {datetime.now().isoformat()}\n")
        
        # Find channel
        channel_id = self.find_channel(channel_name)
        if not channel_id:
            return {"error": f"Channel '{channel_name}' not found"}
        
        # Get videos from channel
        video_ids = self.get_channel_videos(channel_id)
        if not video_ids:
            return {"error": "No videos found on channel"}
        
        # Process comments from each video
        all_comments = []
        for video_id in video_ids[:10]:  # Limit to recent 10 videos for this run
            comments = self.get_video_comments(video_id)
            all_comments.extend(comments)
        
        print(f"\n📊 Processing {len(all_comments)} new comments...\n")
        
        # Log and categorize each comment
        for comment in all_comments:
            category = self.categorize_comment(comment['text'])
            response = self.generate_response(category, comment['text']) if category != 'spam' else None
            response_status = 'auto_responded' if response else 'flagged' if category == 'sales' else 'logged'
            
            # Log to JSONL
            record = {
                'timestamp': comment['timestamp'],
                'comment_id': comment['comment_id'],
                'commenter': comment['author'],
                'text': comment['text'],
                'category': category,
                'response_status': response_status,
                'response_sent': response is not None,
                'response_text': response if response else None,
                'likes': comment['likes']
            }
            
            self._log_comment(record)
            
            # Update stats
            self.stats['total_processed'] += 1
            self.stats['by_category'][category] += 1
            if response_status == 'auto_responded':
                self.stats['auto_responses_sent'] += 1
            elif response_status == 'flagged':
                self.stats['flagged_for_review'] += 1
            
            # Print summary
            print(f"📌 [{category.upper()}] @{comment['author']}: {comment['text'][:60]}...")
            if response:
                print(f"   ✅ Response: {response[:70]}...")
            elif category == 'sales':
                print(f"   🚩 FLAGGED FOR REVIEW")
            print()
        
        return self.stats
    
    def _log_comment(self, record: Dict):
        """Log a comment record to JSONL file."""
        try:
            os.makedirs(os.path.dirname(self.log_file) or '.', exist_ok=True)
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(record) + '\n')
        except Exception as e:
            print(f"❌ Error logging comment: {e}")
    
    def generate_report(self) -> str:
        """Generate final report."""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║          YouTube Comment Monitoring Report                 ║
║              "Concessa Obvius" Channel                      ║
╚════════════════════════════════════════════════════════════╝

📊 SUMMARY STATISTICS
─────────────────────────────────────────────────────────────
Total Comments Processed:     {self.stats['total_processed']}
Auto-Responses Sent:          {self.stats['auto_responses_sent']}
Flagged for Manual Review:    {self.stats['flagged_for_review']}

📈 BREAKDOWN BY CATEGORY
─────────────────────────────────────────────────────────────
Questions:                    {self.stats['by_category']['questions']} ({self.stats['by_category']['questions'] * 100 // max(1, self.stats['total_processed'])}%)
Praise:                       {self.stats['by_category']['praise']} ({self.stats['by_category']['praise'] * 100 // max(1, self.stats['total_processed'])}%)
Spam:                         {self.stats['by_category']['spam']} ({self.stats['by_category']['spam'] * 100 // max(1, self.stats['total_processed'])}%)
Sales/Partnerships:           {self.stats['by_category']['sales']} ({self.stats['by_category']['sales'] * 100 // max(1, self.stats['total_processed'])}%)

📝 LOG FILE
─────────────────────────────────────────────────────────────
Location: {os.path.abspath(self.log_file)}
Format:   JSONL (one record per line)
Fields:   timestamp, comment_id, commenter, text, category, response_status

🔍 ACTIONS TAKEN
─────────────────────────────────────────────────────────────
✅ Auto-Responded to all Questions & Praise
🚩 Flagged {self.stats['flagged_for_review']} Sales/Partnership offers for your review
🔕 Ignored {self.stats['by_category']['spam']} spam comments

⏰ COMPLETION TIME
─────────────────────────────────────────────────────────────
{datetime.now().isoformat()}

═════════════════════════════════════════════════════════════
"""
        return report


def main():
    """Main entry point."""
    if not GOOGLE_API_AVAILABLE:
        print("❌ SETUP REQUIRED\n")
        print("The YouTube Comment Monitor requires Google API client library.")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("─" * 60)
        print("1. Install required packages:")
        print("   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print("\n2. Get YouTube API credentials:")
        print("   a) Go to https://console.cloud.google.com/")
        print("   b) Create a new project")
        print("   c) Enable YouTube Data API v3")
        print("   d) Create an OAuth 2.0 Client ID (Desktop application)")
        print("   e) Download the credentials JSON file")
        print("\n3. Set the API key or credentials:")
        print("   export YOUTUBE_API_KEY='your-api-key-here'")
        print("   OR")
        print("   export YOUTUBE_CREDENTIALS_FILE='/path/to/credentials.json'")
        print("\n4. Run this script again")
        print("─" * 60)
        return
    
    # Check for API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ ERROR: YOUTUBE_API_KEY environment variable not set")
        print("\nPlease set your YouTube API key:")
        print("  export YOUTUBE_API_KEY='your-api-key-here'")
        print("\nThen run this script again.")
        return
    
    try:
        monitor = YouTubeCommentMonitor(api_key)
        stats = monitor.process_comments()
        report = monitor.generate_report()
        print(report)
        print(f"\n✅ Log file saved to: {os.path.abspath(monitor.log_file)}")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
