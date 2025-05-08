"""
YouTube client for uploading videos and retrieving comments.
"""
import os
import pickle
import logging
import tempfile
import requests
from typing import Dict, Any, Optional, List, Union

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Import configuration
from config import YOUTUBE_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_CHANNEL_ID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth 2.0 scopes for YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", 
          "https://www.googleapis.com/auth/youtube.force-ssl"]

class YouTubeClient:
    """
    Client for interacting with YouTube API to upload videos and retrieve comments.
    """
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
                 api_key: Optional[str] = None, channel_id: Optional[str] = None):
        """
        Initialize the YouTube client.
        
        Args:
            client_id: YouTube OAuth client ID (defaults to environment variable)
            client_secret: YouTube OAuth client secret (defaults to environment variable)
            api_key: YouTube API key (defaults to environment variable)
            channel_id: YouTube channel ID (defaults to environment variable)
        """
        self.client_id = client_id or YOUTUBE_CLIENT_ID
        self.client_secret = client_secret or YOUTUBE_CLIENT_SECRET
        self.api_key = api_key or YOUTUBE_API_KEY
        self.channel_id = channel_id or YOUTUBE_CHANNEL_ID
        self.youtube = None
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.warning("YouTube OAuth credentials are missing!")
            raise ValueError("YouTube OAuth credentials are required")
        
        # Initialize client
        try:
            self.authenticate()
            logger.info("YouTube client initialized")
        except Exception as e:
            logger.error(f"Error initializing YouTube client: {str(e)}")
            raise
    
    def authenticate(self) -> None:
        """
        Authenticate with YouTube API using OAuth 2.0.
        """
        creds = None
        force_new_auth = False
        
        # Check for token in data directory first (for Docker), then in current directory
        token_paths = ['/app/data/token.pickle', './data/token.pickle', 'token.pickle']
        token_path_used = None
        
        for token_path in token_paths:
            if os.path.exists(token_path):
                try:
                    with open(token_path, 'rb') as token:
                        creds = pickle.load(token)
                    logger.info(f"Loaded credentials from {token_path}")
                    token_path_used = token_path
                    break
                except Exception as e:
                    logger.warning(f"Error loading credentials from {token_path}: {str(e)}")
                    force_new_auth = True
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid or force_new_auth:
            if creds and creds.expired and creds.refresh_token and not force_new_auth:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed expired credentials")
                except Exception as e:
                    logger.warning(f"Error refreshing credentials: {str(e)}")
                    # If refresh fails, force new authentication
                    creds = None
            
            # If we still don't have valid credentials, get new ones
            if not creds or not creds.valid:
                # Create client_secrets.json file for OAuth flow
                client_secrets = {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }
                
                # Write client secrets to temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    import json
                    json.dump(client_secrets, f)
                    client_secrets_file = f.name
                
                try:
                    # Create flow from client secrets file
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file, 
                        SCOPES,
                        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
                    )
                    
                    # Get the authorization URL
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    
                    # Print the URL for the user to visit
                    print(f"Please visit this URL to authorize this application: {auth_url}")
                    print("After authorization, you will receive a code. Please enter that code here:")
                    
                    # Get the authorization code from the user
                    code = input().strip()
                    
                    # Exchange the authorization code for credentials
                    flow.fetch_token(code=code)
                    creds = flow.credentials
                    
                    logger.info("Authentication successful")
                finally:
                    # Clean up temporary file
                    if os.path.exists(client_secrets_file):
                        os.remove(client_secrets_file)
                
                # Save credentials for future use
                # Try to save in data directory first, then in current directory
                for save_path in ['/app/data', './data', '.']:
                    try:
                        os.makedirs(save_path, exist_ok=True)
                        token_file = os.path.join(save_path, 'token.pickle')
                        with open(token_file, 'wb') as token:
                            pickle.dump(creds, token)
                        logger.info(f"Saved credentials to {token_file}")
                        break
                    except Exception as e:
                        logger.warning(f"Could not save credentials to {save_path}: {str(e)}")
        
        # Build YouTube API client
        self.youtube = build("youtube", "v3", credentials=creds)
    
    def upload_video(self, video_url: str, title: str, description: str, 
                     tags: List[str] = None) -> Optional[str]:
        """
        Upload a video to YouTube.
        
        Args:
            video_url: URL of the video file to upload
            title: Title of the video
            description: Description of the video
            tags: List of tags for the video
            
        Returns:
            YouTube video ID if successful, None otherwise
            Special return value "URL_EXPIRED" if the URL is expired or inaccessible
        """
        logger.info(f"Uploading video: {title}")
        
        # Create a temporary file path
        temp_fd, temp_video_path = tempfile.mkstemp(suffix='.mp4')
        os.close(temp_fd)  # Close the file descriptor immediately
        
        try:
            # Download the video
            try:
                response = requests.get(video_url, stream=True)
                response.raise_for_status()  # Raise exception for HTTP errors
            except requests.HTTPError as e:
                if e.response.status_code == 403:
                    logger.warning(f"URL expired or access denied: {video_url}")
                    return "URL_EXPIRED"  # Special return value for expired URLs
                else:
                    # Re-raise other HTTP errors
                    raise
            
            with open(temp_video_path, 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            
            logger.info(f"Downloaded video to temporary file: {temp_video_path}")
            
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or [],
                    "categoryId": "10"  # Music category
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
            
            # Upload to YouTube
            media = MediaFileUpload(temp_video_path, resumable=True, chunksize=1024*1024)
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload with progress reporting
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Uploaded {int(status.progress() * 100)}%")
            
            # Make sure to close the media file
            media._fd.close()
            
            logger.info(f"Video upload complete: {response['id']}")
            return response["id"]
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error uploading video: {error_str}")
            
            # Check if this is an upload limit exceeded error
            if "uploadLimitExceeded" in error_str or "The user has exceeded the number of videos they may upload" in error_str:
                # Re-raise the exception to be caught by the caller
                raise
                
            return None
            
        finally:
            # Wait a moment to ensure file is released
            import time
            time.sleep(1)
            
            # Clean up temporary file with retry
            for _ in range(5):
                try:
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
                    break
                except Exception as e:
                    logger.warning(f"Failed to remove temp file, retrying: {str(e)}")
                    time.sleep(1)
    
    def reply_to_comment(self, comment_id: str, reply_text: str) -> Optional[str]:
        """
        Reply to a YouTube comment.
        
        Args:
            comment_id: The ID of the comment to reply to
            reply_text: The text of the reply
            
        Returns:
            The ID of the reply comment if successful, None otherwise
        """
        logger.info(f"Replying to comment: {comment_id}")
        
        try:
            response = self.youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": comment_id,
                        "textOriginal": reply_text
                    }
                }
            ).execute()
            
            reply_id = response.get("id")
            logger.info(f"Successfully replied to comment {comment_id} with reply ID: {reply_id}")
            return reply_id
            
        except Exception as e:
            logger.error(f"Error replying to comment {comment_id}: {str(e)}")
            return None
    
    def fetch_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch comments for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to retrieve
            
        Returns:
            List of comment data dictionaries
        """
        logger.info(f"Fetching comments for video ID: {video_id}")
        
        try:
            # Fetch comments with replies
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=max_results
            )
            response = request.execute()
            
            # Process comments
            comments = []
            for item in response.get("items", []):
                comment_id = item["id"]
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                
                # Check if we've already replied to this comment
                has_our_reply = False
                if "replies" in item and item["replies"]["comments"]:
                    for reply in item["replies"]["comments"]:
                        reply_snippet = reply["snippet"]
                        if reply_snippet.get("authorChannelId", {}).get("value") == self.channel_id:
                            has_our_reply = True
                            break
                
                comment_data = {
                    "comment_id": comment_id,
                    "author": snippet["authorDisplayName"],
                    "content": snippet["textOriginal"],
                    "timestamp": snippet["publishedAt"],
                    "has_our_reply": has_our_reply
                }
                comments.append(comment_data)
            
            logger.info(f"Retrieved {len(comments)} comments")
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return []
