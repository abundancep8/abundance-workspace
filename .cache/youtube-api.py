#!/usr/bin/env python3
"""
YouTube API integration for comment monitoring.
Requires: google-auth-oauthlib, google-auth-httplib2, google-api-python-client
Install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timedelta

# YouTube API setup
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class YouTubeCommentFetcher:
    """Fetch and manage comments from YouTube channel."""
    
    def __init__(self, api_key: Optional[str] = None, credentials_file: Optional[str] = None):
        """
        Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API key (for read-only access)
            credentials_file: Path to OAuth 2.0 credentials JSON (for write access)
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.credentials_file = credentials_file or os.getenv("YOUTUBE_CREDENTIALS_FILE")
        self.service = None
        self.channel_id = None
        
        self._init_service()
    
    def _init_service(self):
        """Initialize YouTube API service."""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            if self.credentials_file and Path(self.credentials_file).exists():
                # Use service account credentials (for write access)
                credentials = Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
                )
                self.service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)
            elif self.api_key:
                # Use API key (read-only)
                from googleapiclient.discovery import build
                self.service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.api_key)
            else:
                raise ValueError("Must provide either YOUTUBE_API_KEY or credentials file")
        except ImportError:
            print("⚠️ YouTube API libraries not installed. Install with:")
            print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            raise
    
    def get_channel_id(self, channel_name: str) -> Optional[str]:
        """Get channel ID from channel name."""
        if not self.service:
            return None
        
        try:
            request = self.service.search().list(
                q=channel_name,
                part="snippet",
                type="channel",
                maxResults=1
            )
            response = request.execute()
            
            if response.get("items"):
                return response["items"][0]["snippet"]["channelId"]
        except Exception as e:
            print(f"Error fetching channel ID: {e}")
        
        return None
    
    def fetch_comments(self, channel_id: str, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch recent comments from a channel.
        
        Args:
            channel_id: YouTube channel ID
            since: Only fetch comments after this timestamp (optional)
        
        Returns:
            List of comment dicts with keys: id, author, text, timestamp
        """
        if not self.service:
            return []
        
        comments = []
        
        try:
            # Get uploads playlist for the channel
            request = self.service.channels().list(
                part="contentDetails",
                id=channel_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return comments
            
            uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get recent videos
            request = self.service.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                order="date"
            )
            response = request.execute()
            
            video_ids = [item["snippet"]["resourceId"]["videoId"] for item in response.get("items", [])]
            
            # Fetch comments for each video
            for video_id in video_ids:
                comments.extend(self._fetch_video_comments(video_id, since))
        
        except Exception as e:
            print(f"Error fetching comments: {e}")
        
        return comments
    
    def _fetch_video_comments(self, video_id: str, since: Optional[datetime] = None) -> List[Dict]:
        """Fetch comments for a specific video."""
        comments = []
        
        try:
            request = self.service.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                order="relevance"
            )
            
            while request:
                response = request.execute()
                
                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    
                    # Parse publish time
                    published_at = datetime.fromisoformat(
                        comment["publishedAt"].replace("Z", "+00:00")
                    )
                    
                    # Skip if older than since timestamp
                    if since and published_at < since:
                        continue
                    
                    comments.append({
                        "id": item["id"],
                        "video_id": video_id,
                        "author": comment["authorDisplayName"],
                        "text": comment["textDisplay"],
                        "timestamp": comment["publishedAt"],
                        "likes": comment["likeCount"],
                        "reply_count": item["snippet"]["totalReplyCount"],
                    })
                
                # Check for more pages
                if "nextPageToken" in response:
                    request = self.service.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        textFormat="plainText",
                        pageToken=response["nextPageToken"],
                        maxResults=100,
                        order="relevance"
                    )
                else:
                    request = None
        
        except Exception as e:
            print(f"Error fetching video comments for {video_id}: {e}")
        
        return comments
    
    def post_reply(self, parent_id: str, reply_text: str) -> Optional[str]:
        """Post a reply to a comment."""
        if not self.service:
            print("YouTube API service not available")
            return None
        
        try:
            request = self.service.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": parent_id,
                        "textOriginal": reply_text
                    }
                }
            )
            response = request.execute()
            return response.get("id")
        except Exception as e:
            print(f"Error posting reply: {e}")
            return None


# Example usage
if __name__ == "__main__":
    fetcher = YouTubeCommentFetcher()
    
    # Get channel ID (example)
    channel_id = fetcher.get_channel_id("Concessa Obvius")
    if channel_id:
        print(f"Channel ID: {channel_id}")
        
        # Fetch recent comments
        since = datetime.now() - timedelta(minutes=30)
        comments = fetcher.fetch_comments(channel_id, since=since)
        
        print(f"Fetched {len(comments)} comments")
        for comment in comments[:5]:
            print(f"  {comment['author']}: {comment['text'][:60]}...")
