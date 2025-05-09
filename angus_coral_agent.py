#!/usr/bin/env python3
"""
Angus Coral Agent - Integration between Angus and Coral Protocol

This script implements a Coral Protocol agent that exposes Angus's capabilities
to other agents in the Coral ecosystem.
"""
import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional

# Import Angus components
from supabase_client import SupabaseClient
from youtube_client import YouTubeClient

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

# Tool definitions
upload_video_tool = {
    "name": "upload_video",
    "description": "Upload a video to YouTube",
    "parameters": {
        "type": "object",
        "properties": {
            "video_url": {
                "type": "string",
                "description": "URL of the video file to upload"
            },
            "title": {
                "type": "string",
                "description": "Title of the video"
            },
            "description": {
                "type": "string",
                "description": "Description of the video"
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Tags for the video"
            }
        },
        "required": ["video_url", "title"]
    }
}

fetch_comments_tool = {
    "name": "fetch_comments",
    "description": "Fetch comments for a YouTube video",
    "parameters": {
        "type": "object",
        "properties": {
            "youtube_id": {
                "type": "string",
                "description": "YouTube video ID"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of comments to retrieve"
            }
        },
        "required": ["youtube_id"]
    }
}

analyze_music_tool = {
    "name": "analyze_music",
    "description": "Analyze music and generate a description",
    "parameters": {
        "type": "object",
        "properties": {
            "audio_url": {
                "type": "string",
                "description": "URL of the audio file to analyze"
            },
            "analysis_type": {
                "type": "string",
                "enum": ["basic", "detailed"],
                "description": "Type of analysis to perform"
            }
        },
        "required": ["audio_url"]
    }
}

