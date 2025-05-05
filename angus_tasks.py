#!/usr/bin/env python3
"""
Angus Tasks for CrewAI Integration

This module defines tasks for Agent Angus using CrewAI.
Each task is assigned to a specific agent and has dependencies on other tasks.
"""
from crewai import Task
from angus_agents import AngusAgents
from typing import List, Optional

class AngusTasks:
    """
    Class for creating tasks for Agent Angus using CrewAI.
    """
    
    def __init__(self):
        """Initialize the AngusTasks with agents from AngusAgents."""
        self.agents = AngusAgents()
        
    def get_analysis_task(self) -> Task:
        """
        Create a task for analyzing music.
        
        Returns:
            Task: A CrewAI task for music analysis
        """
        return Task(
            description="""Analyze new music files that are pending upload.
            Extract information about lyrics, mood, themes, genre, and musical characteristics.
            This information will be used to optimize video metadata for YouTube.""",
            agent=self.agents.get_analysis_agent(),
            expected_output="""Detailed analysis of each music file including:
            - Summary of lyrics
            - Identified themes and moods
            - Genre classification
            - Musical characteristics (BPM, key, etc.)
            - Suggested tags for YouTube"""
        )
        
    def get_upload_task(self, context_tasks: Optional[List[Task]] = None) -> Task:
        """
        Create a task for uploading videos.
        
        Args:
            context_tasks: Optional list of tasks that this task depends on
            
        Returns:
            Task: A CrewAI task for uploading videos
        """
        return Task(
            description="""Upload analyzed music to YouTube with optimized metadata.
            Use the analysis results to create compelling titles, descriptions, and tags.
            Update the database with video IDs and upload status.""",
            agent=self.agents.get_upload_agent(),
            expected_output="""List of successfully uploaded videos including:
            - YouTube video IDs
            - Titles and descriptions used
            - Tags applied
            - Upload status and timestamp""",
            context=context_tasks
        )
        
    def get_engagement_task(self, context_tasks: Optional[List[Task]] = None) -> Task:
        """
        Create a task for managing audience engagement.
        
        Args:
            context_tasks: Optional list of tasks that this task depends on
            
        Returns:
            Task: A CrewAI task for audience engagement
        """
        return Task(
            description="""Monitor and respond to comments on uploaded YouTube videos.
            Generate contextually relevant responses using OpenAI.
            Track all interactions in the database.""",
            agent=self.agents.get_engagement_agent(),
            expected_output="""Engagement metrics and response summary:
            - Number of comments processed
            - Number of responses posted
            - Common themes in comments
            - Suggested follow-up actions""",
            context=context_tasks
        )
        
    def get_full_workflow(self) -> List[Task]:
        """
        Create a full workflow with dependencies.
        
        Returns:
            List[Task]: List of tasks in the workflow
        """
        analysis_task = self.get_analysis_task()
        upload_task = self.get_upload_task(context_tasks=[analysis_task])
        engagement_task = self.get_engagement_task(context_tasks=[upload_task])
        
        return [analysis_task, upload_task, engagement_task]
