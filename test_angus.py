#!/usr/bin/env python3
"""
Test script for Agent Angus.

This script tests the Agent Angus application in simulation mode.
"""
import logging
import sys
from angus import AgentAngus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_create_youtube_table():
    """Test creating the YouTube table."""
    logger.info("Testing create_youtube_table...")
    angus = AgentAngus(simulation_mode=True)
    result = angus.create_youtube_table()
    assert result is True, "Failed to create YouTube table"
    logger.info("create_youtube_table test passed")

def test_get_songs_to_upload():
    """Test getting songs to upload."""
    logger.info("Testing get_songs_to_upload...")
    angus = AgentAngus(simulation_mode=True)
    songs = angus.get_songs_to_upload(limit=3)
    assert len(songs) > 0, "No songs returned"
    assert 'title' in songs[0], "Song missing title field"
    assert 'video_url' in songs[0], "Song missing video_url field"
    logger.info(f"get_songs_to_upload test passed, found {len(songs)} songs")

def test_upload_song_to_youtube():
    """Test uploading a song to YouTube."""
    logger.info("Testing upload_song_to_youtube...")
    angus = AgentAngus(simulation_mode=True)
    
    # Create a test song
    test_song = {
        'id': 'test-song-id',
        'title': 'Test Song',
        'video_url': 'https://example.com/test-video.mp4',
        'gpt_description': 'This is a test song description',
        'lyrics': 'Test lyrics for the test song',
        'style': 'test, simulation'
    }
    
    youtube_id = angus.upload_song_to_youtube(test_song)
    assert youtube_id is not None, "Failed to upload song to YouTube"
    logger.info(f"upload_song_to_youtube test passed, got YouTube ID: {youtube_id}")

def test_fetch_comments():
    """Test fetching comments for a video."""
    logger.info("Testing fetch_comments_for_video...")
    angus = AgentAngus(simulation_mode=True)
    
    comments_count = angus.fetch_comments_for_video('simulated-youtube-id', 'test-song-id')
    assert comments_count > 0, "No comments fetched"
    logger.info(f"fetch_comments_for_video test passed, fetched {comments_count} comments")

def run_all_tests():
    """Run all tests."""
    logger.info("Running all tests for Agent Angus in simulation mode...")
    
    test_create_youtube_table()
    test_get_songs_to_upload()
    test_upload_song_to_youtube()
    test_fetch_comments()
    
    logger.info("All tests passed!")

if __name__ == "__main__":
    run_all_tests()
