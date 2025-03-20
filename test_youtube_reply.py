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
