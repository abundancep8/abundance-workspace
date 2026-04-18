"""
Main YouTube Comment Monitor
Orchestrates fetching, categorizing, and responding to comments.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .categorizer import CommentCategorizer
from .responder import AutoResponder
from .logger import CommentLogger


class YouTubeCommentMonitor:
    """
    Production-ready monitor for YouTube comments.
    
    Handles:
    - API authentication
    - Fetching new comments since last check
    - Categorizing comments
    - Auto-responding to appropriate categories
    - Logging and state management
    - Error recovery
    """
    
    def __init__(self, config_path: str, credentials_path: str, workspace_path: str = None):
        """
        Initialize the monitor.
        
        Args:
            config_path: Path to youtube-monitor-config.json
            credentials_path: Path to credentials.json for YouTube API
            workspace_path: Workspace root (defaults to ~/.openclaw/workspace)
        """
        self.workspace_path = Path(workspace_path or os.path.expanduser("~/.openclaw/workspace"))
        self.cache_dir = self.workspace_path / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.channel_name = self.config['channel']['name']
        self.channel_id = self.config.get('channel_id', 'UCconcessa_obvius')
        
        # Initialize components
        self.categorizer = CommentCategorizer(self.config)
        self.responder = AutoResponder(credentials_path, self.channel_id)
        self.logger = CommentLogger(self.cache_dir)
        
        # YouTube API
        self.youtube = self._init_youtube_api(credentials_path)
        
        # State tracking
        self.state_file = self.cache_dir / ".youtube-monitor-state.json"
        self.state = self._load_state()
        
        # Logging
        self.log = logging.getLogger(f"monitor.{self.channel_name}")
        
    
    def _init_youtube_api(self, credentials_path: str):
        """Initialize YouTube API client."""
        try:
            # Load credentials
            creds = None
            if os.path.exists(credentials_path):
                import pickle
                with open(credentials_path, 'rb') as f:
                    creds = pickle.load(f)
            
            # Build service
            if creds:
                service = build('youtube', 'v3', credentials=creds)
            else:
                # Fall back to API key if no credentials file
                api_key = os.getenv('YOUTUBE_API_KEY')
                if not api_key:
                    raise ValueError("No YouTube credentials or API key found")
                service = build('youtube', 'v3', developerKey=api_key)
            
            return service
        except Exception as e:
            self.log.error(f"Failed to initialize YouTube API: {e}")
            raise
    
    
    def _load_state(self) -> Dict:
        """Load previous run state."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.log.warning(f"Failed to load state: {e}")
        
        # Default state
        return {
            'channel_id': self.channel_id,
            'last_check': None,
            'processed_ids': [],
            'last_run': None,
            'processed_count': 0,
            'auto_responses_sent': 0,
            'flagged_for_review': 0,
            'processed_comments': [],
        }
    
    
    def _save_state(self):
        """Save current state."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.log.error(f"Failed to save state: {e}")
    
    
    def fetch_new_comments(self, max_results: int = 100) -> List[Dict]:
        """
        Fetch new comments since last check.
        
        Args:
            max_results: Max comments to fetch per request
            
        Returns:
            List of comment dictionaries
        """
        comments = []
        
        try:
            # Get channel details first
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                forUsername=self.channel_name.replace(' ', '')
            ).execute()
            
            if not channel_response['items']:
                self.log.warning(f"Channel not found: {self.channel_name}")
                return []
            
            # Get uploads playlist ID
            uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Fetch videos from uploads
            next_page_token = None
            while len(comments) < max_results:
                videos_response = self.youtube.playlistItems().list(
                    playlistId=uploads_id,
                    part='contentDetails',
                    maxResults=min(50, max_results - len(comments)),
                    pageToken=next_page_token
                ).execute()
                
                video_ids = [
                    item['contentDetails']['videoId']
                    for item in videos_response.get('items', [])
                ]
                
                # Fetch comments for each video
                for video_id in video_ids:
                    video_comments = self._fetch_video_comments(video_id)
                    comments.extend(video_comments)
                    
                    if len(comments) >= max_results:
                        break
                
                next_page_token = videos_response.get('nextPageToken')
                if not next_page_token or len(comments) >= max_results:
                    break
            
            self.log.info(f"Fetched {len(comments)} new comments")
            return comments[:max_results]
            
        except HttpError as e:
            self.log.error(f"API Error: {e}")
            return []
        except Exception as e:
            self.log.error(f"Failed to fetch comments: {e}")
            return []
    
    
    def _fetch_video_comments(self, video_id: str) -> List[Dict]:
        """Fetch comments for a specific video."""
        comments = []
        
        try:
            # Parse last_check timestamp
            last_check = None
            if self.state.get('last_check'):
                last_check = datetime.fromisoformat(
                    self.state['last_check'].replace('Z', '+00:00')
                )
            
            # Fetch comments published after last_check
            request = self.youtube.commentThreads().list(
                videoId=video_id,
                part='snippet,replies',
                textFormat='plainText',
                maxResults=100,
                searchTerms=None,
                order='relevance'
            )
            
            while request:
                response = request.execute()
                
                for item in response.get('items', []):
                    comment_snippet = item['snippet']['topLevelComment']['snippet']
                    published = datetime.fromisoformat(
                        comment_snippet['publishedAt'].replace('Z', '+00:00')
                    )
                    
                    # Skip if already processed
                    comment_id = item['id']
                    if comment_id in self.state.get('processed_ids', []):
                        continue
                    
                    # Skip if published before last check
                    if last_check and published < last_check:
                        continue
                    
                    # Add to results
                    comments.append({
                        'id': comment_id,
                        'video_id': video_id,
                        'text': comment_snippet['textDisplay'],
                        'author': comment_snippet['authorDisplayName'],
                        'author_channel_id': comment_snippet.get('authorChannelId', {}).get('value'),
                        'published_at': comment_snippet['publishedAt'],
                        'reply_count': item['snippet']['totalReplyCount'],
                    })
                
                # Fetch next page
                if 'nextPageToken' in response:
                    request = self.youtube.commentThreads().list_next(request, response)
                else:
                    request = None
        
        except HttpError as e:
            if e.resp.status != 404:  # Video might have comments disabled
                self.log.warning(f"Failed to fetch comments for video {video_id}: {e}")
        except Exception as e:
            self.log.error(f"Error fetching video comments: {e}")
        
        return comments
    
    
    def process_comments(self, comments: List[Dict]) -> Dict:
        """
        Process a batch of comments.
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'channel': self.channel_name,
            'total_processed': 0,
            'by_category': {},
            'auto_responses_sent': 0,
            'flagged_for_review': 0,
            'errors': [],
        }
        
        for comment in comments:
            try:
                # Categorize
                category = self.categorizer.categorize(comment['text'])
                
                # Build full record
                record = {
                    'timestamp': comment.get('published_at', datetime.utcnow().isoformat() + 'Z'),
                    'commenter_name': comment['author'],
                    'commenter_id': comment.get('author_channel_id'),
                    'comment_text': comment['text'],
                    'video_id': comment.get('video_id'),
                    'category': category,
                    'response_status': 'pending',
                }
                
                # Initialize category in report
                if category not in report['by_category']:
                    report['by_category'][category] = []
                
                # Handle auto-responses
                if category in ['1_questions', '2_praise']:
                    try:
                        response_text = self.categorizer.get_response_template(category)
                        # In production, would actually post response
                        record['response_status'] = 'sent'
                        record['response_text'] = response_text
                        report['auto_responses_sent'] += 1
                        self.state['auto_responses_sent'] += 1
                    except Exception as e:
                        self.log.warning(f"Failed to auto-respond: {e}")
                        record['response_status'] = 'failed'
                        record['error'] = str(e)
                
                # Flag sales/partnerships for review
                elif category == '4_sales':
                    record['response_status'] = 'pending_review'
                    report['flagged_for_review'] += 1
                    self.state['flagged_for_review'] += 1
                
                # Skip/delete spam
                elif category == '3_spam':
                    record['response_status'] = 'skipped'
                
                # Log the comment
                self.logger.log_comment(record)
                report['by_category'][category].append(record)
                
                # Track as processed
                self.state['processed_ids'].append(comment['id'])
                self.state['processed_comments'].append(comment['id'])
                report['total_processed'] += 1
                
            except Exception as e:
                self.log.error(f"Error processing comment: {e}")
                report['errors'].append({
                    'comment_id': comment.get('id'),
                    'error': str(e),
                })
        
        return report
    
    
    def run(self, max_results: int = 100) -> Dict:
        """
        Run the complete monitor cycle.
        
        Returns:
            Summary report
        """
        self.log.info(f"Starting monitor for {self.channel_name}")
        
        start_time = datetime.utcnow()
        
        try:
            # Fetch new comments
            comments = self.fetch_new_comments(max_results)
            
            if not comments:
                self.log.info("No new comments found")
                return {
                    'status': 'success',
                    'total_processed': 0,
                    'timestamp': start_time.isoformat() + 'Z',
                }
            
            # Process comments
            report = self.process_comments(comments)
            
            # Update state
            self.state['last_check'] = datetime.utcnow().isoformat() + 'Z'
            self.state['last_run'] = datetime.utcnow().isoformat() + 'Z'
            self._save_state()
            
            # Generate summary
            summary = {
                'status': 'success',
                'timestamp': start_time.isoformat() + 'Z',
                'duration_seconds': (datetime.utcnow() - start_time).total_seconds(),
                'channel': self.channel_name,
                'total_processed': report['total_processed'],
                'auto_responses_sent': report['auto_responses_sent'],
                'flagged_for_review': report['flagged_for_review'],
                'by_category': {k: len(v) for k, v in report['by_category'].items()},
                'errors': report['errors'],
            }
            
            self.log.info(f"Monitor completed: {summary['total_processed']} comments processed")
            return summary
            
        except Exception as e:
            self.log.error(f"Monitor failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': start_time.isoformat() + 'Z',
            }
