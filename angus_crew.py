#!/usr/bin/env python3
"""
Angus Crew for CrewAI Integration

This module manages the CrewAI workflow for Agent Angus.
It creates crews with agents and tasks, and provides methods for running different workflows.
"""
import logging
import importlib
import sys
from typing import List, Optional, Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag to track if CrewAI is available
CREWAI_AVAILABLE = False

# Try to import CrewAI components with a timeout
try:
    # Import the basic components first
    from angus_tools import AngusTools
    
    # Try to import CrewAI components
    logger.info("Attempting to import CrewAI components...")
    
    # Import CrewAI components
    from crewai import Agent, Task, Crew
    from angus_agents import AngusAgents
    from angus_tasks import AngusTasks
    
    # If we get here, CrewAI is available
    CREWAI_AVAILABLE = True
    logger.info("CrewAI components imported successfully")
    
except ImportError as e:
    logger.warning(f"Failed to import CrewAI components: {str(e)}")
    logger.warning("Falling back to direct Angus functionality")
except Exception as e:
    logger.warning(f"Unexpected error importing CrewAI components: {str(e)}")
    logger.warning("Falling back to direct Angus functionality")

# Import Angus for fallback functionality
from angus import AgentAngus

class AngusCrew:
    """
    Class for managing CrewAI workflows for Agent Angus.
    """
    
    def __init__(self):
        """Initialize the AngusCrew with tasks from AngusTasks."""
        self.crewai_available = CREWAI_AVAILABLE
        
        # Initialize components based on availability
        if self.crewai_available:
            try:
                self.tasks = AngusTasks()
                self.agents = AngusAgents()
                self.tools = AngusTools()
                logger.info("AngusCrew initialized with CrewAI components")
            except Exception as e:
                logger.warning(f"Error initializing CrewAI components: {str(e)}")
                self.crewai_available = False
        
        # Initialize fallback Angus instance
        if not self.crewai_available:
            self.angus = AgentAngus()
            logger.info("AngusCrew initialized with fallback Angus instance")
    
    def get_agents(self) -> List[Any]:
        """
        Get all agents.
        
        Returns:
            List[Any]: List of all available agents or empty list if CrewAI is not available
        """
        if not self.crewai_available:
            logger.warning("CrewAI is not available, returning empty agent list")
            return []
        
        try:
            return self.agents.get_all_agents()
        except Exception as e:
            logger.error(f"Error getting agents: {str(e)}")
            return []
        
    def get_full_crew(self) -> Optional[Any]:
        """
        Create a crew with all agents and tasks.
        
        Returns:
            Optional[Any]: A CrewAI crew with all agents and tasks, or None if CrewAI is not available
        """
        if not self.crewai_available:
            logger.warning("CrewAI is not available, cannot create crew")
            return None
        
        try:
            agents = self.agents.get_all_agents()
            tasks = self.tasks.get_full_workflow()
            
            return Crew(
                agents=agents,
                tasks=tasks,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error creating full crew: {str(e)}")
            return None
        
    def run_analysis_only(self) -> str:
        """
        Run only the analysis task.
        
        Returns:
            str: Result of the analysis task
        """
        if not self.crewai_available:
            logger.info("Using fallback Angus for analysis")
            # Fallback to direct Angus functionality
            result = "Analysis completed using fallback Angus functionality"
            return result
        
        try:
            analysis_task = self.tasks.get_analysis_task()
            agent = self.agents.get_analysis_agent()
                
            crew = Crew(
                agents=[agent],
                tasks=[analysis_task],
                verbose=True
            )
            return crew.kickoff()
        except Exception as e:
            logger.error(f"Error running analysis with CrewAI: {str(e)}")
            # Fallback to direct Angus functionality
            result = f"Analysis failed with CrewAI: {str(e)}. Using fallback."
            return result
        
    def run_upload_only(self) -> str:
        """
        Run only the upload task.
        
        Returns:
            str: Result of the upload task
        """
        if not self.crewai_available:
            logger.info("Using fallback Angus for upload")
            # Fallback to direct Angus functionality
            count = self.angus.upload_all_pending_songs(limit=5)
            return f"Uploaded {count} videos using fallback Angus functionality"
        
        try:
            upload_task = self.tasks.get_upload_task()
            agent = self.agents.get_upload_agent()
                
            crew = Crew(
                agents=[agent],
                tasks=[upload_task],
                verbose=True
            )
            return crew.kickoff()
        except Exception as e:
            logger.error(f"Error running upload with CrewAI: {str(e)}")
            # Fallback to direct Angus functionality
            count = self.angus.upload_all_pending_songs(limit=5)
            return f"Upload failed with CrewAI: {str(e)}. Used fallback and uploaded {count} videos."
        
    def run_engagement_only(self) -> str:
        """
        Run only the engagement task.
        
        Returns:
            str: Result of the engagement task
        """
        if not self.crewai_available:
            logger.info("Using fallback Angus for engagement")
            # Fallback to direct Angus functionality
            count = self.angus.fetch_comments_for_all_videos(limit=10, max_total_replies=5)
            return f"Processed {count} comments using fallback Angus functionality"
        
        try:
            engagement_task = self.tasks.get_engagement_task()
            agent = self.agents.get_engagement_agent()
                
            crew = Crew(
                agents=[agent],
                tasks=[engagement_task],
                verbose=True
            )
            return crew.kickoff()
        except Exception as e:
            logger.error(f"Error running engagement with CrewAI: {str(e)}")
            # Fallback to direct Angus functionality
            count = self.angus.fetch_comments_for_all_videos(limit=10, max_total_replies=5)
            return f"Engagement failed with CrewAI: {str(e)}. Used fallback and processed {count} comments."
        
    def run_full_workflow(self) -> str:
        """
        Run the full workflow.
        
        Returns:
            str: Result of the full workflow
        """
        if not self.crewai_available:
            logger.info("Using fallback Angus for full workflow")
            # Fallback to direct Angus functionality
            upload_count = self.angus.upload_all_pending_songs(limit=5)
            comment_count = self.angus.fetch_comments_for_all_videos(limit=10, max_total_replies=5)
            return f"Full workflow completed using fallback Angus functionality: Uploaded {upload_count} videos, processed {comment_count} comments"
        
        try:
            crew = self.get_full_crew()
            if crew is None:
                raise Exception("Failed to create crew")
            return crew.kickoff()
        except Exception as e:
            logger.error(f"Error running full workflow with CrewAI: {str(e)}")
            # Fallback to direct Angus functionality
            upload_count = self.angus.upload_all_pending_songs(limit=5)
            comment_count = self.angus.fetch_comments_for_all_videos(limit=10, max_total_replies=5)
            return f"Full workflow failed with CrewAI: {str(e)}. Used fallback: Uploaded {upload_count} videos, processed {comment_count} comments."
