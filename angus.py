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
            # Query to find songs with video_url that haven't been successfully uploaded to YouTube yet
            query = """
            SELECT s.* FROM songs s
            WHERE s.video_url IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM youtube y 
                WHERE y.song_id = s.id 
                AND y.status = 'uploaded'
            )
            ORDER BY s.created_at DESC
            LIMIT $1
            """
            
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
    
    def fetch_comments_for_video(self, youtube_id: str, song_id: str = None) -> int:
        """
        Fetch comments for a YouTube video and store them in the feedback table.
        
        Args:
            youtube_id: YouTube video ID
            song_id: Optional song ID (if not provided, will be looked up)
            
        Returns:
            Number of comments fetched and stored
        """
        logger.info(f"Fetching comments for YouTube video: {youtube_id}")
        
        # Get song_id if not provided
        if not song_id:
            response = self.supabase.client.table("youtube").select("song_id").eq("youtube_id", youtube_id).execute()
            if response.data and len(response.data) > 0:
                song_id = response.data[0].get('song_id')
            else:
                logger.warning(f"No record found for YouTube ID: {youtube_id}")
                return 0
        
        # Fetch comments from YouTube
        comments = self.youtube.fetch_comments(youtube_id)
        
        if not comments:
            logger.info(f"No comments found for video: {youtube_id}")
            return 0
        
        # Get existing comment IDs to avoid duplicates
        try:
            # Create a tracking table if it doesn't exist
            self.supabase.client.postgrest.rpc('exec_sql', {
                'query': """
                CREATE TABLE IF NOT EXISTS processed_comments (
                    id SERIAL PRIMARY KEY,
                    comment_id TEXT UNIQUE,
                    video_id TEXT,
                    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
            }).execute()
            
            # Get already processed comment IDs
            response = self.supabase.client.postgrest.rpc('exec_sql', {
                'query': f"SELECT comment_id FROM processed_comments WHERE video_id = '{youtube_id}'"
            }).execute()
            
            processed_comment_ids = set()
            if response.data:
                for row in response.data:
                    processed_comment_ids.add(row.get('comment_id'))
            
            logger.info(f"Found {len(processed_comment_ids)} already processed comments")
            
        except Exception as e:
            logger.warning(f"Error checking processed comments: {str(e)}")
            processed_comment_ids = set()
        
        # Store comments in feedback table
        new_comments = 0
        for comment in comments:
            comment_id = comment["comment_id"]
            
            # Skip already processed comments
            if comment_id in processed_comment_ids:
                continue
            
            try:
                # Store in feedback table
                feedback_data = {
                    "song_id": song_id,
                    "comments": comment["content"],
                    # Rating is null by default, could be set based on sentiment analysis
                }
                
                # Insert into feedback table
                self.supabase.client.table("feedback").insert(feedback_data).execute()
                
                # Mark comment as processed
                self.supabase.client.table("processed_comments").insert({
                    "comment_id": comment_id,
                    "video_id": youtube_id
                }).execute()
                
                new_comments += 1
                
            except Exception as e:
                logger.error(f"Error storing comment {comment_id}: {str(e)}")
        
        logger.info(f"Stored {new_comments} new comments in feedback table for video: {youtube_id}")
        return new_comments
    
    def fetch_comments_for_all_videos(self, limit: int = 10) -> int:
        """
        Fetch comments for all uploaded YouTube videos.
        
        Args:
            limit: Maximum number of videos to process
            
        Returns:
            Total number of comments fetched
        """
        logger.info(f"Fetching comments for all videos (limit: {limit})")
        
        try:
            # Get uploaded videos
            response = self.supabase.client.table("youtube").select("youtube_id,song_id").eq("status", "uploaded").limit(limit).execute()
            
            if not response.data:
                logger.info("No uploaded videos found")
                return 0
            
            # Fetch comments for each video
            total_comments = 0
            for video in response.data:
                youtube_id = video.get('youtube_id')
                song_id = video.get('song_id')
                
                if youtube_id:
                    comments_count = self.fetch_comments_for_video(youtube_id, song_id)
                    total_comments += comments_count
                
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
                comments = self.fetch_comments_for_all_videos(limit=10)
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
        angus.fetch_comments_for_all_videos(limit=args.limit)
    
    # If no specific action was requested, show help
    if not (args.create_table or args.upload or args.fetch_comments or args.daemon):
        parser.print_help()

if __name__ == "__main__":
    main()
