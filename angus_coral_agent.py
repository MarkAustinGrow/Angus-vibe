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
from typing import Dict, Any, List, Optional
import traceback

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
from supabase_client import SupabaseClient

# Import LangChain components
try:
    from langchain.agents import Tool
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser
    import langchain_mcp_adapters
    
    logger.info("Successfully imported LangChain components")
    logger.info(f"Available in langchain_mcp_adapters: {dir(langchain_mcp_adapters)}")
except Exception as e:
    logger.error(f"Error importing LangChain components: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

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
            self.supabase = SupabaseClient()
            logger.info("Successfully initialized SupabaseClient")
        except Exception as e:
            logger.error(f"Error initializing SupabaseClient: {str(e)}")
            self.supabase = None
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0)
        
        logger.info("Angus Coral Agent initialized")
    
    def upload_video(self, args_str: str) -> str:
        """
        Upload a video to YouTube.
        
        Args:
            args_str: JSON string with arguments
            
        Returns:
            Result of the upload operation as a string
        """
        try:
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
            video_url = args.get("video_url")
            title = args.get("title")
            description = args.get("description", "")
            tags = args.get("tags", [])
            
            if not video_url or not title:
                return json.dumps({"error": "Missing required parameters: video_url and title"})
            
            logger.info(f"Uploading video: {title} from {video_url}")
            
            # For now, we'll return a placeholder since we're not using YouTubeClient
            logger.info(f"Simulating upload of video: {title}")
            
            return json.dumps({
                "success": True,
                "youtube_id": "simulated_youtube_id",
                "message": f"Video '{title}' upload simulated successfully"
            })
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return json.dumps({"error": f"Error uploading video: {str(e)}"})
    
    def fetch_comments(self, args_str: str) -> str:
        """
        Fetch comments for a YouTube video.
        
        Args:
            args_str: JSON string with arguments
            
        Returns:
            Comments for the video as a string
        """
        try:
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
            youtube_id = args.get("youtube_id")
            max_results = args.get("max_results", 100)
            
            if not youtube_id:
                return json.dumps({"error": "Missing required parameter: youtube_id"})
            
            logger.info(f"Fetching comments for video: {youtube_id} (max: {max_results})")
            
            # For now, we'll return a placeholder since we're not using YouTubeClient
            logger.info(f"Simulating fetching comments for video: {youtube_id}")
            
            return json.dumps({
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
            })
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return json.dumps({"error": f"Error fetching comments: {str(e)}"})
    
    def analyze_music(self, args_str: str) -> str:
        """
        Analyze music and generate a description.
        
        Args:
            args_str: JSON string with arguments
            
        Returns:
            Analysis results as a string
        """
        try:
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
            audio_url = args.get("audio_url")
            analysis_type = args.get("analysis_type", "basic")
            
            if not audio_url:
                return json.dumps({"error": "Missing required parameter: audio_url"})
            
            logger.info(f"Analyzing music: {audio_url} (type: {analysis_type})")
            
            # This would integrate with Angus's music analysis capabilities
            # For now, we'll return a placeholder
            
            logger.info(f"Completed music analysis for: {audio_url}")
            
            return json.dumps({
                "success": True,
                "analysis": "Music analysis would be performed here",
                "details": {
                    "audio_url": audio_url,
                    "analysis_type": analysis_type
                }
            })
        except Exception as e:
            logger.error(f"Error analyzing music: {str(e)}")
            return json.dumps({"error": f"Error analyzing music: {str(e)}"})
    
    def handle_mention(self, thread_id, sender_id, message):
        """
        Handle a mention from another agent.
        
        Args:
            thread_id: ID of the thread
            sender_id: ID of the sender
            message: Message content
        """
        logger.info(f"Received mention in thread {thread_id} from {sender_id}: {message}")
        
        try:
            # Take time to interpret the instruction
            time.sleep(2)
            
            # Parse the instruction
            instruction = message.strip()
            
            # Determine which tool to use
            response = None
            if "upload" in instruction.lower() and "video" in instruction.lower():
                # Extract parameters from the instruction
                args = {
                    "video_url": "https://example.com/video.mp4",
                    "title": "Example Video"
                }
                response = self.upload_video(args)
            elif "fetch" in instruction.lower() and "comment" in instruction.lower():
                # Extract parameters from the instruction
                args = {
                    "youtube_id": "example_youtube_id"
                }
                response = self.fetch_comments(args)
            elif "analyze" in instruction.lower() and "music" in instruction.lower():
                # Extract parameters from the instruction
                args = {
                    "audio_url": "https://example.com/audio.mp3"
                }
                response = self.analyze_music(args)
            else:
                response = json.dumps({
                    "error": f"I don't understand how to handle: {instruction}"
                })
            
            # Take time to formulate a response
            time.sleep(3)
            
            # Send the response
            from langchain_mcp_adapters import send_message
            send_message(thread_id, response, [sender_id])
            
            logger.info(f"Sent response in thread {thread_id} to {sender_id}")
            
        except Exception as e:
            logger.error(f"Error handling mention: {str(e)}")
            traceback.print_exc()
    
    def run(self):
        """
        Run the Angus Coral agent.
        
        This method starts the agent and connects it to the Coral Protocol server.
        """
        logger.info(f"Starting Angus Coral Agent with server URL: {self.coral_server_url}")
        
        try:
            # Import Coral Protocol tools
            from langchain_mcp_adapters import list_agents, wait_for_mentions, create_thread, send_message
            
            # Configure the base URL
            langchain_mcp_adapters.base_url = self.coral_server_url
            
            # Set up agent parameters
            langchain_mcp_adapters.agent_id = self.agent_id
            langchain_mcp_adapters.agent_description = self.agent_description
            langchain_mcp_adapters.wait_for_agents = 2  # Wait for 2 agents to be available
            
            logger.info("Agent configured with Coral Protocol server")
            
            # Main loop
            while True:
                try:
                    # Wait for mentions
                    logger.info("Waiting for mentions...")
                    mentions = wait_for_mentions(timeout=8)
                    
                    if mentions:
                        for mention in mentions:
                            thread_id = mention.get("threadId")
                            sender_id = mention.get("senderId")
                            message = mention.get("message")
                            
                            # Handle the mention
                            self.handle_mention(thread_id, sender_id, message)
                    
                    # Wait before checking for mentions again
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}")
                    traceback.print_exc()
                    time.sleep(5)  # Wait before retrying
                
        except KeyboardInterrupt:
            logger.info("Angus Coral Agent stopped by user")
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
