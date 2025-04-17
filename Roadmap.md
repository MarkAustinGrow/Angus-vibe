# Revised Project Roadmap for Agent Angus

## Overview

**Goal**: Build an AI agent named **Angus** that automates YouTube publishing and audience feedback collection. Angus will:
1. **Upload existing songs from Supabase** to YouTube
2. **Track uploaded videos** in a new YouTube table
3. **Retrieve and store YouTube comments** in the Supabase database for analysis

This will be an **agentic system**, allowing **Angus** to act autonomously, using external APIs and integrating with other AI agents.

---

## Phases

1. **Initialize the Project** ✅  
2. **Create YouTube Table in Supabase** ✅  
3. **Implement YouTube Video Upload Tool** ✅  
4. **Implement YouTube Comment Retrieval Tool** ✅  
5. **Iteration & Refinement** 🔄

---

## 1. Initialize the Project ✅

1. **Set Up Repo** ✅  
   - Create a new repository (e.g., GitHub or GitLab) to manage code, including:
     - `roadmap_angus.md` (this document)
     - Scripts for video upload and comment retrieval
     - Code for integrating with Supabase

2. **Establish Local Dev Environment** ✅  
   - Use existing Python environment
   - Choose YouTube API library (e.g., `google-api-python-client`)

3. **Install Required Dependencies** ✅  
   - For Python:
     ```bash
     pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client supabase
     ```

---

## 2. Create YouTube Table in Supabase ✅

1. **Design YouTube Table Schema** ✅

   | Field Name      | Type        | Description                                  |
   |----------------|------------|----------------------------------------------|
   | `id` (PK)      | `uuid`      | Unique ID, primary key (auto-generated)     |
   | `song_id`      | `uuid`      | Reference to songs table                    |
   | `youtube_id`   | `text`      | YouTube video ID                            |
   | `title`        | `text`      | Video title on YouTube                      |
   | `description`  | `text`      | Video description on YouTube                |
   | `upload_date`  | `timestamp` | Timestamp of when the video was uploaded    |
   | `status`       | `text`      | Upload status (e.g., "pending", "uploaded", "failed") |
   | `view_count`   | `integer`   | Number of views (can be updated periodically) |
   | `like_count`   | `integer`   | Number of likes (can be updated periodically) |

2. **Create Table in Supabase** ✅ (via SQL):
   ```sql
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
   ```

---

## 3. Implement YouTube Video Upload Tool ✅

1. **Create YouTube Authentication Module** ✅
   - Implement OAuth 2.0 authentication using the YouTube API credentials
   - Store tokens securely

2. **Develop Video Upload Function** ✅
   - Create a function to upload videos to YouTube using the YouTube Data API v3
   - Use the video_url field from the songs table to download the video file
   - Use title, gpt_description, and other fields for YouTube metadata

3. **Implement Upload Tracking** ✅
   - Record upload status in the youtube table
   - Handle success/failure scenarios

### Python Script for Uploading Videos from Supabase

```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from supabase import create_client
import os
import pickle
import requests
import tempfile

# YouTube API setup
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secret.json"  # From YouTube API credentials

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_youtube_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def upload_song_to_youtube(song_id):
    # Get song data from Supabase
    response = supabase.table("songs").select("*").eq("id", song_id).execute()
    
    if not response.data or len(response.data) == 0:
        print(f"No song found with ID: {song_id}")
        return None
    
    song = response.data[0]
    
    # Check if video URL exists
    if not song.get('video_url'):
        print(f"No video URL for song: {song.get('title')}")
        return None
    
    # Download video file to temporary location
    video_url = song['video_url']
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        response = requests.get(video_url, stream=True)
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_video_path = temp_file.name
    
    try:
        # Prepare YouTube upload
        creds = get_youtube_credentials()
        youtube = build("youtube", "v3", credentials=creds)
        
        # Prepare video metadata
        title = song.get('title', 'Untitled Song')
        description = song.get('gpt_description', '')
        if not description and song.get('lyrics'):
            description = f"Lyrics:\n\n{song['lyrics']}"
        
        tags = []
        if song.get('style'):
            tags.extend(song['style'].split(','))
        
        # Upload to YouTube
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "10"  # Music category
                },
                "status": {
                    "privacyStatus": "public"
                }
            },
            media_body=MediaFileUpload(temp_video_path)
        )
        
        # Execute upload
        response = request.execute()
        youtube_id = response["id"]
        
        # Store in youtube table
        youtube_data = {
            "song_id": song_id,
            "youtube_id": youtube_id,
            "title": title,
            "description": description,
            "status": "uploaded"
        }
        
        supabase.table("youtube").insert(youtube_data).execute()
        
        print(f"Successfully uploaded {title} to YouTube with ID: {youtube_id}")
        return youtube_id
        
    except Exception as e:
        print(f"Error uploading to YouTube: {str(e)}")
        
        # Record failure in youtube table
        youtube_data = {
            "song_id": song_id,
            "status": "failed",
            "title": song.get('title', 'Untitled Song'),
            "description": f"Upload failed: {str(e)}"
        }
        supabase.table("youtube").insert(youtube_data).execute()
        return None
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

def upload_all_songs():
    # Get all songs with video URLs that haven't been uploaded yet
    query = """
    SELECT s.id FROM songs s
    LEFT JOIN youtube y ON s.id = y.song_id
    WHERE s.video_url IS NOT NULL AND y.id IS NULL
    """
    response = supabase.rpc('execute_sql', {'query': query}).execute()
    
    if not response.data:
        print("No songs found to upload")
        return
    
    for song_data in response.data:
        song_id = song_data['id']
        print(f"Uploading song ID: {song_id}")
        upload_song_to_youtube(song_id)
```

