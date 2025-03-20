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
