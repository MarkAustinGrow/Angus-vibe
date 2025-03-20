#!/usr/bin/env python3
"""
Test script to fetch comments for a specific video.

This script fetches comments for a specific YouTube video and checks if they have replies.
"""
import logging
import sys
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the necessary modules
from youtube_client import YouTubeClient
from supabase_client import SupabaseClient

def test_fetch_specific_video(video_id):
    """
    Test fetching comments for a specific video.
    
    Args:
        video_id: The YouTube video ID to fetch comments from
    """
    logger.info(f"Testing fetching comments for video: {video_id}")
    
    try:
        # Initialize the YouTube client
        youtube = YouTubeClient()
        
        # Initialize the Supabase client
        supabase = SupabaseClient()
        
        # Check if the video is in the YouTube table
        response = supabase.client.table("youtube").select("*").eq("youtube_id", video_id).execute()
        
        if response.data and len(response.data) > 0:
            logger.info(f"Video found in YouTube table: {response.data[0]}")
        else:
            logger.info(f"Video not found in YouTube table")
            
            # Add the video to the YouTube table
            logger.info(f"Adding video to YouTube table")
            
            # First, check if the video exists on YouTube
            try:
                video_response = youtube.youtube.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()
                
                if video_response.get("items"):
                    video_info = video_response["items"][0]
                    title = video_info["snippet"]["title"]
                    
                    # Insert into YouTube table
                    youtube_data = {
                        "youtube_id": video_id,
                        "title": title,
                        "status": "uploaded"
                    }
                    
                    supabase.client.table("youtube").insert(youtube_data).execute()
                    logger.info(f"Added video to YouTube table: {title}")
                else:
                    logger.error(f"Video not found on YouTube: {video_id}")
                    return False
            except Exception as e:
                logger.error(f"Error getting video info: {str(e)}")
                return False
        
        # Fetch comments from YouTube
        comments = youtube.fetch_comments(video_id)
        
        if not comments:
            logger.error(f"No comments found for video: {video_id}")
            return False
        
        logger.info(f"Found {len(comments)} comments")
        
        # Check if comments have replies
        for comment in comments:
            comment_id = comment["comment_id"]
            comment_text = comment["content"]
            has_our_reply = comment.get("has_our_reply", False)
            
            logger.info(f"Comment: '{comment_text}'")
            logger.info(f"Has our reply: {has_our_reply}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test fetching comments for a specific video')
    parser.add_argument('--video-id', required=True, help='YouTube video ID to fetch comments from')
    
    args = parser.parse_args()
    
    success = test_fetch_specific_video(args.video_id)
    sys.exit(0 if success else 1)
