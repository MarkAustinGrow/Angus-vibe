#!/usr/bin/env python3
"""
Angus Tools for CrewAI Integration

This module provides tool wrappers for Agent Angus functionality to be used with CrewAI.
It wraps the core functionality of Agent Angus as CrewAI tools.
"""
from angus import AgentAngus
from crewai.tools import BaseTool, tool
from typing import Optional, List, Dict, Any, Type
from pydantic import BaseModel, Field

# Initialize the AgentAngus instance
angus_instance = AgentAngus()

# Define input schemas for tools
class UploadVideosInput(BaseModel):
    """Input schema for the upload_videos tool."""
    limit: int = Field(5, description="Maximum number of videos to upload")

class ManageCommentsInput(BaseModel):
    """Input schema for the manage_comments tool."""
    limit: int = Field(10, description="Maximum number of videos to process")
    max_replies: int = Field(5, description="Maximum number of replies to post")

class AnalyzeMusicInput(BaseModel):
    """Input schema for the analyze_music tool."""
    url: str = Field(..., description="URL of the music file or YouTube video")
    is_youtube: bool = Field(False, description="Whether the URL is a YouTube video")

# Define tools using BaseTool subclassing
class UploadVideosTool(BaseTool):
    """Tool for uploading videos to YouTube."""
    name: str = "upload_videos"
    description: str = "Upload pending songs from Supabase to YouTube"
    args_schema: Type[BaseModel] = UploadVideosInput

    def _run(self, limit: int = 5) -> str:
        """
        Upload pending songs to YouTube.
        
        Args:
            limit: Maximum number of videos to upload
            
        Returns:
            str: Result message with count of uploaded videos
        """
        count = angus_instance.upload_all_pending_songs(limit=limit)
        return f"Successfully uploaded {count} videos to YouTube"

class ManageCommentsTool(BaseTool):
    """Tool for managing YouTube comments."""
    name: str = "manage_comments"
    description: str = "Fetch comments from YouTube videos and respond using OpenAI"
    args_schema: Type[BaseModel] = ManageCommentsInput

    def _run(self, limit: int = 10, max_replies: int = 5) -> str:
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

class AnalyzeMusicTool(BaseTool):
    """Tool for analyzing music."""
    name: str = "analyze_music"
    description: str = "Analyze music using OpenAI to extract insights about lyrics, mood, themes, and musical characteristics"
    args_schema: Type[BaseModel] = AnalyzeMusicInput

    def _run(self, url: str, is_youtube: bool = False) -> Dict[str, Any]:
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

# Define tools using the @tool decorator
@tool("upload_videos_simple")
def upload_videos_simple(limit: int = 5) -> str:
    """
    Upload pending songs from Supabase to YouTube.
    
    Args:
        limit: Maximum number of videos to upload
        
    Returns:
        str: Result message with count of uploaded videos
    """
    count = angus_instance.upload_all_pending_songs(limit=limit)
    return f"Successfully uploaded {count} videos to YouTube"

@tool("manage_comments_simple")
def manage_comments_simple(limit: int = 10, max_replies: int = 5) -> str:
    """
    Fetch comments from YouTube videos and respond using OpenAI.
    
    Args:
        limit: Maximum number of videos to process
        max_replies: Maximum number of replies to post
        
    Returns:
        str: Result message with count of processed comments
    """
    count = angus_instance.fetch_comments_for_all_videos(limit=limit, max_total_replies=max_replies)
    return f"Processed {count} comments across YouTube videos"

@tool("analyze_music_simple")
def analyze_music_simple(url: str, is_youtube: bool = False) -> Dict[str, Any]:
    """
    Analyze music using OpenAI to extract insights about lyrics, mood, themes, and musical characteristics.
    
    Args:
        url: URL of the music file or YouTube video
        is_youtube: Whether the URL is a YouTube video
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    from openai_utils import analyze_music as openai_analyze
    result = openai_analyze(url, is_youtube_url=is_youtube)
    return result

# Add caching to the tools
def cache_analysis(arguments: dict, result: Dict[str, Any]) -> bool:
    """
    Cache function for the analyze_music tool.
    Only cache successful analyses.
    
    Args:
        arguments: The arguments passed to the tool
        result: The result of the tool
        
    Returns:
        bool: Whether to cache the result
    """
    # Only cache if the result doesn't contain an error
    return 'error' not in result

# Apply caching to the tools
analyze_music_simple.cache_function = cache_analysis

class AngusTools:
    """
    Wrapper class for Agent Angus functionality as CrewAI tools.
    """
    
    def __init__(self):
        """Initialize the AngusTools."""
        pass
        
    def get_upload_tool(self) -> BaseTool:
        """
        Get the tool for uploading videos to YouTube.
        
        Returns:
            BaseTool: A CrewAI tool for uploading videos
        """
        return UploadVideosTool()
        
    def get_comment_tool(self) -> BaseTool:
        """
        Get the tool for managing YouTube comments.
        
        Returns:
            BaseTool: A CrewAI tool for managing comments
        """
        return ManageCommentsTool()
        
    def get_analysis_tool(self) -> BaseTool:
        """
        Get the tool for analyzing music.
        
        Returns:
            BaseTool: A CrewAI tool for music analysis
        """
        return AnalyzeMusicTool()
        
    def get_all_tools(self) -> List[BaseTool]:
        """
        Get all Angus tools.
        
        Returns:
            List[BaseTool]: List of all available tools
        """
        return [
            self.get_upload_tool(),
            self.get_comment_tool(),
            self.get_analysis_tool()
        ]
    
    def get_all_simple_tools(self) -> List:
        """
        Get all simple Angus tools created with the @tool decorator.
        
        Returns:
            List: List of all available simple tools
        """
        return [
            upload_videos_simple,
            manage_comments_simple,
            analyze_music_simple
        ]
