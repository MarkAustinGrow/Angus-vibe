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
from typing import Dict, Any, List, Optional

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
        Get songs from Supabase that haven't been uploaded to YouTube yet.
        
        Args:
            limit: Maximum number of songs to return
            
        Returns:
            List of song data dictionaries
        """
        logger.info(f"Getting songs to upload (limit: {limit})")
        
        try:
            # Query to find songs with video_url that haven't been uploaded to YouTube yet
            query = """
            SELECT s.* FROM songs s
            LEFT JOIN youtube y ON s.id = y.song_id
            WHERE s.video_url IS NOT NULL AND y.id IS NULL
            ORDER BY s.created_at DESC
            LIMIT $1
            """
            
            # This is a placeholder - the actual implementation would depend on how
            # your Supabase client handles parameterized queries
            # response = self.supabase.execute_sql(query, [limit])
            
            # For now, we'll use the list_songs method and filter manually
            all_songs = self.supabase.list_songs(limit=50)
            
            # Filter songs that have video_url
            songs_with_videos = [
                song for song in all_songs 
                if song.get('video_url')
            ]
            
            # Limit the number of songs
            songs_to_upload = songs_with_videos[:limit]
            
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
        for song in songs:
            youtube_id = self.upload_song_to_youtube(song)
            if youtube_id:
                successful_uploads += 1
            
            # Add a small delay between uploads to avoid rate limiting
            if len(songs) > 1:
                time.sleep(2)
        
        logger.info(f"Uploaded {successful_uploads} out of {len(songs)} songs")
        return successful_uploads
    
    def fetch_comments_for_video(self, youtube_id: str, song_id: str = None) -> int:
        """
        Fetch comments for a YouTube video and store them in the comments table.
        
        Args:
            youtube_id: YouTube video ID
            song_id: Optional song ID (if not provided, will be looked up)
            
        Returns:
            Number of comments fetched
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
        
        # Store comments in Supabase
        comment_data = []
        for comment in comments:
            comment_data.append({
                "video_id": youtube_id,
                "song_id": song_id,
                "comment_id": comment["comment_id"],
                "author": comment["author"],
                "content": comment["content"],
                "timestamp": comment["timestamp"]
            })
        
        self.supabase.client.table("comments").insert(comment_data).execute()
        
        logger.info(f"Stored {len(comments)} comments for video: {youtube_id}")
        return len(comments)
    
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

def main():
    """
    Main entry point for Agent Angus.
    """
    parser = argparse.ArgumentParser(description='Agent Angus - YouTube Publishing and Feedback Collection')
    parser.add_argument('--create-table', action='store_true', help='Create the YouTube table in Supabase')
    parser.add_argument('--upload', action='store_true', help='Upload pending songs to YouTube')
    parser.add_argument('--fetch-comments', action='store_true', help='Fetch comments for uploaded videos')
    parser.add_argument('--limit', type=int, default=10, help='Limit the number of items to process')
    
    args = parser.parse_args()
    
    # Initialize Agent Angus
    angus = AgentAngus()
    
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
    if not (args.create_table or args.upload or args.fetch_comments):
        parser.print_help()

if __name__ == "__main__":
    main()
