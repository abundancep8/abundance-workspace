"""
Auto Responder
Handles posting replies to YouTube comments via API.
"""

import logging
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class AutoResponder:
    """
    Handles auto-responses to YouTube comments.
    
    Can post replies to comments, with error handling and rate limiting.
    """
    
    def __init__(self, credentials_path: str, channel_id: str):
        """
        Initialize responder.
        
        Args:
            credentials_path: Path to credentials.json
            channel_id: YouTube channel ID
        """
        self.channel_id = channel_id
        self.log = logging.getLogger('responder')
        
        try:
            import pickle
            import os
            
            creds = None
            if os.path.exists(credentials_path):
                with open(credentials_path, 'rb') as f:
                    creds = pickle.load(f)
            
            if creds:
                self.youtube = build('youtube', 'v3', credentials=creds)
            else:
                api_key = os.getenv('YOUTUBE_API_KEY')
                if not api_key:
                    raise ValueError("No YouTube credentials found")
                self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        except Exception as e:
            self.log.warning(f"Failed to initialize responder: {e}")
            self.youtube = None
    
    
    def post_reply(self, comment_id: str, reply_text: str) -> bool:
        """
        Post a reply to a comment.
        
        Args:
            comment_id: ID of the comment to reply to
            reply_text: Text of the reply
            
        Returns:
            True if successful, False otherwise
        """
        if not self.youtube:
            self.log.warning("YouTube API not initialized")
            return False
        
        try:
            request = self.youtube.comments().insert(
                part='snippet',
                body={
                    'snippet': {
                        'parentId': comment_id,
                        'textOriginal': reply_text
                    }
                }
            )
            response = request.execute()
            self.log.info(f"Posted reply to comment {comment_id}")
            return True
        
        except HttpError as e:
            if e.resp.status == 403:
                self.log.warning(f"Permission denied posting reply: {e}")
            elif e.resp.status == 404:
                self.log.warning(f"Comment not found: {comment_id}")
            else:
                self.log.error(f"API error posting reply: {e}")
            return False
        
        except Exception as e:
            self.log.error(f"Failed to post reply: {e}")
            return False
    
    
    def pin_comment(self, video_id: str, comment_id: str) -> bool:
        """
        Pin a comment (if channel owner).
        
        Args:
            video_id: Video ID
            comment_id: Comment ID to pin
            
        Returns:
            True if successful
        """
        if not self.youtube:
            return False
        
        try:
            self.youtube.commentThreads().update(
                part='snippet',
                body={
                    'id': comment_id,
                    'snippet': {
                        'canReply': True,
                        'isPublic': True
                    }
                }
            ).execute()
            return True
        except Exception as e:
            self.log.warning(f"Failed to pin comment: {e}")
            return False
    
    
    def delete_comment(self, comment_id: str) -> bool:
        """
        Delete a comment (spam, etc).
        
        Args:
            comment_id: Comment ID to delete
            
        Returns:
            True if successful
        """
        if not self.youtube:
            return False
        
        try:
            self.youtube.comments().delete(id=comment_id).execute()
            self.log.info(f"Deleted comment {comment_id}")
            return True
        except HttpError as e:
            if e.resp.status == 403:
                self.log.warning(f"Cannot delete comment (not owner?): {comment_id}")
            else:
                self.log.error(f"API error deleting comment: {e}")
            return False
        except Exception as e:
            self.log.error(f"Failed to delete comment: {e}")
            return False
