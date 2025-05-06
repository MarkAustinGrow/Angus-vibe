#!/usr/bin/env python3
"""
Angus Tools for CrewAI Integration

This module provides tool wrappers for Agent Angus functionality to be used with CrewAI.
It wraps the core functionality of Agent Angus as CrewAI tools.
"""
from angus import AgentAngus
from langchain.tools import Tool
from typing import Optional, List, Dict, Any

# Initialize the AgentAngus instance
angus_instance = AgentAngus()

class AngusTools:
    """
    Wrapper class for Agent Angus functionality as CrewAI tools.
    """
    
    def __init__(self):
        """Initialize the AngusTools."""
        pass
        
    def get_upload_tool(self) -> Tool:
        """
        Get the tool for uploading videos to YouTube.
        
        Returns:
            Tool: A CrewAI tool for uploading videos
        """
        def upload_videos(limit: int = 5) -> str:
            """
            Upload pending songs to YouTube.
            
            Args:
                limit: Maximum number of videos to upload
                
            Returns:
                str: Result message with count of uploaded videos
            """
            count = angus_instance.upload_all_pending_songs(limit=limit)
            return f"Successfully uploaded {count} videos to YouTube"
            
        return Tool(
            name="upload_videos",
            func=upload_videos,
            description="Upload pending songs from Supabase to YouTube"
        )
        
    def get_comment_tool(self) -> Tool:
        """
        Get the tool for managing YouTube comments.
        
        Returns:
            Tool: A CrewAI tool for managing comments
        """
        def manage_comments(limit: int = 10, max_replies: int = 5) -> str:
            """
            Fetch and respond to YouTube comments.
            
            Args:
                limit: Maximum number of videos to process
                max_replies: Maximum number of replies to post
                
            Returns:
                str: Result message with count of processed comments
            """
            count = angus_instance.fetch_comments_for_all_videos(limit=limit, max_total_replies=max_replies)
            return f"Processed {count} comments across YouTube videos"
            
        return Tool(
            name="manage_comments",
            func=manage_comments,
            description="Fetch comments from YouTube videos and respond using OpenAI"
        )
        
    def get_analysis_tool(self) -> Tool:
        """
        Get the tool for analyzing music.
        
        Returns:
            Tool: A CrewAI tool for music analysis
        """
        def analyze_music(url: str, is_youtube: bool = False) -> Dict[str, Any]:
            """
            Analyze music using OpenAI.
            
            Args:
                url: URL of the music file or YouTube video
                is_youtube: Whether the URL is a YouTube video
                
            Returns:
                Dict[str, Any]: Analysis results
            """
            from openai_utils import analyze_music as openai_analyze
            result = openai_analyze(url, is_youtube_url=is_youtube)
            return result
            
        return Tool(
            name="analyze_music",
            func=analyze_music,
            description="Analyze music using OpenAI to extract insights about lyrics, mood, themes, and musical characteristics"
        )
        
    def get_all_tools(self) -> List[Tool]:
        """
        Get all Angus tools.
        
        Returns:
            List[Tool]: List of all available tools
        """
        return [
            self.get_upload_tool(),
            self.get_comment_tool(),
            self.get_analysis_tool()
        ]
