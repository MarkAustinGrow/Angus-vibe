#!/usr/bin/env python3
"""
Unit tests for Agent Angus CrewAI integration.

This script provides unit tests for the CrewAI integration with Agent Angus.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from angus_crew import AngusCrew
from angus_tasks import AngusTasks
from angus_agents import AngusAgents
from angus_tools import AngusTools

class TestAngusTools(unittest.TestCase):
    """
    Test the AngusTools class.
    """
    
    @patch('angus.AgentAngus')
    def test_upload_tool(self, mock_angus):
        """Test the upload tool."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.upload_all_pending_songs.return_value = 3
        mock_angus.return_value = mock_instance
        
        # Create tool
        tools = AngusTools()
        upload_tool = tools.get_upload_tool()
        
        # Test tool
        result = upload_tool.func(limit=5)
        self.assertIn("Successfully uploaded 3 videos", result)
        mock_instance.upload_all_pending_songs.assert_called_with(limit=5)
    
    @patch('angus.AgentAngus')
    def test_comment_tool(self, mock_angus):
        """Test the comment tool."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.fetch_comments_for_all_videos.return_value = 10
        mock_angus.return_value = mock_instance
        
        # Create tool
        tools = AngusTools()
        comment_tool = tools.get_comment_tool()
        
        # Test tool
        result = comment_tool.func(limit=5, max_replies=3)
        self.assertIn("Processed 10 comments", result)
        mock_instance.fetch_comments_for_all_videos.assert_called_with(limit=5, max_total_replies=3)
    
    @patch('openai_utils.analyze_music')
    @patch('angus.AgentAngus')
    def test_analysis_tool(self, mock_angus, mock_analyze):
        """Test the analysis tool."""
        # Setup mock
        mock_analyze.return_value = {"summary": "Test summary"}
        
        # Create tool
        tools = AngusTools()
        analysis_tool = tools.get_analysis_tool()
        
        # Test tool
        result = analysis_tool.func(url="https://example.com/song.mp3", is_youtube=False)
        self.assertEqual(result, {"summary": "Test summary"})
        mock_analyze.assert_called_with("https://example.com/song.mp3", is_youtube_url=False)
    
    @patch('angus.AgentAngus')
    def test_get_all_tools(self, mock_angus):
        """Test getting all tools."""
        # Create tools
        tools = AngusTools()
        all_tools = tools.get_all_tools()
        
        # Test result
        self.assertEqual(len(all_tools), 3)
        self.assertEqual(all_tools[0].name, "upload_videos")
        self.assertEqual(all_tools[1].name, "manage_comments")
        self.assertEqual(all_tools[2].name, "analyze_music")

class TestAngusAgents(unittest.TestCase):
    """
    Test the AngusAgents class.
    """
    
    @patch('angus_tools.AngusTools')
    def test_get_upload_agent(self, mock_tools):
        """Test getting the upload agent."""
        # Setup mock
        mock_tools_instance = MagicMock()
        mock_tools_instance.get_upload_tool.return_value = "upload_tool"
        mock_tools.return_value = mock_tools_instance
        
        # Create agent
        agents = AngusAgents()
        upload_agent = agents.get_upload_agent()
        
        # Test agent
        self.assertEqual(upload_agent.role, "YouTube Upload Specialist")
        self.assertEqual(upload_agent.tools, ["upload_tool"])
    
    @patch('angus_tools.AngusTools')
    def test_get_engagement_agent(self, mock_tools):
        """Test getting the engagement agent."""
        # Setup mock
        mock_tools_instance = MagicMock()
        mock_tools_instance.get_comment_tool.return_value = "comment_tool"
        mock_tools.return_value = mock_tools_instance
        
        # Create agent
        agents = AngusAgents()
        engagement_agent = agents.get_engagement_agent()
        
        # Test agent
        self.assertEqual(engagement_agent.role, "Audience Engagement Specialist")
        self.assertEqual(engagement_agent.tools, ["comment_tool"])
    
    @patch('angus_tools.AngusTools')
    def test_get_analysis_agent(self, mock_tools):
        """Test getting the analysis agent."""
        # Setup mock
        mock_tools_instance = MagicMock()
        mock_tools_instance.get_analysis_tool.return_value = "analysis_tool"
        mock_tools.return_value = mock_tools_instance
        
        # Create agent
        agents = AngusAgents()
        analysis_agent = agents.get_analysis_agent()
        
        # Test agent
        self.assertEqual(analysis_agent.role, "Music Analysis Specialist")
        self.assertEqual(analysis_agent.tools, ["analysis_tool"])
    
    @patch('angus_tools.AngusTools')
    def test_get_all_agents(self, mock_tools):
        """Test getting all agents."""
        # Setup mock
        mock_tools_instance = MagicMock()
        mock_tools.return_value = mock_tools_instance
        
        # Create agents
        agents = AngusAgents()
        
        # Mock the individual agent methods
        agents.get_upload_agent = MagicMock(return_value="upload_agent")
        agents.get_engagement_agent = MagicMock(return_value="engagement_agent")
        agents.get_analysis_agent = MagicMock(return_value="analysis_agent")
        
        all_agents = agents.get_all_agents()
        
        # Test result
        self.assertEqual(len(all_agents), 3)
        self.assertEqual(all_agents[0], "upload_agent")
        self.assertEqual(all_agents[1], "engagement_agent")
        self.assertEqual(all_agents[2], "analysis_agent")

class TestAngusTasks(unittest.TestCase):
    """
    Test the AngusTasks class.
    """
    
    @patch('angus_agents.AngusAgents')
    def test_get_analysis_task(self, mock_agents):
        """Test getting the analysis task."""
        # Setup mock
        mock_agents_instance = MagicMock()
        mock_agents_instance.get_analysis_agent.return_value = "analysis_agent"
        mock_agents.return_value = mock_agents_instance
        
        # Create task
        tasks = AngusTasks()
        analysis_task = tasks.get_analysis_task()
        
        # Test task
        self.assertEqual(analysis_task.agent, "analysis_agent")
        self.assertIn("Analyze new music files", analysis_task.description)
    
    @patch('angus_agents.AngusAgents')
    def test_get_upload_task(self, mock_agents):
        """Test getting the upload task."""
        # Setup mock
        mock_agents_instance = MagicMock()
        mock_agents_instance.get_upload_agent.return_value = "upload_agent"
        mock_agents.return_value = mock_agents_instance
        
        # Create task
        tasks = AngusTasks()
        upload_task = tasks.get_upload_task(context_tasks=["context_task"])
        
        # Test task
        self.assertEqual(upload_task.agent, "upload_agent")
        self.assertIn("Upload analyzed music", upload_task.description)
        self.assertEqual(upload_task.context, ["context_task"])
    
    @patch('angus_agents.AngusAgents')
    def test_get_engagement_task(self, mock_agents):
        """Test getting the engagement task."""
        # Setup mock
        mock_agents_instance = MagicMock()
        mock_agents_instance.get_engagement_agent.return_value = "engagement_agent"
        mock_agents.return_value = mock_agents_instance
        
        # Create task
        tasks = AngusTasks()
        engagement_task = tasks.get_engagement_task(context_tasks=["context_task"])
        
        # Test task
        self.assertEqual(engagement_task.agent, "engagement_agent")
        self.assertIn("Monitor and respond to comments", engagement_task.description)
        self.assertEqual(engagement_task.context, ["context_task"])
    
    @patch('angus_agents.AngusAgents')
    def test_get_full_workflow(self, mock_agents):
        """Test getting the full workflow."""
        # Setup mock
        mock_agents_instance = MagicMock()
        mock_agents.return_value = mock_agents_instance
        
        # Create tasks
        tasks = AngusTasks()
        
        # Mock the individual task methods
        tasks.get_analysis_task = MagicMock(return_value="analysis_task")
        tasks.get_upload_task = MagicMock(return_value="upload_task")
        tasks.get_engagement_task = MagicMock(return_value="engagement_task")
        
        workflow = tasks.get_full_workflow()
        
        # Test result
        self.assertEqual(len(workflow), 3)
        self.assertEqual(workflow[0], "analysis_task")
        self.assertEqual(workflow[1], "upload_task")
        self.assertEqual(workflow[2], "engagement_task")
        
        # Verify the task dependencies
        tasks.get_upload_task.assert_called_with(context_tasks=["analysis_task"])
        tasks.get_engagement_task.assert_called_with(context_tasks=["upload_task"])

class TestAngusCrew(unittest.TestCase):
    """
    Test the AngusCrew class.
    """
    
    @patch('crewai.Crew')
    @patch('angus_tasks.AngusTasks')
    def test_get_full_crew(self, mock_tasks, mock_crew):
        """Test getting the full crew."""
        # Setup mocks
        mock_tasks_instance = MagicMock()
        mock_tasks_instance.agents.get_all_agents.return_value = ["agent1", "agent2"]
        mock_tasks_instance.get_full_workflow.return_value = ["task1", "task2"]
        mock_tasks.return_value = mock_tasks_instance
        
        mock_crew_instance = MagicMock()
        mock_crew.return_value = mock_crew_instance
        
        # Create crew
        crew = AngusCrew()
        result = crew.get_full_crew()
        
        # Test result
        self.assertEqual(result, mock_crew_instance)
        mock_crew.assert_called_with(
            agents=["agent1", "agent2"],
            tasks=["task1", "task2"],
            verbose=True
        )
    
    @patch('crewai.Crew')
    @patch('angus_tasks.AngusTasks')
    def test_run_analysis_only(self, mock_tasks, mock_crew):
        """Test running only the analysis task."""
        # Setup mocks
        mock_tasks_instance = MagicMock()
        mock_tasks_instance.get_analysis_task.return_value = "analysis_task"
        mock_tasks_instance.agents.get_analysis_agent.return_value = "analysis_agent"
        mock_tasks.return_value = mock_tasks_instance
        
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "analysis_result"
        mock_crew.return_value = mock_crew_instance
        
        # Create crew
        crew = AngusCrew()
        result = crew.run_analysis_only()
        
        # Test result
        self.assertEqual(result, "analysis_result")
        mock_crew.assert_called_with(
            agents=["analysis_agent"],
            tasks=["analysis_task"],
            verbose=True
        )
        mock_crew_instance.kickoff.assert_called_once()
    
    @patch('crewai.Crew')
    @patch('angus_tasks.AngusTasks')
    def test_run_upload_only(self, mock_tasks, mock_crew):
        """Test running only the upload task."""
        # Setup mocks
        mock_tasks_instance = MagicMock()
        mock_tasks_instance.get_upload_task.return_value = "upload_task"
        mock_tasks_instance.agents.get_upload_agent.return_value = "upload_agent"
        mock_tasks.return_value = mock_tasks_instance
        
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "upload_result"
        mock_crew.return_value = mock_crew_instance
        
        # Create crew
        crew = AngusCrew()
        result = crew.run_upload_only()
        
        # Test result
        self.assertEqual(result, "upload_result")
        mock_crew.assert_called_with(
            agents=["upload_agent"],
            tasks=["upload_task"],
            verbose=True
        )
        mock_crew_instance.kickoff.assert_called_once()
    
    @patch('crewai.Crew')
    @patch('angus_tasks.AngusTasks')
    def test_run_engagement_only(self, mock_tasks, mock_crew):
        """Test running only the engagement task."""
        # Setup mocks
        mock_tasks_instance = MagicMock()
        mock_tasks_instance.get_engagement_task.return_value = "engagement_task"
        mock_tasks_instance.agents.get_engagement_agent.return_value = "engagement_agent"
        mock_tasks.return_value = mock_tasks_instance
        
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "engagement_result"
        mock_crew.return_value = mock_crew_instance
        
        # Create crew
        crew = AngusCrew()
        result = crew.run_engagement_only()
        
        # Test result
        self.assertEqual(result, "engagement_result")
        mock_crew.assert_called_with(
            agents=["engagement_agent"],
            tasks=["engagement_task"],
            verbose=True
        )
        mock_crew_instance.kickoff.assert_called_once()
    
    @patch('crewai.Crew')
    @patch('angus_tasks.AngusTasks')
    def test_run_full_workflow(self, mock_tasks, mock_crew):
        """Test running the full workflow."""
        # Setup mocks
        mock_tasks_instance = MagicMock()
        mock_tasks.return_value = mock_tasks_instance
        
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "full_workflow_result"
        mock_crew.return_value = mock_crew_instance
        
        # Create crew
        crew = AngusCrew()
        
        # Mock the get_full_crew method
        crew.get_full_crew = MagicMock(return_value=mock_crew_instance)
        
        result = crew.run_full_workflow()
        
        # Test result
        self.assertEqual(result, "full_workflow_result")
        crew.get_full_crew.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()

if __name__ == "__main__":
    unittest.main()
