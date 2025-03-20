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
