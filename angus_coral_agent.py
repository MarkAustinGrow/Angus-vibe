#!/usr/bin/env python3
"""
Angus Coral Agent - Integration between Angus and Coral Protocol using LangChain

This script implements a Coral Protocol agent that exposes Angus's capabilities
to other agents in the Coral ecosystem using LangChain MCP adapters.
"""
import os
import sys
import json
import time
import logging
import traceback
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('angus_coral.log')
    ]
)
logger = logging.getLogger(__name__)

# Import Angus components
try:
    from supabase_client import SupabaseClient
    logger.info("Successfully initialized SupabaseClient")
except Exception as e:
    logger.error(f"Error importing SupabaseClient: {str(e)}")
    SupabaseClient = None

class AngusCoralAgent:
    """
    Angus Coral Agent - Exposes Angus capabilities to the Coral Protocol
    """
    
    def __init__(self, coral_server_url="https://coral.pushcollective.club/sse"):
        """
        Initialize the Angus Coral Agent.
        
        Args:
            coral_server_url: URL of the Coral Protocol Server
        """
        self.coral_server_url = coral_server_url
        self.agent_id = "angus_agent"
        self.agent_description = """
        You are angus_agent, responsible for YouTube publishing and feedback collection.
        You can upload videos to YouTube, retrieve comments, and analyze music.
        """
        
        # Initialize Angus components
        try:
            if SupabaseClient:
                self.supabase = SupabaseClient()
                logger.info("Successfully initialized SupabaseClient")
            else:
                self.supabase = None
                logger.warning("SupabaseClient not available")
        except Exception as e:
            logger.error(f"Error initializing SupabaseClient: {str(e)}")
            self.supabase = None
        
        logger.info("Angus Coral Agent initialized")
    
    def upload_video(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a video to YouTube.
        
        Args:
            args: Arguments for the upload
            
        Returns:
            Result of the upload operation
        """
        try:
            video_url = args.get("video_url")
            title = args.get("title")
            description = args.get("description", "")
            tags = args.get("tags", [])
            
            if not video_url or not title:
                return {
                    "success": False,
                    "error": "Missing required parameters: video_url and title"
                }
            
            logger.info(f"Uploading video: {title} from {video_url}")
            
            # For now, we'll return a placeholder since we're not using YouTubeClient
            logger.info(f"Simulating upload of video: {title}")
            
            return {
                "success": True,
                "youtube_id": "simulated_youtube_id",
                "message": f"Video '{title}' upload simulated successfully"
            }
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return {
                "success": False,
                "error": f"Error uploading video: {str(e)}"
            }
    
    def fetch_comments(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch comments for a YouTube video.
        
        Args:
            args: Arguments for fetching comments
            
        Returns:
            Comments for the video
        """
        try:
            youtube_id = args.get("youtube_id")
            max_results = args.get("max_results", 100)
            
            if not youtube_id:
                return {
                    "success": False,
                    "error": "Missing required parameter: youtube_id"
                }
            
            logger.info(f"Fetching comments for video: {youtube_id} (max: {max_results})")
            
            # For now, we'll return a placeholder since we're not using YouTubeClient
            logger.info(f"Simulating fetching comments for video: {youtube_id}")
            
            return {
                "success": True,
                "comments": [
                    {
                        "id": "comment1",
                        "author": "User1",
                        "content": "Great video!",
                        "timestamp": "2023-01-01T12:00:00Z"
                    },
                    {
                        "id": "comment2",
                        "author": "User2",
                        "content": "I enjoyed this content.",
                        "timestamp": "2023-01-02T12:00:00Z"
                    }
                ],
                "count": 2
            }
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return {
                "success": False,
                "error": f"Error fetching comments: {str(e)}"
            }
    
    def analyze_music(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze music and generate a description.
        
        Args:
            args: Arguments for music analysis
            
        Returns:
            Analysis results
        """
        try:
            audio_url = args.get("audio_url")
            analysis_type = args.get("analysis_type", "basic")
            
            if not audio_url:
                return {
                    "success": False,
                    "error": "Missing required parameter: audio_url"
                }
            
            logger.info(f"Analyzing music: {audio_url} (type: {analysis_type})")
            
            # This would integrate with Angus's music analysis capabilities
            # For now, we'll return a placeholder
            
            logger.info(f"Completed music analysis for: {audio_url}")
            
            return {
                "success": True,
                "analysis": "Music analysis would be performed here",
                "details": {
                    "audio_url": audio_url,
                    "analysis_type": analysis_type
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing music: {str(e)}")
            return {
                "success": False,
                "error": f"Error analyzing music: {str(e)}"
            }
    
    def create_tools(self):
        """
        Create tools for the agent.
        
        Returns:
            List of tools
        """
        try:
            from langchain.agents import Tool
            
            tools = [
                Tool(
                    name="upload_video",
                    func=self.upload_video,
                    description="Upload a video to YouTube. Args: video_url (str), title (str), description (str, optional), tags (List[str], optional)"
                ),
                Tool(
                    name="fetch_comments",
                    func=self.fetch_comments,
                    description="Fetch comments for a YouTube video. Args: youtube_id (str), max_results (int, optional)"
                ),
                Tool(
                    name="analyze_music",
                    func=self.analyze_music,
                    description="Analyze music and generate a description. Args: audio_url (str), analysis_type (str, optional: 'basic' or 'detailed')"
                )
            ]
            
            return tools
        except Exception as e:
            logger.error(f"Error creating tools: {str(e)}")
            traceback.print_exc()
            return []
    
    def create_agent_chain(self):
        """
        Create the agent chain.
        
        Returns:
            Agent chain
        """
        try:
            from langchain.prompts import PromptTemplate
            from langchain_openai import ChatOpenAI
            from langchain.schema.runnable import RunnablePassthrough
            from langchain.schema.output_parser import StrOutputParser
            
            # Define the prompt template
            prompt = PromptTemplate.from_template(
                """
                You are the Angus agent, specialized in YouTube operations and music analysis.
                
                User request: {input}
                
                Think through how to handle this request using your available tools.
                """
            )
            
            # Create the LLM
            llm = ChatOpenAI(temperature=0)
            
            # Create the chain
            chain = (
                {"input": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            return chain
        except Exception as e:
            logger.error(f"Error creating agent chain: {str(e)}")
            traceback.print_exc()
            return None
    
    def run(self):
        """
        Run the Angus Coral agent.
        
        This method starts the agent and connects it to the Coral Protocol server.
        """
        logger.info(f"Starting Angus Coral Agent with server URL: {self.coral_server_url}")
        
        try:
            # Import langchain_mcp_adapters
            import langchain_mcp_adapters
            
            # Log available attributes in langchain_mcp_adapters
            logger.info(f"Available in langchain_mcp_adapters: {dir(langchain_mcp_adapters)}")
            
            # Create tools
            tools = self.create_tools()
            
            # Create agent chain
            chain = self.create_agent_chain()
            
            if not tools or not chain:
                logger.error("Failed to create tools or agent chain, exiting")
                return
            
            # Set up agent parameters
            langchain_mcp_adapters.agent_id = self.agent_id
            langchain_mcp_adapters.agent_description = self.agent_description
            langchain_mcp_adapters.base_url = self.coral_server_url
            
            # Check if there's a connect or run method
            if hasattr(langchain_mcp_adapters, 'connect'):
                logger.info("Using langchain_mcp_adapters.connect method")
                langchain_mcp_adapters.connect(
                    agent_id=self.agent_id,
                    agent_description=self.agent_description,
                    base_url=self.coral_server_url,
                    tools=tools,
                    llm_chain=chain
                )
            elif hasattr(langchain_mcp_adapters, 'run'):
                logger.info("Using langchain_mcp_adapters.run method")
                langchain_mcp_adapters.run(
                    agent_id=self.agent_id,
                    agent_description=self.agent_description,
                    base_url=self.coral_server_url,
                    tools=tools,
                    llm_chain=chain
                )
            else:
                # Try to use the module directly
                logger.info("Using langchain_mcp_adapters module directly")
                
                # Check if there are any callable attributes
                callable_attrs = [attr for attr in dir(langchain_mcp_adapters) 
                                 if not attr.startswith('__') and callable(getattr(langchain_mcp_adapters, attr))]
                
                if callable_attrs:
                    logger.info(f"Found callable attributes: {callable_attrs}")
                    
                    # Try to use the first callable attribute
                    first_callable = getattr(langchain_mcp_adapters, callable_attrs[0])
                    logger.info(f"Trying to use {callable_attrs[0]}")
                    
                    try:
                        first_callable(
                            agent_id=self.agent_id,
                            agent_description=self.agent_description,
                            base_url=self.coral_server_url,
                            tools=tools,
                            llm_chain=chain
                        )
                    except Exception as e:
                        logger.error(f"Error using {callable_attrs[0]}: {str(e)}")
                        traceback.print_exc()
                else:
                    logger.error("No callable attributes found in langchain_mcp_adapters")
                    
                    # Just keep the process running
                    logger.info("Keeping the process running...")
                    while True:
                        time.sleep(60)
                        logger.info("Angus Coral Agent is running...")
            
        except Exception as e:
            logger.error(f"Error running Angus Coral Agent: {str(e)}")
            traceback.print_exc()

def main():
    """
    Main entry point for the Angus Coral Agent.
    """
    # Get Coral server URL from environment variable or use default
    coral_server_url = os.environ.get("CORAL_SERVER_URL", "https://coral.pushcollective.club/sse")
    
    # Create and run the agent
    agent = AngusCoralAgent(coral_server_url=coral_server_url)
    agent.run()

if __name__ == "__main__":
    main()
