"""
Configuration module for Agent Angus.

This module loads environment variables from a .env file if available
and provides them as constants for use throughout the application.
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    logger.info("Loading environment variables from .env file")
    load_dotenv()
else:
    logger.warning(".env file not found, using system environment variables")

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# YouTube API credentials
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# YouTube channel ID (for identifying our own comments)
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials are missing!")

if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET:
    logger.warning("YouTube OAuth credentials are missing!")

if not OPENAI_API_KEY:
    logger.warning("OpenAI API key is missing!")

if not YOUTUBE_CHANNEL_ID:
    logger.warning("YouTube channel ID is missing!")
