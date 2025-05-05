#!/usr/bin/env python3
"""
Angus Crew for CrewAI Integration

This module manages the CrewAI workflow for Agent Angus.
It creates crews with agents and tasks, and provides methods for running different workflows.
"""
from crewai import Crew
from angus_tasks import AngusTasks
from angus_agents import AngusAgents

class AngusCrew:
    """
    Class for managing CrewAI workflows for Agent Angus.
    """
    
    def __init__(self):
        """Initialize the AngusCrew with tasks from AngusTasks."""
        self.tasks = AngusTasks()
        self.agents = AngusAgents()
        
    def get_full_crew(self) -> Crew:
        """
        Create a crew with all agents and tasks.
        
        Returns:
            Crew: A CrewAI crew with all agents and tasks
        """
        agents = self.agents.get_all_agents()
        tasks = self.tasks.get_full_workflow()
        
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=True
        )
        
    def run_analysis_only(self):
        """
        Run only the analysis task.
        
        Returns:
            str: Result of the analysis task
        """
        analysis_task = self.tasks.get_analysis_task()
        agent = self.agents.get_analysis_agent()
            
        crew = Crew(
            agents=[agent],
            tasks=[analysis_task],
            verbose=True
        )
        return crew.kickoff()
        
    def run_upload_only(self):
        """
        Run only the upload task.
        
        Returns:
            str: Result of the upload task
        """
        upload_task = self.tasks.get_upload_task()
        agent = self.agents.get_upload_agent()
            
        crew = Crew(
            agents=[agent],
            tasks=[upload_task],
            verbose=True
        )
        return crew.kickoff()
        
    def run_engagement_only(self):
        """
        Run only the engagement task.
        
        Returns:
            str: Result of the engagement task
        """
        engagement_task = self.tasks.get_engagement_task()
        agent = self.agents.get_engagement_agent()
            
        crew = Crew(
            agents=[agent],
            tasks=[engagement_task],
            verbose=True
        )
        return crew.kickoff()
        
    def run_full_workflow(self):
        """
        Run the full workflow.
        
        Returns:
            str: Result of the full workflow
        """
        crew = self.get_full_crew()
        return crew.kickoff()
