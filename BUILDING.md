# Building Agent Angus with AI Coding Tools

This document provides detailed instructions for building Agent Angus using AI coding tools like GitHub Copilot, Claude, or ChatGPT. It breaks down the system into components and provides step-by-step guidance for implementation.

## System Architecture

Agent Angus consists of several key components:

1. **Main Agent (angus.py)**: Orchestrates the entire system, handling command-line arguments, scheduling tasks, and coordinating between components.

2. **YouTube Client (youtube_client.py)**: Handles all interactions with the YouTube API, including video uploads, comment fetching, and comment replies.

3. **Supabase Client (supabase_client.py)**: Manages database operations with Supabase, including storing video information and comments.

4. **OpenAI Utilities (openai_utils.py)**: Generates responses to YouTube comments using OpenAI's API.

5. **Database Schema (create_youtube_table.sql)**: Defines the structure of the YouTube table in Supabase.

6. **Test Scripts**: Various scripts to test different aspects of the system.

## Implementation Steps

### Step 1: Set Up Project Structure

First, create the project directory and initialize the basic file structure:

```bash
mkdir angus
cd angus
touch angus.py youtube_client.py supabase_client.py openai_utils.py create_youtube_table.sql requirements.txt .env
```

### Step 2: Define Requirements

Create a `requirements.txt` file with the necessary dependencies:

```
google-api-python-client
google-auth-oauthlib
google-auth-httplib2
supabase
requests
openai
python-dotenv
schedule
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file with the required API keys and credentials:

```
# YouTube API Credentials
YOUTUBE_API_KEY=your-api-key
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret
YOUTUBE_CHANNEL_ID=your-channel-id

# Supabase Credentials
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# OpenAI API Credentials
OPENAI_API_KEY=your-openai-api-key
```

### Step 4: Implement Configuration Module

Create a `config.py` file to load environment variables:

```python
"""
Configuration module for Agent Angus.

This module loads environment variables from a .env file and provides them as constants.
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
logger.info("Loading environment variables from .env file")
load_dotenv()

# YouTube API credentials
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# OpenAI API credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### Step 5: Implement Supabase Client

Create the `supabase_client.py` file to handle database operations:

#### AI Prompt for Supabase Client:
```
Create a Python class called SupabaseClient that handles interactions with Supabase. The class should:
1. Initialize with Supabase URL and key from environment variables
2. Have methods to list songs with pagination
3. Include error handling for all database operations
4. Use logging to track operations
```

#### Implementation:

```python
"""
Supabase client for interacting with the database.
"""
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

# Import configuration
from config import SUPABASE_URL, SUPABASE_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Client for interacting with Supabase database.
    """
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize the Supabase client.
        
        Args:
            url: Supabase URL (defaults to environment variable)
            key: Supabase key (defaults to environment variable)
        """
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        
        # Validate credentials
        if not self.url or not self.key:
            logger.error("Supabase credentials are missing!")
            raise ValueError("Supabase URL and key are required")
        
        # Initialize client
        try:
            self.client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {str(e)}")
            raise
    
    def list_songs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List songs from the songs table.
        
        Args:
            limit: Maximum number of songs to return
            offset: Number of songs to skip
            
        Returns:
            List of song data dictionaries
        """
        logger.info(f"Listing songs (limit: {limit}, offset: {offset})")
        
        try:
            response = self.client.table("songs").select("*").limit(limit).offset(offset).execute()
            
            if response.data:
                logger.info(f"Retrieved {len(response.data)} songs")
                return response.data
            else:
                logger.info("No songs found")
                return []
                
        except Exception as e:
            logger.error(f"Error listing songs: {str(e)}")
            return []
```

### Step 6: Implement YouTube Client

Create the `youtube_client.py` file to handle YouTube API operations:

#### AI Prompt for YouTube Client:
```
Create a Python class called YouTubeClient that handles interactions with the YouTube API. The class should:
1. Initialize with YouTube API credentials from environment variables
2. Handle OAuth 2.0 authentication with token persistence
3. Include methods for:
   - Uploading videos
   - Fetching comments for a video
   - Replying to comments
4. Include error handling for API rate limits and quota exceeded
5. Use logging to track operations
```

#### Implementation:

```python
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
        
        # Check if we have stored credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
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
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
        
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
        """
        logger.info(f"Uploading video: {title}")
        
        # Create a temporary file path
        temp_fd, temp_video_path = tempfile.mkstemp(suffix='.mp4')
        os.close(temp_fd)  # Close the file descriptor immediately
        
        try:
            # Download the video
            response = requests.get(video_url, stream=True)
            response.raise_for_status()  # Raise exception for HTTP errors
            
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
```

### Step 7: Implement OpenAI Utilities

Create the `openai_utils.py` file to handle OpenAI API operations:

#### AI Prompt for OpenAI Utilities:
```
Create a Python module called openai_utils.py that handles interactions with the OpenAI API. The module should:
1. Use the OpenAI API key from environment variables
2. Include a function to generate responses to YouTube comments
3. Use the OpenAI API v1.0.0+ syntax (not the older ChatCompletion.create syntax)
4. Include error handling for API issues
5. Use logging to track operations
```

#### Implementation:

```python
"""
OpenAI utilities for Agent Angus.

