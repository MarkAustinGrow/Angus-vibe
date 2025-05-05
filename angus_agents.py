#!/usr/bin/env python3
"""
Angus Agents for CrewAI Integration

This module defines specialized agents for Agent Angus using CrewAI.
Each agent has a specific role, goal, and backstory, and is equipped with
the appropriate tools from angus_tools.py.
"""
from crewai import Agent
from angus_tools import AngusTools

class AngusAgents:
    """
    Class for creating specialized agents for Agent Angus using CrewAI.
    """
    
    def __init__(self):
        """Initialize the AngusAgents with tools from AngusTools."""
        self.tools = AngusTools()
        
    def get_upload_agent(self) -> Agent:
        """
        Create an agent specialized in uploading videos to YouTube.
        
        Returns:
            Agent: A CrewAI agent for uploading videos
        """
        return Agent(
            role='YouTube Upload Specialist',
            goal='Efficiently upload AI-generated music videos to YouTube',
            backstory="""You are a specialist in preparing and uploading content to YouTube.
            You understand how to optimize video metadata, handle upload quotas, and ensure
            successful uploads. You maintain detailed records of all uploads in the database.""",
            tools=[self.tools.get_upload_tool()],
            verbose=True
        )
        
    def get_engagement_agent(self) -> Agent:
        """
        Create an agent specialized in audience engagement.
        
        Returns:
            Agent: A CrewAI agent for audience engagement
        """
        return Agent(
            role='Audience Engagement Specialist',
            goal='Maximize audience engagement through thoughtful responses to comments',
            backstory="""You are an expert in analyzing and responding to audience feedback.
            You understand how to craft personalized, contextually relevant responses that
            encourage further engagement. You track all interactions in the database.""",
            tools=[self.tools.get_comment_tool()],
            verbose=True
        )
        
    def get_analysis_agent(self) -> Agent:
        """
        Create an agent specialized in music analysis.
        
        Returns:
            Agent: A CrewAI agent for music analysis
        """
        return Agent(
            role='Music Analysis Specialist',
            goal='Provide deep insights into music content for better understanding and categorization',
            backstory="""You are trained to analyze musical elements, lyrics, and themes.
            You can extract key information about genre, mood, and musical characteristics
            to help with categorization and metadata generation.""",
            tools=[self.tools.get_analysis_tool()],
            verbose=True
        )
    
    def get_simple_upload_agent(self) -> Agent:
        """
        Create an agent specialized in uploading videos to YouTube using simple tools.
        
        Returns:
            Agent: A CrewAI agent for uploading videos
        """
        from angus_tools import upload_videos_simple
        
        return Agent(
            role='YouTube Upload Specialist (Simple)',
            goal='Efficiently upload AI-generated music videos to YouTube',
            backstory="""You are a specialist in preparing and uploading content to YouTube.
            You understand how to optimize video metadata, handle upload quotas, and ensure
            successful uploads. You maintain detailed records of all uploads in the database.""",
            tools=[upload_videos_simple],
            verbose=True
        )
        
    def get_simple_engagement_agent(self) -> Agent:
        """
        Create an agent specialized in audience engagement using simple tools.
        
        Returns:
            Agent: A CrewAI agent for audience engagement
        """
        from angus_tools import manage_comments_simple
        
        return Agent(
            role='Audience Engagement Specialist (Simple)',
            goal='Maximize audience engagement through thoughtful responses to comments',
            backstory="""You are an expert in analyzing and responding to audience feedback.
            You understand how to craft personalized, contextually relevant responses that
            encourage further engagement. You track all interactions in the database.""",
            tools=[manage_comments_simple],
            verbose=True
        )
        
    def get_simple_analysis_agent(self) -> Agent:
        """
        Create an agent specialized in music analysis using simple tools.
        
        Returns:
            Agent: A CrewAI agent for music analysis
        """
        from angus_tools import analyze_music_simple
        
        return Agent(
            role='Music Analysis Specialist (Simple)',
            goal='Provide deep insights into music content for better understanding and categorization',
            backstory="""You are trained to analyze musical elements, lyrics, and themes.
            You can extract key information about genre, mood, and musical characteristics
            to help with categorization and metadata generation.""",
            tools=[analyze_music_simple],
            verbose=True
        )
        
    def get_all_agents(self) -> list:
        """
        Get all specialized agents.
        
        Returns:
            list: List of all available agents
        """
        return [
            self.get_upload_agent(),
            self.get_engagement_agent(),
            self.get_analysis_agent()
        ]
    
    def get_all_simple_agents(self) -> list:
        """
        Get all specialized agents using simple tools.
        
        Returns:
            list: List of all available simple agents
        """
        return [
            self.get_simple_upload_agent(),
            self.get_simple_engagement_agent(),
            self.get_simple_analysis_agent()
        ]
