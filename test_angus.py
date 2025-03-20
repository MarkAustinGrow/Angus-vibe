#!/usr/bin/env python3
"""
Test script for Agent Angus.

This script tests the Agent Angus application using mocks to avoid making actual API calls.
"""
import logging
import sys
import unittest
from unittest.mock import patch, MagicMock
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

class TestAgentAngus(unittest.TestCase):
    """Test cases for Agent Angus."""
    
    @patch('angus.SupabaseClient')
    @patch('angus.YouTubeClient')
    def setUp(self, mock_youtube, mock_supabase):
        """Set up test fixtures."""
        self.mock_supabase = mock_supabase.return_value
        self.mock_youtube = mock_youtube.return_value
        self.angus = AgentAngus()
        
        # Mock the Supabase client's methods
        self.mock_supabase.client = MagicMock()
        self.mock_supabase.client.postgrest = MagicMock()
        self.mock_supabase.client.postgrest.rpc = MagicMock()
        self.mock_supabase.client.postgrest.rpc.return_value.execute = MagicMock()
        
        # Mock the list_songs method to return test data
        self.mock_supabase.list_songs = MagicMock(return_value=[
            {
                'id': 'test-song-id-1',
                'title': 'Test Song 1',
                'video_url': 'https://example.com/test-video-1.mp4',
                'gpt_description': 'This is test song 1',
                'lyrics': 'Test lyrics for song 1',
                'style': 'test, mock'
            },
            {
                'id': 'test-song-id-2',
                'title': 'Test Song 2',
                'video_url': 'https://example.com/test-video-2.mp4',
                'gpt_description': 'This is test song 2',
                'lyrics': 'Test lyrics for song 2',
                'style': 'test, mock'
            }
        ])
        
        # Mock the YouTube client's methods
        self.mock_youtube.upload_video = MagicMock(return_value='test-youtube-id')
        self.mock_youtube.fetch_comments = MagicMock(return_value=[
            {
                'comment_id': 'test-comment-id-1',
                'author': 'Test User 1',
                'content': 'This is a test comment 1',
                'timestamp': '2025-03-20T10:00:00Z'
            },
            {
                'comment_id': 'test-comment-id-2',
                'author': 'Test User 2',
                'content': 'This is a test comment 2',
                'timestamp': '2025-03-20T11:00:00Z'
            }
        ])
    
    def test_create_youtube_table(self):
        """Test creating the YouTube table."""
        logger.info("Testing create_youtube_table...")
        
        # Mock the open function to return test SQL
        with patch('builtins.open', unittest.mock.mock_open(read_data='CREATE TABLE test;')):
            result = self.angus.create_youtube_table()
            self.assertTrue(result, "Failed to create YouTube table")
        
        logger.info("create_youtube_table test passed")
    
    def test_get_songs_to_upload(self):
        """Test getting songs to upload."""
        logger.info("Testing get_songs_to_upload...")
        
        songs = self.angus.get_songs_to_upload(limit=3)
        self.assertTrue(len(songs) > 0, "No songs returned")
        self.assertIn('title', songs[0], "Song missing title field")
        self.assertIn('video_url', songs[0], "Song missing video_url field")
        
        logger.info(f"get_songs_to_upload test passed, found {len(songs)} songs")
    
    def test_upload_song_to_youtube(self):
        """Test uploading a song to YouTube."""
        logger.info("Testing upload_song_to_youtube...")
        
        # Create a test song
        test_song = {
            'id': 'test-song-id',
            'title': 'Test Song',
            'video_url': 'https://example.com/test-video.mp4',
            'gpt_description': 'This is a test song description',
            'lyrics': 'Test lyrics for the test song',
            'style': 'test, mock'
        }
        
        youtube_id = self.angus.upload_song_to_youtube(test_song)
        self.assertIsNotNone(youtube_id, "Failed to upload song to YouTube")
        
        logger.info(f"upload_song_to_youtube test passed, got YouTube ID: {youtube_id}")
    
    def test_fetch_comments(self):
        """Test fetching comments for a video."""
        logger.info("Testing fetch_comments_for_video...")
        
        # Mock the Supabase client's table method
        self.mock_supabase.client.table = MagicMock()
        self.mock_supabase.client.table.return_value.select = MagicMock()
        self.mock_supabase.client.table.return_value.select.return_value.eq = MagicMock()
        self.mock_supabase.client.table.return_value.select.return_value.eq.return_value.execute = MagicMock()
        self.mock_supabase.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'song_id': 'test-song-id'}]
        
        # Mock the Supabase client's table method for feedback insertion
        self.mock_supabase.client.table.return_value.insert = MagicMock()
        self.mock_supabase.client.table.return_value.insert.return_value.execute = MagicMock()
        
        comments_count = self.angus.fetch_comments_for_video('test-youtube-id', 'test-song-id')
        self.assertTrue(comments_count > 0, "No comments fetched")
        
        logger.info(f"fetch_comments_for_video test passed, fetched {comments_count} comments")

def run_all_tests():
    """Run all tests."""
    logger.info("Running all tests for Agent Angus...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    logger.info("All tests completed!")

if __name__ == "__main__":
    run_all_tests()