---

## 4. Implement YouTube Comment Retrieval Tool ✅

1. **Create Comment Fetching Function** ✅
   - Develop a function to retrieve comments for uploaded videos
   - Store comments in a comments table with reference to the youtube table

2. **Implement Periodic Comment Updates** ✅
   - Set up a scheduler to periodically fetch new comments

### Python Script for Retrieving Comments

```python
def fetch_comments_for_video(youtube_id):
    # Get YouTube API client
    creds = get_youtube_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    
    # Fetch comments
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=youtube_id,
        maxResults=100
    )
    response = request.execute()
    
    # Get song_id from youtube table
    youtube_record = supabase.table("youtube").select("song_id").eq("youtube_id", youtube_id).execute()
    if not youtube_record.data:
        print(f"No record found for YouTube ID: {youtube_id}")
        return
    
    song_id = youtube_record.data[0]['song_id']
    
    # Process and store comments
    comments = []
    for item in response.get("items", []):
        comment_id = item["id"]
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        
        comment_data = {
            "video_id": youtube_id,
            "song_id": song_id,
            "comment_id": comment_id,
            "author": snippet["authorDisplayName"],
            "content": snippet["textOriginal"],
            "timestamp": snippet["publishedAt"]
        }
        comments.append(comment_data)
    
    # Store in comments table
    if comments:
        supabase.table("comments").insert(comments).execute()
        print(f"Stored {len(comments)} comments for video: {youtube_id}")
```

---

## 5. Iteration & Refinement 🔄

1. **Automate Angus' Workflow** ✅  
   - Implement daemon mode with continuous operation ✅
     - Add a scheduler to run tasks at specified intervals ✅
     - Implement proper logging for scheduled operations ✅
     - Add graceful shutdown handling ✅
   
   - **Optimize Hourly Video Upload** ✅
     - Upload exactly one video per hour (instead of up to 3) ✅
     - Implement a queue system to ensure videos are uploaded in the correct order ✅
     - Select the next video based on creation date (oldest first) ✅
     - Add detailed logging to track when each video is scheduled for upload ✅
     - Example implementation:
       ```python
       def youtube_upload_task():
           # Get only the next video to upload
           songs = self.get_songs_to_upload(limit=1)
           if songs:
               logger.info(f"Uploading next video in queue: {songs[0].get('title')}")
               self.upload_song_to_youtube(songs[0])
           else:
               logger.info("No pending videos to upload")
       ```
   
   - **Strengthen Duplicate Upload Prevention** ✅
     - Implement robust SQL query to properly check for already uploaded videos ✅
     - Add a status field update mechanism to mark songs as "pending", "uploaded", or "failed" ✅
     - Create a verification step that checks YouTube for the video before marking as successfully uploaded ✅
     - Example query:
       ```sql
       -- More robust query to find songs not yet uploaded
       SELECT s.* FROM songs s
       LEFT JOIN youtube y ON s.id = y.song_id
       WHERE s.video_url IS NOT NULL 
       AND (y.id IS NULL OR y.status = 'failed')
       ORDER BY s.created_at ASC
       LIMIT 1
       ```
   
   - **Improve Comment Collection Tracking** ✅
     - Enhance the processed_comments table schema to include more metadata ✅
     - Implement a more efficient comment comparison algorithm to ensure no duplicates ✅
     - Add periodic verification to check for comment consistency between YouTube and the database ✅
     - Example schema:
       ```sql
       CREATE TABLE IF NOT EXISTS processed_comments (
           id SERIAL PRIMARY KEY,
           comment_id TEXT UNIQUE,
           video_id TEXT,
           content_hash TEXT,  -- Hash of comment content for verification
           processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
           last_verified_at TIMESTAMP WITH TIME ZONE
       );
       ```
   
   - Handle YouTube API rate limits and quotas ✅

2. **Expand Functionality** 🔄  
   - Add YouTube analytics tracking ⏳
   - Implement comment sentiment analysis 🔄

3. **Integrate with Other Agents** ⏳  
   - Allow **Agent Yona** to analyze feedback and refine music ⏳

4. **Security & Access** ✅  
   - Protect API keys and credentials ✅

---

## Summary

This revised roadmap details how to:
1. Upload existing songs from your Supabase database to YouTube ✅
2. Track uploaded videos in a new "youtube" table ✅
3. Retrieve and store YouTube comments for analysis ✅

The implementation will leverage your existing database structure and YouTube API credentials to create an autonomous publishing and feedback collection system.

## Status Legend
- ✅ Completed
- 🔄 In Progress
- ⏳ Pending
