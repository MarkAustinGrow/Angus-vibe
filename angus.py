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
import json
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

class SupabaseLogHandler(logging.Handler):
    """
    Custom logging handler that sends logs to a Supabase table.
    """
    def __init__(self, supabase_client):
        super().__init__()
        self.supabase = supabase_client
        
    def emit(self, record):
        try:
            # Extract exception info if present
            exc_info = None
            if record.exc_info:
                exc_info = self.formatter.formatException(record.exc_info)
            
            # Format the log message
            log_entry = {
                "level": record.levelname,
                "source": record.name,
                "message": self.format(record),
                "details": {
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "pathname": record.pathname,
                    "exc_info": exc_info
                }
            }
            
            # Insert into Supabase
            self.supabase.client.table("angus_logs").insert(log_entry).execute()
        except Exception:
            # Don't let logging errors crash the application
            self.handleError(record)

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
        
        # Add Supabase log handler
        try:
            supabase_handler = SupabaseLogHandler(self.supabase)
            supabase_handler.setLevel(logging.INFO)  # Only log INFO and above
            supabase_handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(supabase_handler)
            logger.info("Supabase log handler initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase log handler: {str(e)}")
        
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
        
        # Check if there are any existing records for this song
        existing_records = None
        try:
            existing_response = self.supabase.client.table("youtube").select("id, status").eq("song_id", song_id).execute()
            existing_records = existing_response.data if existing_response.data else []
            
            # Log existing records for debugging
            if existing_records:
                logger.info(f"Found {len(existing_records)} existing records for song '{title}'")
                for record in existing_records:
                    logger.info(f"  Record ID: {record.get('id')}, Status: {record.get('status')}")
        except Exception as e:
            logger.error(f"Error checking for existing records: {str(e)}")
            existing_records = []
        
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
                # Update or record the failure in the youtube table before re-raising
                try:
                    youtube_data = {
                        "song_id": song_id,
                        "status": "failed",
                        "title": title,
                        "description": f"Upload failed: {upload_error}"
                    }
                    
                    # Update existing record or insert new one
                    if existing_records:
                        # Update the first record
                        record_id = existing_records[0].get('id')
                        self.supabase.client.table("youtube").update(youtube_data).eq("id", record_id).execute()
                        logger.info(f"Updated existing record {record_id} with upload failure")
                    else:
                        # Insert new record
                        self.supabase.client.table("youtube").insert(youtube_data).execute()
                        logger.info(f"Inserted new record for upload failure")
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
                    # If there are existing records, update the first one and delete the rest
                    if existing_records:
                        # Update the first record
                        record_id = existing_records[0].get('id')
                        self.supabase.client.table("youtube").update(youtube_data).eq("id", record_id).execute()
                        logger.info(f"Updated existing record {record_id} with successful upload")
                        
                        # Delete any additional records
                        if len(existing_records) > 1:
                            for record in existing_records[1:]:
                                delete_id = record.get('id')
                                self.supabase.client.table("youtube").delete().eq("id", delete_id).execute()
                                logger.info(f"Deleted duplicate record {delete_id} for song '{title}'")
                    else:
                        # Insert new record
                        self.supabase.client.table("youtube").insert(youtube_data).execute()
                        logger.info(f"Inserted new record for successful upload")
                    
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
                    # If there are existing records, update the first one
                    if existing_records:
                        # Update the first record
                        record_id = existing_records[0].get('id')
                        self.supabase.client.table("youtube").update(youtube_data).eq("id", record_id).execute()
                        logger.info(f"Updated existing record {record_id} with upload failure")
                    else:
                        # Insert new record
                        self.supabase.client.table("youtube").insert(youtube_data).execute()
                        logger.info(f"Inserted new record for upload failure")
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
        existing_comments = self.supabase.client.table("feedback").select("comments, comment_id").eq("song_id", song_id).execute()
        existing_comment_texts = set()
        existing_comment_ids = set()
        if existing_comments.data:
            for item in existing_comments.data:
                if item.get('comments'):
                    existing_comment_texts.add(item.get('comments'))
                if item.get('comment_id'):
                    existing_comment_ids.add(item.get('comment_id'))
        
        # Store comments in feedback table and reply to them
        new_comments = 0
        for comment in comments:
            # Check if we've reached the maximum number of replies
            if max_replies is not None and new_comments >= max_replies:
                logger.info(f"Reached maximum number of replies ({max_replies}) for video: {youtube_id}")
                break
                
            comment_id = comment["comment_id"]
            comment_text = comment["content"]
            
            # Skip if we already have this comment ID
            if comment_id in existing_comment_ids:
                logger.info(f"Comment ID already exists in feedback table: {comment_id}")
                continue
            
            # Skip if we've already replied to this comment
            if comment.get("has_our_reply", False):
                logger.info(f"Already replied to comment: {comment_text[:30]}...")
                
                # Still store it if we don't have it yet
                if comment_id not in existing_comment_ids:
                    feedback_data = {
                        "song_id": song_id,
                        "comments": comment_text,
                        "comment_id": comment_id
                    }
                    self.supabase.client.table("feedback").insert(feedback_data).execute()
                    logger.info(f"Stored comment that already has a reply: {comment_text[:30]}...")
                
                continue
            
            try:
                # Store in feedback table
                feedback_data = {
                    "song_id": song_id,
                    "comments": comment_text,
                    "comment_id": comment_id
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
    
    def cleanup_old_logs(self, days_to_keep=7):
        """
        Remove logs older than the specified number of days.
        
        Args:
            days_to_keep: Number of days of logs to keep
            
        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        
        try:
            # Delete logs older than cutoff_date
            response = self.supabase.client.table("angus_logs").delete().lt("timestamp", cutoff_date.isoformat()).execute()
            deleted_count = len(response.data) if response.data else 0
            logger.info(f"Cleaned up {deleted_count} logs older than {days_to_keep} days")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {str(e)}")
            return 0
    
    def run_scheduled_tasks(self):
        """
        Run scheduled tasks continuously.
        
        This method sets up scheduled tasks to run at specified intervals:
        - Upload videos to YouTube every hour
        - Fetch comments from YouTube videos every hour
        - Clean up old logs every day
        
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
        
        # Define the log cleanup task
        def log_cleanup_task():
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{current_time}] Running scheduled log cleanup")
            try:
                deleted = self.cleanup_old_logs(days_to_keep=7)  # Keep logs for 7 days
                logger.info(f"[{current_time}] Scheduled log cleanup complete - deleted {deleted} old logs")
            except Exception as e:
                logger.error(f"[{current_time}] Error in scheduled log cleanup: {str(e)}")
        
        # Schedule the tasks to run every hour
        schedule.every(1).hour.do(youtube_upload_task)
        schedule.every(1).hour.do(comment_retrieval_task)
        schedule.every(1).day.at("00:00").do(log_cleanup_task)  # Run once per day at midnight
        
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
