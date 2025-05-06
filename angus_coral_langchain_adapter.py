"""
Coral Protocol LangChain Integration for Angus

This module provides integration between Angus and the Coral Protocol
using LangChain.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

from src.coral_protocol.langchain import CoralRunnable, CoralRunnableConfig
from langchain.schema.runnable import Runnable
from langchain_openai import ChatOpenAI

# Import Angus components
from angus import AgentAngus
from angus_tools import AngusTools
from angus_crew import AngusCrew

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AngusCoralLangChainAdapter:
    """
    Adapter for integrating Angus with the Coral Protocol using LangChain.
    
    This class provides functionality for:
    - Registering Angus's capabilities with a Coral server
    - Handling requests from other agents through the Coral Protocol
    - Sending requests to other agents through the Coral Protocol
    """
    
    def __init__(self, 
                 coral_server_url: str,
                 openai_api_key: Optional[str] = None,
                 did_domain: str = "angus.ai",
                 private_key_path: Optional[str] = None):
        """
        Initialize the Angus Coral LangChain Adapter.
        
        Args:
            coral_server_url: URL of the Coral server
            openai_api_key: API key for OpenAI (optional, will use environment variable if not provided)
            did_domain: Domain for the did:web identifier
            private_key_path: Path to a file containing a private key for DID
        """
        # Initialize Angus components
        self.angus_agent = AgentAngus()
        self.angus_tools = AngusTools()
        self.angus_crew = AngusCrew()
        
        self.coral_server_url = coral_server_url
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize DID (in a real implementation, this would use a proper DID library)
        self.did = f"did:web:{did_domain}"
        self.private_key = self._get_or_create_private_key(private_key_path)
        
        # Create capability document
        self.capability_document = self._create_capability_document()
        
        # Create Coral runnable configuration
        self.coral_config = CoralRunnableConfig(
            server_url=coral_server_url,
            did=self.did,
            private_key=self.private_key,
            capability_document=self.capability_document,
            agent_name="Agent Angus",
            agent_description="AI agent for YouTube publishing and audience engagement"
        )
        
        # Create Coral runnable
        self.coral_runnable = self._create_coral_runnable()
        
        logger.info(f"AngusCoralLangChainAdapter initialized with DID: {self.did}")
        logger.info(f"Connected to Coral server at: {coral_server_url}")
    
    def _get_or_create_private_key(self, private_key_path: Optional[str]) -> bytes:
        """
        Get or create a private key for DID.
        
        Args:
            private_key_path: Path to a file containing a private key
            
        Returns:
            Private key as bytes
        """
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, 'rb') as f:
                return f.read()
        
        # In a real implementation, this would generate a proper private key
        # For now, we'll just return a placeholder
        return b'placeholder_private_key'
    
    def _create_capability_document(self) -> Dict[str, Any]:
        """
        Create a capability document for Angus.
        
        Returns:
            Dictionary containing Angus's capabilities
        """
        return {
            "name": "Agent Angus",
            "description": "AI agent for YouTube publishing and audience engagement",
            "functions": [
                {
                    "name": "upload_videos",
                    "description": "Upload pending songs from Supabase to YouTube",
                    "parameters": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of videos to upload",
                            "default": 5
                        }
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "count": {"type": "integer"},
                            "message": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "manage_comments",
                    "description": "Fetch comments from YouTube videos and respond using OpenAI",
                    "parameters": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of videos to process",
                            "default": 10
                        },
                        "max_replies": {
                            "type": "integer",
                            "description": "Maximum number of replies to post",
                            "default": 5
                        }
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "count": {"type": "integer"},
                            "message": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "analyze_music",
                    "description": "Analyze music using OpenAI to extract insights",
                    "parameters": {
                        "url": {
                            "type": "string",
                            "description": "URL of the music file or YouTube video"
                        },
                        "is_youtube": {
                            "type": "boolean",
                            "description": "Whether the URL is a YouTube video",
                            "default": False
                        },
                        "model": {
                            "type": "string",
                            "description": "OpenAI model to use",
                            "default": "gpt-4o",
                            "enum": ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
                        }
                    },
                    "returns": {
                        "type": "object",
                        "description": "Detailed music analysis including lyrics, genres, moods, and more"
                    }
                }
            ]
        }
    
    def _create_coral_runnable(self) -> CoralRunnable:
        """
        Create a Coral runnable with Angus's capabilities.
        
        Returns:
            CoralRunnable instance
        """
        # Define the functions to expose through Coral
        functions = {
            "upload_videos": self._handle_upload_videos,
            "manage_comments": self._handle_manage_comments,
            "analyze_music": self._handle_analyze_music
        }
        
        # Create the Coral runnable
        coral_runnable = CoralRunnable(
            functions=functions,
            config=self.coral_config
        )
        
        return coral_runnable
    
    def _handle_upload_videos(self, limit: int = 5) -> Dict[str, Any]:
        """
        Handle upload_videos function call from Coral Protocol.
        
        Args:
            limit: Maximum number of videos to upload
            
        Returns:
            Dictionary with result information
        """
        try:
            # Use the Angus agent to upload videos
            count = self.angus_agent.upload_all_pending_songs(limit=limit)
            
            return {
                "success": True,
                "count": count,
                "message": f"Successfully uploaded {count} videos to YouTube"
            }
        except Exception as e:
            logger.error(f"Error handling upload_videos: {str(e)}")
            
            # Check if this is an upload limit exceeded error
            error_str = str(e)
            if "uploadLimitExceeded" in error_str or "The user has exceeded the number of videos they may upload" in error_str:
                return {
                    "success": False,
                    "count": 0,
                    "message": "YouTube upload limit exceeded. Try again later.",
                    "error": "UPLOAD_LIMIT_EXCEEDED"
                }
            
            return {
                "success": False,
                "count": 0,
                "message": f"Error uploading videos: {str(e)}",
                "error": "UPLOAD_ERROR"
            }
    
    def _handle_manage_comments(self, limit: int = 10, max_replies: int = 5) -> Dict[str, Any]:
        """
        Handle manage_comments function call from Coral Protocol.
        
        Args:
            limit: Maximum number of videos to process
            max_replies: Maximum number of replies to post
            
        Returns:
            Dictionary with result information
        """
        try:
            # Use the Angus agent to manage comments
            count = self.angus_agent.fetch_comments_for_all_videos(limit=limit, max_total_replies=max_replies)
            
            return {
                "success": True,
                "count": count,
                "message": f"Processed {count} comments across YouTube videos"
            }
        except Exception as e:
            logger.error(f"Error handling manage_comments: {str(e)}")
            return {
                "success": False,
                "count": 0,
                "message": f"Error managing comments: {str(e)}",
                "error": "COMMENT_ERROR"
            }
    
    def _handle_analyze_music(self, url: str, is_youtube: bool = False, model: str = "gpt-4o") -> Dict[str, Any]:
        """
        Handle analyze_music function call from Coral Protocol.
        
        Args:
            url: URL of the music file or YouTube video
            is_youtube: Whether the URL is a YouTube video
            model: OpenAI model to use
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Import the analyze_music function from openai_utils
            from openai_utils import analyze_music
            
            # Analyze the music
            result = analyze_music(url, is_youtube_url=is_youtube, model=model)
            
            # Check if there was an error
            if "error" in result:
                return {
                    "success": False,
                    "message": f"Error analyzing music: {result.get('details', 'Unknown error')}",
                    "error": "ANALYSIS_ERROR"
                }
            
            # Return the analysis results
            return {
                "success": True,
                "message": "Successfully analyzed music",
                "analysis": result
            }
        except Exception as e:
            logger.error(f"Error handling analyze_music: {str(e)}")
            return {
                "success": False,
                "message": f"Error analyzing music: {str(e)}",
                "error": "ANALYSIS_ERROR"
            }
    
    def register_with_coral_server(self) -> bool:
        """
        Register Angus's capabilities with the Coral server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # The registration happens automatically when the CoralRunnable is created
            # We just need to make sure it's initialized
            if self.coral_runnable:
                logger.info(f"Successfully registered with Coral server at {self.coral_server_url}")
                return True
            else:
                logger.error("Coral runnable not initialized")
                return False
        except Exception as e:
            logger.error(f"Error registering with Coral server: {str(e)}")
            return False
    
    def call_agent(self, agent_did: str, function_name: str, **kwargs) -> Any:
        """
        Call a function on another agent through the Coral Protocol.
        
        Args:
            agent_did: DID of the agent to call
            function_name: Name of the function to call
            **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        try:
            logger.info(f"Calling {function_name} on agent {agent_did}")
            
            # Create the function call
            result = self.coral_runnable.call_agent(
                agent_did=agent_did,
                function_name=function_name,
                **kwargs
            )
            
            logger.info(f"Successfully called {function_name} on agent {agent_did}")
            return result
        except Exception as e:
            logger.error(f"Error calling agent {agent_did}: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """
        Discover agents registered with the Coral server.
        
        Returns:
            List of dictionaries containing agent information
        """
        try:
            logger.info(f"Discovering agents on Coral server {self.coral_server_url}")
            
            # Get the list of agents
            agents = self.coral_runnable.discover_agents()
            
            logger.info(f"Discovered {len(agents)} agents")
            return agents
        except Exception as e:
            logger.error(f"Error discovering agents: {str(e)}")
            return []
    
    def get_agent_capabilities(self, agent_did: str) -> Dict[str, Any]:
        """
        Get the capabilities of an agent.
        
        Args:
            agent_did: DID of the agent
            
        Returns:
            Dictionary containing the agent's capabilities
        """
        try:
            logger.info(f"Getting capabilities for agent {agent_did}")
            
            # Get the agent's capabilities
            capabilities = self.coral_runnable.get_agent_capabilities(agent_did)
            
            logger.info(f"Successfully retrieved capabilities for agent {agent_did}")
            return capabilities
        except Exception as e:
            logger.error(f"Error getting capabilities for agent {agent_did}: {str(e)}")
            return {}
    
    def start_server(self, host: str = '0.0.0.0', port: int = 5001) -> None:
        """
        Start a server to listen for requests from the Coral Protocol.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        try:
            logger.info(f"Starting Coral server on {host}:{port}")
            
            # Start the server
            self.coral_runnable.start_server(host=host, port=port)
            
            logger.info(f"Coral server started on {host}:{port}")
        except Exception as e:
            logger.error(f"Error starting Coral server: {str(e)}")
            raise