This module provides functions for generating responses using OpenAI.
"""
import logging
from openai import OpenAI
from typing import Optional

# Import configuration
from config import OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(comment_text: str, song_title: str, song_style: Optional[str] = None) -> Optional[str]:
    """
    Generate a response to a YouTube comment using OpenAI.
    
    Args:
        comment_text: The text of the comment
        song_title: The title of the song
        song_style: Optional style information about the song
        
    Returns:
        Generated response text
    """
    try:
        # Create a system prompt that includes context about the song
        system_prompt = f"You are a friendly assistant responding to comments on a music video for the song '{song_title}'"
        if song_style:
            system_prompt += f" which is in the style of {song_style}."
        system_prompt += " Keep responses brief (max 2 sentences), friendly, and engaging. Thank the user for their feedback."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Someone commented: '{comment_text}'. Write a brief, friendly response."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        reply_text = response.choices[0].message.content.strip()
        logger.info(f"Generated response for comment: {reply_text}")
        return reply_text
        
    except Exception as e:
        logger.error(f"Error generating response with OpenAI: {str(e)}")
        return None
```

### Step 8: Create Database Schema

Create the `create_youtube_table.sql` file to define the YouTube table schema:

#### AI Prompt for Database Schema:
```
Create a SQL script to create a YouTube table in Supabase. The table should:
1. Have a UUID primary key
2. Reference the songs table with a foreign key
3. Store YouTube video ID, title, description, and upload date
4. Include status field for tracking upload status
5. Include fields for view count and like count
6. Have appropriate indexes for efficient queries
```

#### Implementation:

```sql
-- Create the youtube table to track uploaded videos
create table if not exists youtube (
  id uuid default uuid_generate_v4() primary key,
  song_id uuid references songs(id),
  youtube_id text unique,
  title text,
  description text,
  upload_date timestamp with time zone default now(),
  status text,
  view_count integer default 0,
  like_count integer default 0
);

-- Create index for faster lookups
create index if not exists youtube_song_id_idx on youtube(song_id);
create index if not exists youtube_youtube_id_idx on youtube(youtube_id);
create index if not exists youtube_status_idx on youtube(status);

-- Add comment to explain table purpose
comment on table youtube is 'Tracks videos uploaded to YouTube from the songs table';
```

### Step 9: Implement Main Agent

Create the `angus.py` file to orchestrate the entire system:

#### AI Prompt for Main Agent:
```
Create a Python script called angus.py that implements Agent Angus. The script should:
1. Import the necessary modules (supabase_client, youtube_client, openai_utils)
2. Define a class called AgentAngus that orchestrates the system
3. Include methods for:
   - Creating the YouTube table in Supabase
   - Uploading songs to YouTube
   - Fetching comments from YouTube videos
   - Replying to comments using OpenAI
4. Include a scheduler for running tasks periodically
5. Parse command-line arguments for different operations
6. Include error handling and logging
```

#### Implementation:

```python
#!/usr/bin/env python3
"""
Agent Angus - YouTube Publishing and Feedback Collection Agent

