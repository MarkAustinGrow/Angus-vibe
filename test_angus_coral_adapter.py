#!/usr/bin/env python3
"""
Test script for the Agent Angus Coral Protocol Adapter.

This script tests the basic functionality of the AngusCoralAdapter class
without actually connecting to the Coral Protocol server.
"""
import unittest
import logging
from unittest.mock import MagicMock, patch
from angus_coral_adapter import AngusCoralAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAngusCoralAdapter(unittest.TestCase):
    """
    Test cases for the AngusCoralAdapter class.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        """
        # Mock the CoralClient
        self.mock_coral_client = MagicMock()
        self.mock_coral_client.register_agent.return_value = "test-agent-id"
        
        # Mock the AgentAngus
        self.mock_angus = MagicMock()
        
        # Create a patcher for the CoralClient
        self.coral_client_patcher = patch('angus_coral_adapter.CoralClient')
        self.mock_coral_client_class = self.coral_client_patcher.start()
        self.mock_coral_client_class.return_value = self.mock_coral_client
        
        # Create a patcher for the AgentAngus
        self.angus_patcher = patch('angus_coral_adapter.AgentAngus')
        self.mock_angus_class = self.angus_patcher.start()
        self.mock_angus_class.return_value = self.mock_angus
        
        # Create the adapter
        self.adapter = AngusCoralAdapter(session_id="test-session")
        
        # Set the agent_id
        self.adapter.agent_id = "test-agent-id"
    
    def tearDown(self):
        """
        Clean up the test environment.
        """
        self.coral_client_patcher.stop()
        self.angus_patcher.stop()
    
    def test_register_agent(self):
        """
        Test the register_agent method.
        """
        # Call the method
        agent_id = self.adapter.register_agent()
        
        # Check that the CoralClient's register_agent method was called
        self.mock_coral_client.register_agent.assert_called_once_with(
            name="Agent Angus",
            description="An AI agent that automates YouTube publishing and audience feedback collection for AI-generated music videos."
        )
        
        # Check that the agent_id was set correctly
        self.assertEqual(agent_id, "test-agent-id")
        self.assertEqual(self.adapter.agent_id, "test-agent-id")
    
    def test_upload_song_to_youtube(self):
        """
        Test the upload_song_to_youtube method.
        """
        # Set up the mock
        self.mock_angus.upload_song_to_youtube.return_value = "test-youtube-id"
        
        # Call the method
        result = self.adapter.upload_song_to_youtube(
            video_url="https://example.com/video.mp4",
            title="Test Video",
            description="This is a test video",
            tags=["test", "video"]
        )
        
        # Check that the AgentAngus's upload_song_to_youtube method was called
        self.mock_angus.upload_song_to_youtube.assert_called_once()
        
        # Check the song object
        song_arg = self.mock_angus.upload_song_to_youtube.call_args[0][0]
        self.assertEqual(song_arg["title"], "Test Video")
        self.assertEqual(song_arg["video_url"], "https://example.com/video.mp4")
        self.assertEqual(song_arg["gpt_description"], "This is a test video")
        self.assertEqual(song_arg["style"], "test,video")
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["youtube_id"], "test-youtube-id")
        self.assertEqual(result["message"], "Successfully uploaded 'Test Video' to YouTube")
    
    def test_fetch_comments(self):
        """
        Test the fetch_comments method.
        """
        # Set up the mock
        self.mock_angus.fetch_comments_for_video.return_value = 5
        
        # Call the method
        result = self.adapter.fetch_comments(
            youtube_id="test-youtube-id",
            max_replies=10
        )
        
        # Check that the AgentAngus's fetch_comments_for_video method was called
        self.mock_angus.fetch_comments_for_video.assert_called_once_with(
            youtube_id="test-youtube-id",
            max_replies=10
        )
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(result["comments_count"], 5)
        self.assertEqual(result["message"], "Fetched 5 comments from YouTube video")
    
    def test_analyze_music(self):
        """
        Test the analyze_music method.
        """
        # Create a patcher for the analyze_music function
        with patch('angus_coral_adapter.analyze_music') as mock_analyze_music:
            # Set up the mock
            mock_analyze_music.return_value = {
                "title": "Test Song",
                "genres": [{"name": "Pop", "weight": 80}],
                "moods": [{"name": "Happy", "weight": 90}]
            }
            
            # Call the method
            result = self.adapter.analyze_music(
                input_source="https://youtube.com/watch?v=test",
                is_youtube_url=True,
                model="gpt-4o"
            )
            
            # Check that the analyze_music function was called
            mock_analyze_music.assert_called_once_with(
                "https://youtube.com/watch?v=test",
                is_youtube_url=True,
                model="gpt-4o"
            )
            
            # Check the result
            self.assertTrue(result["success"])
            self.assertEqual(result["analysis"]["title"], "Test Song")
            self.assertEqual(result["analysis"]["genres"][0]["name"], "Pop")
            self.assertEqual(result["analysis"]["moods"][0]["name"], "Happy")
    
    def test_process_mention_analyze_youtube(self):
        """
        Test the _process_mention method with an analyze YouTube request.
        """
        # Create a patcher for the analyze_music method
        with patch.object(self.adapter, 'analyze_music') as mock_analyze_music:
            # Set up the mock
            mock_analyze_music.return_value = {
                "success": True,
                "analysis": {
                    "title": "Test Song",
                    "genres": [{"name": "Pop", "weight": 80}],
                    "moods": [{"name": "Happy", "weight": 90}]
                }
            }
            
            # Call the method
            result = self.adapter._process_mention(
                thread_id="test-thread",
                content="analyze this YouTube video: https://youtube.com/watch?v=test",
                sender_id="test-sender"
            )
            
            # Check that the analyze_music method was called
            mock_analyze_music.assert_called_once_with(
                "https://youtube.com/watch?v=test",
                is_youtube_url=True
            )
            
            # Check that the send_message method was called
            self.mock_coral_client.send_message.assert_called_once()
            
            # Check the result
            self.assertTrue(result["success"])
            self.assertEqual(result["action"], "analyze_youtube")
            self.assertEqual(result["thread_id"], "test-thread")

if __name__ == "__main__":
    unittest.main()