class AngusCoral:
    """
    Angus Coral Agent - Exposes Angus capabilities to the Coral Protocol
    """
    
    def __init__(self, coral_server_url="https://coral.pushcollective.club/sse"):
        """
        Initialize the Angus Coral Agent.
        
        Args:
            coral_server_url: URL of the Coral Protocol Server
        """
        # Initialize Angus components
        self.supabase = SupabaseClient()
        self.youtube = YouTubeClient()
        
        # Coral server connection
        self.coral_url = coral_server_url
        self.agent_id = "angus_agent"
        self.agent_description = "Angus is a YouTube publishing and feedback collection agent that can upload videos, retrieve comments, and analyze music."
        self.agent_did = None  # Will be assigned by Coral server
        
        # Define tools
        self.tools = [
            upload_video_tool,
            fetch_comments_tool,
            analyze_music_tool
        ]
        
        # Tool implementations
        self.tool_implementations = {
            "upload_video": self.upload_video,
            "fetch_comments": self.fetch_comments,
            "analyze_music": self.analyze_music
        }
        
        logger.info("Angus Coral Agent initialized")
        
    def register_agent(self):
        """
        Register with the Coral server.
        
        Returns:
            True if registration was successful, False otherwise
        """
        logger.info(f"Registering with Coral server at {self.coral_url}")
        
        # Registration data based on Coral Protocol examples
        registration_data = {
            "agentId": self.agent_id,
            "agentDescription": self.agent_description,
            "tools": self.tools,
            "waitForAgents": 2  # Wait for at least 2 agents to be available
        }
        
        try:
            # Send registration request
            response = requests.post(
                f"{self.coral_url}/register",
                json=registration_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.agent_did = result.get("agentDid")
                logger.info(f"Successfully registered with Coral server. Agent DID: {self.agent_did}")
                return True
            else:
                logger.error(f"Failed to register with Coral server: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error registering with Coral server: {str(e)}")
            return False
    
    def listen_for_messages(self):
        """
        Listen for messages from other agents.
        
        This method runs in a loop, continuously checking for new messages.
        """
        logger.info("Starting to listen for messages")
        
        # Connect to SSE endpoint
        sse_url = f"{self.coral_url}/events?agentId={self.agent_id}"
        logger.info(f"SSE URL: {sse_url}")
        
        # Implementation would use SSE client to listen for events
        # For simplicity, we'll use a polling approach here
        while True:
            try:
                # Poll for new messages
                response = requests.get(f"{self.coral_url}/messages?agentId={self.agent_id}")
                
                if response.status_code == 200:
                    messages = response.json()
                    
                    if messages:
                        logger.info(f"Received {len(messages)} new messages")
                        
                        for message in messages:
                            self.process_message(message)
                
                # Wait before polling again
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error listening for messages: {str(e)}")
                time.sleep(5)  # Wait longer after an error
    
    def process_message(self, message: Dict[str, Any]):
        """
        Process a message from another agent.
        
        Args:
            message: Message data from the Coral server
        """
        # Extract message details
        thread_id = message.get("threadId")
        sender_id = message.get("senderId")
        content = message.get("content", {})
        
        logger.info(f"Processing message from {sender_id} in thread {thread_id}")
        logger.info(f"Message content: {content}")
        
        # Check if this is a tool invocation
        tool_name = content.get("tool")
        tool_params = content.get("parameters", {})
        
        if tool_name and tool_name in self.tool_implementations:
            # Execute the tool
            logger.info(f"Executing tool: {tool_name} with parameters: {tool_params}")
            
            try:
                result = self.tool_implementations[tool_name](tool_params)
                
                # Send the result back
                self.send_message(thread_id, sender_id, {
                    "result": result,
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                
                # Send error message
                self.send_message(thread_id, sender_id, {
                    "error": str(e),
                    "status": "error"
                })
        else:
            logger.warning(f"Received message with unknown tool: {tool_name}")
            
            # Send error message
            self.send_message(thread_id, sender_id, {
                "error": f"Unknown tool: {tool_name}",
                "status": "error"
            })
    
    def send_message(self, thread_id: str, recipient_id: str, content: Dict[str, Any]):
        """
        Send a message to another agent.
        
        Args:
            thread_id: ID of the thread
            recipient_id: ID of the recipient agent
            content: Message content
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        logger.info(f"Sending message to {recipient_id} in thread {thread_id}")
        
        message_data = {
            "threadId": thread_id,
            "senderId": self.agent_id,
            "recipientId": recipient_id,
            "content": content
        }
        
        try:
            response = requests.post(
                f"{self.coral_url}/send",
                json=message_data
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent message to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    # Tool implementations
    def upload_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a video to YouTube.
        
        Args:
            params: Tool parameters
            
        Returns:
            Result of the upload operation
        """
        title = params.get("title")
        video_url = params.get("video_url")
        description = params.get("description", "")
        tags = params.get("tags", [])
        
        logger.info(f"Uploading video: {title} from {video_url}")
        
        # Call Angus's upload functionality
        youtube_id = self.youtube.upload_video(
            video_url=video_url,
            title=title,
            description=description,
            tags=tags
        )
        
        if youtube_id == "URL_EXPIRED":
            logger.warning(f"Video URL has expired: {video_url}")
            return {
                "success": False,
                "error": "Video URL has expired",
                "status": "url_expired"
            }
        
        if youtube_id:
            logger.info(f"Successfully uploaded video: {title} with ID: {youtube_id}")
        else:
            logger.error(f"Failed to upload video: {title}")
        
        return {
            "success": youtube_id is not None,
            "youtube_id": youtube_id,
            "message": f"Video '{title}' uploaded successfully" if youtube_id else "Upload failed"
        }
    
    def fetch_comments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch comments for a YouTube video.
        
        Args:
            params: Tool parameters
            
        Returns:
            Comments for the video
        """
        youtube_id = params.get("youtube_id")
        max_results = params.get("max_results", 100)
        
        logger.info(f"Fetching comments for video: {youtube_id} (max: {max_results})")
        
        # Call Angus's comment fetching functionality
        comments = self.youtube.fetch_comments(youtube_id, max_results=max_results)
        
        logger.info(f"Retrieved {len(comments)} comments for video: {youtube_id}")
        
        return {
            "success": True,
            "comments": comments,
            "count": len(comments)
        }
    
    def analyze_music(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze music and generate a description.
        
        Args:
            params: Tool parameters
            
        Returns:
            Analysis results
        """
        audio_url = params.get("audio_url")
        analysis_type = params.get("analysis_type", "basic")
        
        logger.info(f"Analyzing music: {audio_url} (type: {analysis_type})")
        
        # This would integrate with Angus's music analysis capabilities
        # For now, we'll return a placeholder
        
        logger.info(f"Completed music analysis for: {audio_url}")
        
        return {
            "success": True,
            "analysis": "Music analysis would be performed here",
            "details": params
        }
    
    def run(self):
        """
        Run the Angus Coral agent.
        
        This method registers the agent and starts listening for messages.
        """
        if self.register_agent():
            logger.info("Starting to listen for messages")
            self.listen_for_messages()
        else:
            logger.error("Failed to register agent. Exiting.")

def main():
    """
    Main entry point for the Angus Coral Agent.
    """
    # Get Coral server URL from environment variable or use default
    coral_server_url = os.environ.get("CORAL_SERVER_URL", "https://coral.pushcollective.club/sse")
    
    # Create and run the agent
    agent = AngusCoral(coral_server_url=coral_server_url)
    agent.run()

if __name__ == "__main__":
    main()
