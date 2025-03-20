#!/usr/bin/env python3
"""
Test script to run Angus on a specific video.

This script runs the fetch_comments_for_video method of AgentAngus on a specific video.
"""
import logging
import sys
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the necessary modules
from angus import AgentAngus

def test_angus_specific_video(video_id):
    """
    Test running Angus on a specific video.
    
    Args:
        video_id: The YouTube video ID to fetch comments from
    """
    logger.info(f"Testing Angus on video: {video_id}")
    
    try:
        # Initialize Agent Angus
        angus = AgentAngus()
        
        # Fetch comments for the specific video
        comments_count = angus.fetch_comments_for_video(video_id)
        
        logger.info(f"Processed {comments_count} new comments for video: {video_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test running Angus on a specific video')
    parser.add_argument('--video-id', required=True, help='YouTube video ID to fetch comments from')
    
    args = parser.parse_args()
    
    success = test_angus_specific_video(args.video_id)
    sys.exit(0 if success else 1)
