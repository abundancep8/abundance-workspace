#!/usr/bin/env python3
"""
YouTube Direct Upload System
Generate videos from scripts + upload to Concessa Obvius channel
Bypasses Blotato entirely - direct YouTube OAuth integration
"""

import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime, timedelta
import time

# YouTube API setup
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "youtube-oauth-secrets.json"  # OAuth credentials

class YouTubeUploader:
    def __init__(self, client_secrets_file):
        self.youtube = self.authenticate(client_secrets_file)
        self.channel_id = "UC_gFZz1H2SBJjCJqj0P4KNg"  # Concessa Obvius channel
        
    def authenticate(self, secrets_file):
        """Authenticate with YouTube API using OAuth"""
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            secrets_file, SCOPES)
        credentials = flow.run_local_server(port=0)
        
        youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)
        
        print("✅ YouTube API authenticated")
        return youtube
    
    def upload_video(self, video_file, title, description, tags=None):
        """Upload video to YouTube"""
        print(f"\n📤 Uploading: {title}")
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or ['AI', 'business', 'automation'],
                'categoryId': '27'  # Education category
            },
            'status': {
                'privacyStatus': 'public',
                'publishAt': datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(
                video_file,
                chunksize=-1,
                resumable=True
            )
        )
        
        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload progress: {int(status.progress() * 100)}%")
            except googleapiclient.errors.HttpError as e:
                print(f"❌ Upload failed: {e}")
                return None
        
        video_id = response['id']
        print(f"✅ Uploaded successfully")
        print(f"   Video ID: {video_id}")
        print(f"   URL: https://youtube.com/watch?v={video_id}")
        
        return video_id
    
    def schedule_video(self, video_file, title, description, publish_time):
        """Schedule video for specific time"""
        print(f"\n📤 Scheduling: {title} for {publish_time}")
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['AI', 'business', 'automation'],
                'categoryId': '27'
            },
            'status': {
                'privacyStatus': 'private',  # Private until publish time
                'publishAt': publish_time.isoformat() + 'Z'
            }
        }
        
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
        
        return response['id']


class VideoGenerator:
    """Generate videos from scripts using text-to-video service"""
    
    def __init__(self, service_type='local'):
        """
        service_type: 'local' (ffmpeg), 'heygen', 'synthesia', 'd-id', 'pika'
        For now, using local generation with ffmpeg + image frames
        """
        self.service = service_type
        
    def generate_from_script(self, script_text, title, output_file):
        """Generate video from script"""
        print(f"\n🎬 Generating video: {title}")
        
        if self.service == 'local':
            # Simple approach: create slides from script, combine into video
            self.generate_local_video(script_text, title, output_file)
        else:
            # Would integrate with external service
            print(f"⚠️ {self.service} integration not yet implemented")
            
    def generate_local_video(self, script, title, output_file):
        """Generate video locally using ffmpeg"""
        # Create a simple text-based video (slides with voiceover could be added later)
        # For now, just creating a placeholder
        
        print(f"⏳ Creating video file...")
        
        # In production, this would:
        # 1. Split script into slides
        # 2. Create image frames for each slide
        # 3. Synthesize speech from script (TTS)
        # 4. Combine into video with ffmpeg
        # 5. Add captions, music, effects
        
        # Placeholder: create minimal video file
        import subprocess
        
        try:
            # Create a silent 30-second video (placeholder)
            cmd = [
                'ffmpeg', '-f', 'lavfi', '-i', 'color=c=black:s=1280x720:d=30',
                '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono:d=30',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-y', output_file
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✅ Video generated: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Video generation failed: {e}")
            return False


def main():
    print("🚀 YouTube Direct Upload System\n")
    
    # Check if we have YouTube authentication
    if not os.path.exists('youtube-oauth-secrets.json'):
        print("⚠️ YouTube OAuth secrets file not found")
        print("Need: youtube-oauth-secrets.json (from Google Cloud Console)")
        print("Instructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create OAuth 2.0 credentials (Desktop app)")
        print("3. Download JSON and save as youtube-oauth-secrets.json")
        return
    
    # Initialize uploader
    try:
        uploader = YouTubeUploader('youtube-oauth-secrets.json')
    except Exception as e:
        print(f"❌ YouTube authentication failed: {e}")
        return
    
    # Load scripts
    print("\n📚 Loading scripts...")
    try:
        with open('blotato-script-batch-1.md', 'r') as f:
            content = f.read()
    except:
        print("❌ Script batch file not found")
        return
    
    # Test: generate and upload one video
    print("\n" + "="*60)
    print("TEST: Generate + Upload 1 Video")
    print("="*60)
    
    generator = VideoGenerator('local')
    
    # Create test video
    test_script = "Day 1: I hired an AI and here's what happened"
    test_video = "/tmp/test-video.mp4"
    
    if generator.generate_from_script(test_script, "Test Video", test_video):
        # Upload to YouTube
        if os.path.exists(test_video):
            video_id = uploader.upload_video(
                test_video,
                title="I hired an AI and here's what happened (Test)",
                description="Day 1 of building with AI",
                tags=['AI', 'business', 'automation']
            )
            
            if video_id:
                print(f"\n✅ SUCCESS: Video uploaded to YouTube!")
                print(f"   Video ID: {video_id}")
                
                # Log success
                with open('.cache/youtube-uploads.jsonl', 'a') as f:
                    f.write(json.dumps({
                        'timestamp': datetime.now().isoformat(),
                        'video_id': video_id,
                        'title': "I hired an AI",
                        'script_batch': 1,
                        'status': 'uploaded'
                    }) + '\n')


if __name__ == '__main__':
    main()