This script automates the process of:
1. Uploading videos from Supabase songs table to YouTube
2. Tracking uploaded videos in a YouTube table
3. Retrieving and storing YouTube comments for analysis
"""
import os
import sys
import time
import logging
import argparse
import datetime
import threading
from typing import Dict, Any, List, Optional

# Import schedule library for task scheduling
try:
    import schedule
except ImportError:
    print("Schedule library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule

# Import custom modules
from supabase_client import SupabaseClient
from youtube_client import YouTubeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('angus.log')
    ]
)
logger = logging.getLogger(__name__)

class AgentAngus:
    """
    Agent Angus automates YouTube publishing and feedback collection.
    """
    
    def __init__(self):
        """
        Initialize Agent Angus.
        """
        # Initialize clients
        self.supabase = SupabaseClient()
        self.youtube = YouTubeClient()
        
        logger.info("Agent Angus initialized")
    
    def create_youtube_table(self) -> bool:
        """
        Create the YouTube table in Supabase if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read SQL file
            with open('create_youtube_table.sql', 'r') as f:
                sql = f.read()
            
            # Execute SQL
            logger.info("Creating youtube table in Supabase")
            
            # Split SQL into separate statements
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            
            for statement in statements:
                try:
                    # Execute each statement
                    self.supabase.client.postgrest.rpc('exec_sql', {'query': statement}).execute()
                except Exception as e:
                    # Log error but continue with other statements
                    logger.warning(f"Error executing SQL statement: {str(e)}")
                    logger.warning(f"Statement: {statement}")
            
            logger.info("YouTube table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating YouTube table: {str(e)}")
            return False
    
    def get_songs_to_upload(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get songs from Supabase that haven't been successfully uploaded to YouTube yet.
        
        Args:
            limit: Maximum number of songs to return
            
        Returns:
            List of song data dictionaries
        """
        logger.info(f"Getting songs to upload (limit: {limit})")
        
        try:
            # For now, we'll use the list_songs method and filter manually
            all_songs = self.supabase.list_songs(limit=50)
            
            # Get all successfully uploaded song IDs
            response = self.supabase.client.table("youtube").select("song_id").eq("status", "uploaded").execute()
            uploaded_song_ids = set()
            if response.data:
                for item in response.data:
                    uploaded_song_ids.add(item.get('song_id'))
            
            # Filter songs that have video_url and haven't been successfully uploaded
            songs_to_upload = [
                song for song in all_songs 
                if song.get('video_url') and song.get('id') not in uploaded_song_ids
            ]
            
            # Limit the number of songs
            songs_to_upload = songs_to_upload[:limit]
            
            logger.info(f"Found {len(songs_to_upload)} songs to upload")
            return songs_to_upload
            
        except Exception as e:
            logger.error(f"Error getting songs to upload: {str(e)}")
            return []
    
    def upload_song_to_youtube(self, song: Dict[str, Any]) -> Optional[str]:
        """
        Upload a song to YouTube and store the result in the youtube table.
        
        Args:
            song: Song data dictionary
            
        Returns:
            YouTube video ID if successful, None otherwise
            
        Raises:
            Exception: If there's an error during upload, including upload limit exceeded
        """
        song_id = song.get('id')
        title = song.get('title', 'Untitled Song')
        video_url = song.get('video_url')
        
        if not video_url:
            logger.warning(f"No video URL for song: {title}")
            return None
        
        logger.info(f"Uploading song '{title}' to YouTube")
        
        youtube_id = None
        upload_error = None
        
        try:
            # Prepare description
            description = song.get('gpt_description', '')
            if not description and song.get('lyrics'):
                description = f"Lyrics:\n\n{song['lyrics']}"
            
            # Prepare tags
            tags = []
            if song.get('style'):
                tags.extend([tag.strip() for tag in song['style'].split(',')])
            
            # Upload to YouTube
            youtube_id = self.youtube.upload_video(
                video_url=video_url,
                title=title,
                description=description,
                tags=tags
            )
            
            if not youtube_id:
                upload_error = "Upload failed - no YouTube ID returned"
                logger.error(f"Failed to upload song '{title}' to YouTube")
                return None
            
        except Exception as e:
            upload_error = str(e)
            logger.error(f"Error uploading song '{title}' to YouTube: {upload_error}")
            
            # Check if this is an upload limit exceeded error and re-raise it
            if "uploadLimitExceeded" in upload_error or "The user has exceeded the number of videos they may upload" in upload_error:
                # Record the failure in the youtube table before re-raising
                try:
                    youtube_data = {
                        "song_id": song_id,
                        "status": "failed",
                        "title": title,
                        "description": f"Upload failed: {upload_error}"
                    }
                    self.supabase.client.table("youtube").insert(youtube_data).execute()
                except Exception as db_error:
                    logger.error(f"Error recording upload limit failure to Supabase: {str(db_error)}")
                
                # Re-raise the exception to be caught by upload_all_pending_songs
                raise
            
            return None
        
        finally:
            # Record result in youtube table
            if youtube_id:
                # Record success
                youtube_data = {
                    "song_id": song_id,
                    "youtube_id": youtube_id,
                    "title": title,
                    "description": description,
                    "status": "uploaded"
                }
                
                try:
                    self.supabase.client.table("youtube").insert(youtube_data).execute()
                    logger.info(f"Successfully uploaded '{title}' to YouTube with ID: {youtube_id}")
                except Exception as e:
                    logger.error(f"Error recording successful upload to Supabase: {str(e)}")
            
            elif upload_error:
                # Record failure
                youtube_data = {
                    "song_id": song_id,
                    "status": "failed",
                    "title": title,
                    "description": f"Upload failed: {upload_error}"
                }
                
                try:
                    self.supabase.client.table("youtube").insert(youtube_data).execute()
                except Exception as e:
                    logger.error(f"Error recording failed upload to Supabase: {str(e)}")
        
        return youtube_id
    
    def upload_all_pending_songs(self, limit: int = 10) -> int:
        """
        Upload all pending songs to YouTube.
        
        Args:
            limit: Maximum number of songs to upload
            
        Returns:
            Number of successfully uploaded songs
        """
        logger.info(f"Uploading pending songs (limit: {limit})")
        
        # Get songs to upload
        songs = self.get_songs_to_upload(limit=limit)
        
        if not songs:
            logger.info("No songs found to upload")
            return 0
        
        # Upload each song
        successful_uploads = 0
        upload_limit_exceeded = False
        
        for song in songs:
            # Skip remaining uploads if we've hit the YouTube upload limit
            if upload_limit_exceeded:
                logger.warning(f"Skipping upload of '{song.get('title')}' due to YouTube upload limit")
                continue
                
            try:
                youtube_id = self.upload_song_to_youtube(song)
                if youtube_id:
                    successful_uploads += 1
                
                # Add a small delay between uploads to avoid rate limiting
                if len(songs) > 1:
                    time.sleep(2)
                    
            except Exception as e:
                error_str = str(e)
                # Check if this is an upload limit exceeded error
                if "uploadLimitExceeded" in error_str or "The user has exceeded the number of videos they may upload" in error_str:
                    logger.warning("YouTube upload limit exceeded. Stopping further uploads.")
                    upload_limit_exceeded = True
                else:
                    logger.error(f"Error uploading song '{song.get('title')}': {error_str}")
        
        logger.info(f"Uploaded {successful_uploads} out of {len(songs)} songs")
        
        # Return a special code if we hit the upload limit
        if upload_limit_exceeded:
            logger.warning("YouTube upload limit reached. Will try again in the next scheduled run.")
        
        return successful_uploads
    
    def fetch_comments_for_video(self, youtube_id: str, song_id: str = None, max_replies: int = None) -> int:
        """
        Fetch comments for a YouTube video, store them in the feedback table,
        and reply to them using OpenAI.
        
        Args:
            youtube_id: YouTube video ID
            song_id: Optional song ID (if not provided, will be looked up)
            max_replies: Maximum number of replies to post (None for unlimited)
            
        Returns:
            Number of comments fetched and stored
        """
        logger.info(f"Fetching comments for YouTube video: {youtube_id}")
        
        # Get song_id and title if not provided
        song_title = "Unknown Song"
        song_style = None
        if not song_id:
            response = self.supabase.client.table("youtube").select("song_id,title").eq("youtube_id", youtube_id).execute()
            if response.data and len(response.data) > 0:
                song_id = response.data[0].get('song_id')
                song_title = response.data[0].get('title', song_title)
            else:
                logger.warning(f"No record found for YouTube ID: {youtube_id}")
                return 0
        else:
            # Get song title and style
            response = self.supabase.client.table("songs").select("title,style").eq("id", song_id).execute()
            if response.data and len(response.data) > 0:
                song_title = response.data[0].get('title', song_title)
                song_style = response.data[0].get('style')
        
        # Fetch comments from YouTube
        comments = self.youtube.fetch_comments(youtube_id)
        
        if not comments:
            logger.info(f"No comments found for video: {youtube_id}")
            return 0
        
        # Get existing comments for this song to avoid duplicates
        existing_comments = self.supabase.client.table("feedback").select("comments").eq("song_id", song_id).execute()
        existing_comment_texts = set()
        if existing_comments.data:
            for item in existing_comments.data:
                if item.get('comments'):
                    existing_comment_texts.add(item.get('comments'))
        
        # Store comments in feedback table and reply to them
        new_comments = 0
        for comment in comments:
            # Check if we've reached the maximum number of replies
            if max_replies is not None and new_comments >= max_replies:
                logger.info(f"Reached maximum number of replies ({max_replies}) for video: {youtube_id}")
                break
                
            comment_id = comment["comment_id"]
            comment_text = comment["content"]
            
            # Skip if we already have this comment text
            if comment_text in existing_comment_texts:
                logger.info(f"Comment already exists in feedback table: {comment_text[:30]}...")
                continue
            
            # Skip if we've already replied to this comment
            if comment.get("has_our_reply", False):
                logger.info(f"Already replied to comment: {comment_text[:30]}...")
                
                # Still store it if we don't have it yet
                if comment_text not in existing_comment_texts:
                    feedback_data = {
                        "song_id": song_id,
                        "comments": comment_text,
                    }
                    self.supabase.client.table("feedback").insert(feedback_data).execute()
                    logger.info(f"Stored comment that already has a reply: {comment_text[:30]}...")
                
                continue
            
            try:
                # Store in feedback table
                feedback_data = {
                    "song_id": song_id,
                    "comments": comment_text,
                }
                
                # Insert into feedback table
                self.supabase.client.table("feedback").insert(feedback_data).execute()
                
                # Generate a response using OpenAI
                from openai_utils import generate_response
                response_text = generate_response(comment_text, song_title, song_style)
                
                if response_text:
                    # Reply to the comment
                    reply_id = self.youtube.reply_to_comment(comment_id, response_text)
                    
                    if reply_id:
                        logger.info(f"Successfully replied to comment: {comment_text[:30]}...")
                        new_comments += 1
                
            except Exception as e:
                logger.error(f"Error processing comment {comment_id}: {str(e)}")
        
        logger.info(f"Processed {new_comments} new comments for video: {youtube_id}")
        return new_comments
    
    def fetch_comments_for_all_videos(self, limit: int = 10, max_total_replies: int = 10) -> int:
        """
        Fetch comments for all uploaded YouTube videos.
        
        Args:
            limit: Maximum number of videos to process
            max_total_replies: Maximum total number of replies to post across all videos
            
        Returns:
            Total number of comments fetched
        """
        logger.info(f"Fetching comments for all videos (limit: {limit}, max_replies: {max_total_replies})")
        
        try:
            # Get uploaded videos
            response = self.supabase.client.table("youtube").select("youtube_id,song_id").eq("status", "uploaded").limit(limit).execute()
            
            if not response.data:
                logger.info("No uploaded videos found")
                return 0
            
            # Fetch comments for each video
            total_comments = 0
            remaining_replies = max_total_replies
            
            for video in response.data:
                youtube_id = video.get('youtube_id')
                song_id = video.get('song_id')
                
                if youtube_id:
                    # Calculate how many replies to allow for this video
                    # If we have 5 videos and want 10 total replies, allocate 2 per video
                    # But if we've already used some replies, adjust accordingly
                    replies_per_video = max(1, remaining_replies // len(response.data))
                    
                    # Fetch comments and limit replies for this video
                    comments_count = self.fetch_comments_for_video(youtube_id, song_id, max_replies=replies_per_video)
                    total_comments += comments_count
                    
                    # Update remaining replies
                    remaining_replies -= comments_count
                    
                    # If we've reached the maximum total replies, stop
                    if remaining_replies <= 0:
                        logger.info(f"Reached maximum total replies ({max_total_replies})")
                        break
                
                # Add a small delay between requests to avoid rate limiting
                if len(response.data) > 1:
                    time.sleep(1)
            
            logger.info(f"Fetched a total of {total_comments} comments from {len(response.data)} videos")
            return total_comments
            
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return 0
    
    def run_scheduled_tasks(self):
        """
        Run scheduled tasks continuously.
        
        This method sets up scheduled tasks to run at specified intervals:
        - Upload videos to YouTube every hour
        - Fetch comments from YouTube videos every hour
        
        The method runs indefinitely until interrupted.
        """
        logger.info("Starting scheduled task runner")
        
        # Define the YouTube upload task
        def youtube_upload_task():
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{current_time}] Running scheduled YouTube upload")
            try:
                uploaded = self.upload_all_pending_songs(limit=1)  # Only upload 1 video at a time
                logger.info(f"[{current_time}] Scheduled upload complete - uploaded {uploaded} videos")
            except Exception as e:
                logger.error(f"[{current_time}] Error in scheduled upload: {str(e)}")
        
        # Define the comment retrieval task
        def comment_retrieval_task():
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{current_time}] Running scheduled comment retrieval")
            try:
                comments = self.fetch_comments_for_all_videos(limit=10, max_total_replies=10)
                logger.info(f"[{current_time}] Scheduled comment retrieval complete - fetched {comments} comments")
            except Exception as e:
                logger.error(f"[{current_time}] Error in scheduled comment retrieval: {str(e)}")
        
        # Schedule the tasks to run every hour
        schedule.every(1).hour.do(youtube_upload_task)
        schedule.every(1).hour.do(comment_retrieval_task)
        
        # Run the tasks immediately on startup
        logger.info("Running initial tasks on startup")
        youtube_upload_task()
        comment_retrieval_task()
        
        # Run the scheduler loop
        logger.info("Entering scheduler loop - Agent Angus is now running continuously")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for pending tasks
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user - shutting down")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                # Continue running despite errors
                time.sleep(60)

def main():
    """
    Main entry point for Agent Angus.
    """
    parser = argparse.ArgumentParser(description='Agent Angus - YouTube Publishing and Feedback Collection')
    parser.add_argument('--create-table', action='store_true', help='Create the YouTube table in Supabase')
    parser.add_argument('--upload', action='store_true', help='Upload pending songs to YouTube')
    parser.add_argument('--fetch-comments', action='store_true', help='Fetch comments for uploaded videos')
    parser.add_argument('--limit', type=int, default=1, help='Limit the number of items to process (default: 1)')
    parser.add_argument('--max-replies', type=int, default=10, help='Maximum number of comment replies to post (default: 10)')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode with scheduled tasks')
    
    args = parser.parse_args()
    
    # Initialize Agent Angus
    angus = AgentAngus()
    
    # Run in daemon mode if requested
    if args.daemon:
        try:
            logger.info("Starting Agent Angus in daemon mode")
            # Create the YouTube table if it doesn't exist
            angus.create_youtube_table()
            # Run scheduled tasks (this will run indefinitely)
            angus.run_scheduled_tasks()
        except KeyboardInterrupt:
            logger.info("Daemon mode terminated by user")
        return
    
    # Create YouTube table if requested
    if args.create_table:
        angus.create_youtube_table()
    
    # Upload songs if requested
    if args.upload:
        angus.upload_all_pending_songs(limit=args.limit)
    
    # Fetch comments if requested
    if args.fetch_comments:
        angus.fetch_comments_for_all_videos(limit=args.limit, max_total_replies=args.max_replies)
    
    # If no specific action was requested, show help
    if not (args.create_table or args.upload or args.fetch_comments or args.daemon):
        parser.print_help()

if __name__ == "__main__":
    main()
```

### Step 10: Implement Test Scripts

Now let's create some test scripts to verify different aspects of the system:

#### AI Prompt for Test Scripts:
```
Create a set of Python test scripts for Agent Angus:
1. test_openai_response.py - Tests OpenAI response generation
2. test_youtube_reply.py - Tests YouTube comment reply functionality
3. test_comment_response_flow.py - Tests the complete comment response flow
```

#### Implementation of test_openai_response.py:

```python
#!/usr/bin/env python3
"""
Test script for OpenAI comment response feature.

This script tests the OpenAI comment response generation without requiring
actual new YouTube comments. It simulates a comment and generates a response.
"""
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the OpenAI utilities
from openai_utils import generate_response

# Test comment and song details
test_comment = "This song is amazing! I love the beat and the lyrics are so meaningful."
test_song_title = "Cosmic Dreams"
test_song_style = "Electronic, Ambient"

def test_openai_response():
    """
    Test the OpenAI response generation.
    """
    logger.info(f"Testing OpenAI response generation for comment: '{test_comment}'")
    logger.info(f"Song title: '{test_song_title}'")
    logger.info(f"Song style: '{test_song_style}'")
    
    try:
        # Generate a response
        response = generate_response(test_comment, test_song_title, test_song_style)
        
        if response:
            logger.info(f"Successfully generated response: '{response}'")
            return True
        else:
            logger.error("Failed to generate a response")
            return False
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_response()
    sys.exit(0 if success else 1)
```

#### Implementation of test_youtube_reply.py:

```python
#!/usr/bin/env python3
"""
Test script for YouTube comment reply functionality.

This script tests the ability to reply to YouTube comments without
requiring actual new comments. It uses a specified video ID and comment ID.
"""
import logging
import sys
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the YouTube client
from youtube_client import YouTubeClient
from openai_utils import generate_response

def test_youtube_reply(video_id, comment_id=None):
    """
    Test the YouTube comment reply functionality.
    
    Args:
        video_id: The YouTube video ID to fetch comments from
        comment_id: Optional specific comment ID to reply to
    """
    logger.info(f"Testing YouTube comment reply for video: {video_id}")
    
    try:
        # Initialize the YouTube client
        youtube = YouTubeClient()
        
        # Fetch comments for the video
        comments = youtube.fetch_comments(video_id)
        
        if not comments:
            logger.error(f"No comments found for video: {video_id}")
            return False
        
        logger.info(f"Found {len(comments)} comments")
        
        # If a specific comment ID is provided, find it
        if comment_id:
            target_comment = next((c for c in comments if c["comment_id"] == comment_id), None)
            if not target_comment:
                logger.error(f"Comment ID {comment_id} not found in video {video_id}")
                return False
            comments = [target_comment]
        else:
            # Otherwise, use the first comment that doesn't have our reply
            comments = [c for c in comments if not c.get("has_our_reply", False)]
            if not comments:
                logger.error("All comments already have replies")
                return False
        
        # Generate and post a reply for the selected comment
        for comment in comments[:1]:  # Just use the first comment
            comment_id = comment["comment_id"]
            comment_text = comment["content"]
            
            logger.info(f"Selected comment: '{comment_text}'")
            
            # Generate a response using OpenAI
            response_text = generate_response(comment_text, f"Test Video {video_id}", "Test Style")
            
            if not response_text:
                logger.error("Failed to generate a response")
                continue
            
            logger.info(f"Generated response: '{response_text}'")
            
            # Reply to the comment
            reply_id = youtube.reply_to_comment(comment_id, response_text)
            
            if reply_id:
                logger.info(f"Successfully replied to comment with reply ID: {reply_id}")
                return True
            else:
                logger.error("Failed to post reply")
                return False
        
        return False
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test YouTube comment reply functionality')
    parser.add_argument('--video-id', required=True, help='YouTube video ID to fetch comments from')
    parser.add_argument('--comment-id', help='Specific comment ID to reply to (optional)')
    
    args = parser.parse_args()
    
    success = test_youtube_reply(args.video_id, args.comment_id)
    sys.exit(0 if success else 1)
```

#### Implementation of test_comment_response_flow.py:

```python
#!/usr/bin/env python3
"""
Test script for the complete comment response flow.

This script tests the entire flow from fetching comments to generating
responses and posting replies. It simulates the behavior of the
fetch_comments_for_video method in AgentAngus.
"""
import logging
import sys
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the necessary modules
from youtube_client import YouTubeClient
from openai_utils import generate_response

def test_comment_response_flow(video_id):
    """
    Test the complete comment response flow.
    
    Args:
        video_id: The YouTube video ID to fetch comments from
    """
    logger.info(f"Testing complete comment response flow for video: {video_id}")
    
    try:
        # Initialize the YouTube client
        youtube = YouTubeClient()
        
        # Fetch comments for the video
        comments = youtube.fetch_comments(video_id)
        
        if not comments:
            logger.error(f"No comments found for video: {video_id}")
            return False
        
        logger.info(f"Found {len(comments)} comments")
        
        # Filter comments that don't have our reply
        comments_without_replies = [c for c in comments if not c.get("has_our_reply", False)]
        
        if not comments_without_replies:
            logger.info("All comments already have replies")
            return True
        
        logger.info(f"Found {len(comments_without_replies)} comments without replies")
        
        # Process each comment
        successful_replies = 0
        for comment in comments_without_replies:
            comment_id = comment["comment_id"]
            comment_text = comment["content"]
            
            logger.info(f"Processing comment: '{comment_text}'")
            
            # Generate a response using OpenAI
            song_title = f"Test Video {video_id}"
            song_style = "Test Style"
            response_text = generate_response(comment_text, song_title, song_style)
            
            if not response_text:
                logger.error("Failed to generate a response")
                continue
            
            logger.info(f"Generated response: '{response_text}'")
            
            # Reply to the comment
            reply_id = youtube.reply_to_comment(comment_id, response_text)
            
            if reply_id:
                logger.info(f"Successfully replied to comment with reply ID: {reply_id}")
                successful_replies += 1
            else:
                logger.error("Failed to post reply")
        
        logger.info(f"Successfully replied to {successful_replies} out of {len(comments_without_replies)} comments")
        return successful_replies > 0
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test complete comment response flow')
    parser.add_argument('--video-id', required=True, help='YouTube video ID to fetch comments from')
    
    args = parser.parse_args()
    
    success = test_comment_response_flow(args.video_id)
    sys.exit(0 if success else 1)
```

### Step 11: Create Run Scripts

Create batch and shell scripts to run Agent Angus with common commands:

#### Implementation of run_angus.bat (for Windows):

```batch
@echo off
REM Batch script to run Agent Angus with common commands

REM Function to display help
:show_help
echo Agent Angus - YouTube Publishing and Feedback Collection
echo.
echo Usage: run_angus.bat [command] [options]
echo.
echo Commands:
echo   setup       Create the YouTube table in Supabase
echo   upload      Upload pending songs to YouTube
echo   comments    Fetch comments for uploaded videos
echo   daemon      Run in daemon mode with scheduled tasks
echo   test        Run tests in simulation mode
echo   help        Show this help message
echo.
echo Options:
echo   --limit N   Limit the number of items to process (default: 10)
echo   --simulate  Run in simulation mode without making actual API calls
echo.
echo Examples:
echo   run_angus.bat setup
echo   run_angus.bat upload --limit 5
echo   run_angus.bat comments --limit 10
echo   run_angus.bat upload --simulate
echo   run_angus.bat test
goto :eof

REM Default values
set LIMIT=10
set SIMULATE=

REM Parse command
set COMMAND=%1
shift

REM Parse options
:parse_args
if "%1"=="" goto execute_command
if "%1"=="--limit" (
    set LIMIT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--simulate" (
    set SIMULATE=--simulate
    shift
    goto parse_args
)
echo Unknown option: %1
call :show_help
exit /b 1

REM Execute command
:execute_command
if "%COMMAND%"=="setup" (
    echo Creating YouTube table in Supabase...
    python angus.py --create-table %SIMULATE%
    goto :eof
)
if "%COMMAND%"=="upload" (
    echo Uploading songs to YouTube (limit: %LIMIT%)...
    python angus.py --upload --limit %LIMIT% %SIMULATE%
    goto :eof
)
if "%COMMAND%"=="comments" (
    echo Fetching comments for uploaded videos (limit: %LIMIT%)...
    python angus.py --fetch-comments --limit %LIMIT% %SIMULATE%
    goto :eof
)
if "%COMMAND%"=="daemon" (
    echo Starting Agent Angus in daemon mode...
    python angus.py --daemon
    goto :eof
)
if "%COMMAND%"=="test" (
    echo Running tests in simulation mode...
    python test_angus.py
    goto :eof
)
if "%COMMAND%"=="help" (
    call :show_help
    goto :eof
)
echo Unknown command: %COMMAND%
call :show_help
exit /b 1
```

#### Implementation of run_angus.sh (for Unix-based systems):

```bash
#!/bin/bash
# Script to run Agent Angus with common commands

# Function to display help
show_help() {
    echo "Agent Angus - YouTube Publishing and Feedback Collection"
    echo ""
    echo "Usage: ./run_angus.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  setup       Create the YouTube table in Supabase"
    echo "  upload      Upload pending songs to YouTube"
    echo "  comments    Fetch comments for uploaded videos"
    echo "  daemon      Run in daemon mode with scheduled tasks"
    echo "  test        Run tests in simulation mode"
    echo "  help        Show this help message"
    echo ""
    echo "Options:"
    echo "  --limit N   Limit the number of items to process (default: 10)"
    echo "  --simulate  Run in simulation mode without making actual API calls"
    echo ""
    echo "Examples:"
    echo "  ./run_angus.sh setup"
    echo "  ./run_angus.sh upload --limit 5"
    echo "  ./run_angus.sh comments --limit 10"
    echo "  ./run_angus.sh upload --simulate"
    echo "  ./run_angus.sh test"
}

# Default values
LIMIT=10
SIMULATE=""

# Parse command
COMMAND=$1
shift

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --limit)
            LIMIT=$2
            shift 2
            ;;
        --simulate)
            SIMULATE="--simulate"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    setup)
        echo "Creating YouTube table in Supabase..."
        python angus.py --create-table $SIMULATE
        ;;
    upload)
        echo "Uploading songs to YouTube (limit: $LIMIT)..."
        python angus.py --upload --limit $LIMIT $SIMULATE
        ;;
    comments)
        echo "Fetching comments for uploaded videos (limit: $LIMIT)..."
        python angus.py --fetch-comments --limit $LIMIT $SIMULATE
        ;;
    daemon)
        echo "Starting Agent Angus in daemon mode..."
        python angus.py --daemon
        ;;
    test)
        echo "Running tests in simulation mode..."
        python test_angus.py
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
```

## Building with AI Coding Tools

When using AI coding tools like GitHub Copilot, Claude, or ChatGPT to build Agent Angus, follow these guidelines:

1. **Start with the architecture**: Provide the AI with the system architecture and component breakdown first.

2. **Implement one component at a time**: Focus on implementing one component at a time, starting with the configuration and client modules.

3. **Use the provided prompts**: The AI prompts provided in this document are designed to guide the AI in generating the correct code for each component.

4. **Review and refine**: After the AI generates code for a component, review it for correctness and refine as needed.

5. **Test incrementally**: Test each component as it's implemented to ensure it works correctly before moving on to the next component.

6. **Integrate components**: Once all components are implemented and tested individually, integrate them and test the complete system.

## Testing the System

After building the system, test it using the provided test scripts:

1. Test OpenAI response generation:
   ```bash
   python test_openai_response.py
   ```

2. Test YouTube comment reply functionality:
   ```bash
   python test_youtube_reply.py --video-id VIDEO_ID
   ```

3. Test the complete comment response flow:
   ```bash
   python test_comment_response_flow.py --video-id VIDEO_ID
   ```

4. Run Agent Angus in daemon mode:
   ```bash
   python angus.py --daemon
   ```

## Conclusion

By following this guide, you can build Agent Angus using AI coding tools. The system automates the process of uploading videos to YouTube, tracking them in a database, and responding to comments using OpenAI-generated responses.

The modular architecture makes it easy to extend and maintain, and the comprehensive test scripts ensure that each component works correctly.
