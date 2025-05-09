"""
Angus Coral Adapter

This module provides the adapter for connecting the Angus agent to the Coral Protocol.
"""
import os
import logging
from typing import Dict, Any, List, Optional

from openai import OpenAI
from langchain_community.llms import OpenAI as LangChainOpenAI
from langchain_openai.chat_models import ChatOpenAI

from angus_agent import AngusAgent
from src.coral_protocol.langchain import CoralRunnableConfig, CoralRunnable

logger = logging.getLogger(__name__)

class AngusCoralAdapter:
    """
    Adapter for connecting the Angus agent to the Coral Protocol.
    """
    
    def __init__(
        self,
        angus_agent: AngusAgent,
        coral_server_url: str,
        openai_api_key: Optional[str] = None,
        did_domain: str = "angus.ai",
        private_key_path: Optional[str] = None
    ):
        """
        Initialize the Angus Coral adapter.
        
        Args:
            angus_agent: Angus agent instance
            coral_server_url: URL of the Coral Protocol server
            openai_api_key: OpenAI API key
            did_domain: Domain for the DID
            private_key_path: Path to the private key file
        """
        self.angus_agent = angus_agent
        self.coral_server_url = coral_server_url
        self.openai_api_key = openai_api_key or angus_agent.openai_api_key
        
        # Use the DID manager from the Angus agent
        self.did_manager = angus_agent.did_manager
        self.capability_generator = angus_agent.capability_generator
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(api_key=self.openai_api_key)
        
        # Create Coral runnable configuration
        self.coral_config = CoralRunnableConfig(
            server_url=coral_server_url,
            did=self.did_manager.did,
            private_key=self._get_private_key_bytes(),
            capability_document=self.capability_generator.generate()
        )
        
        # Create Coral runnable
        self.coral_runnable = self._create_coral_runnable()
        
        logger.info(f"Initialized Angus Coral Adapter with server URL: {coral_server_url}")
    
    def _get_private_key_bytes(self) -> bytes:
        """
        Get the private key as bytes.
        
        Returns:
            Private key as bytes
        """
        return self.angus_agent.get_private_key_bytes()
    
    def _create_coral_runnable(self) -> CoralRunnable:
        """
        Create a Coral runnable for the Angus agent.
        
        Returns:
            CoralRunnable instance
        """
        # Define the functions to expose through Coral
        functions = {
            "upload_video": self.angus_agent.upload_video,
            "fetch_comments": self.angus_agent.fetch_comments,
            "analyze_music": self.angus_agent.analyze_music
        }
        
        # Create the Coral runnable
        coral_runnable = CoralRunnable(
            functions=functions,
            config=self.coral_config
        )
        
        return coral_runnable
    
    def register_with_coral_server(self) -> bool:
        """
        Register the Angus agent with the Coral Protocol server.
        
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            logger.info("Registering Angus agent with Coral Protocol server")
            
            # Register the agent
            success = self.coral_runnable.register()
            
            if success:
                logger.info("Angus agent registered successfully with Coral Protocol server")
            else:
                logger.error("Failed to register Angus agent with Coral Protocol server")
            
            return success
        except Exception as e:
            logger.error(f"Error registering Angus agent with Coral Protocol server: {str(e)}")
            return False
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """
        Discover agents on the Coral Protocol server.
        
        Returns:
            List of agents
        """
        try:
            logger.info("Discovering agents on Coral Protocol server")
            
            # List agents
            agents = self.coral_runnable.list_agents()
            
            logger.info(f"Discovered {len(agents)} agents on Coral Protocol server")
            
            return agents
        except Exception as e:
            logger.error(f"Error discovering agents on Coral Protocol server: {str(e)}")
            return []
    
    def create_thread(self) -> Optional[str]:
        """
        Create a thread on the Coral Protocol server.
        
        Returns:
            Thread ID if successful, None otherwise
        """
        try:
            logger.info("Creating thread on Coral Protocol server")
            
            # Create thread
            thread_id = self.coral_runnable.create_thread()
            
            if thread_id:
                logger.info(f"Thread created successfully: {thread_id}")
            else:
                logger.error("Failed to create thread")
            
            return thread_id
        except Exception as e:
            logger.error(f"Error creating thread on Coral Protocol server: {str(e)}")
            return None
    
    def send_message(self, thread_id: str, message: str, mentions: List[str]) -> bool:
        """
        Send a message to a thread on the Coral Protocol server.
        
        Args:
            thread_id: ID of the thread
            message: Message content
            mentions: List of agent IDs to mention
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending message to thread {thread_id} with mentions {mentions}")
            
            # Send message
            success = self.coral_runnable.send_message(thread_id, message, mentions)
            
            if success:
                logger.info(f"Message sent successfully to thread {thread_id}")
            else:
                logger.error(f"Failed to send message to thread {thread_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error sending message to thread {thread_id}: {str(e)}")
            return False
    
    def get_agent_capabilities(self, agent_did: str) -> Optional[Dict[str, Any]]:
        """
        Get the capabilities of an agent on the Coral Protocol server.
        
        Args:
            agent_did: DID of the agent
            
        Returns:
            Capabilities of the agent if successful, None otherwise
        """
        try:
            logger.info(f"Getting capabilities for agent {agent_did}")
            
            # This would call a method on the Coral runnable to get agent capabilities
            # For now, we'll return a placeholder
            
            logger.info(f"Simulating getting capabilities for agent {agent_did}")
            
            return {
                "name": "Example Agent",
                "description": "An example agent",
                "capabilities": {
                    "example_function": {
                        "description": "An example function",
                        "parameters": {
                            "param1": {
                                "type": "string",
                                "description": "Parameter 1"
                            }
                        },
                        "returns": {
                            "type": "object",
                            "properties": {
                                "result": {
                                    "type": "string",
                                    "description": "Result of the function"
                                }
                            }
                        }
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting capabilities for agent {agent_did}: {str(e)}")
            return None
    
    def call_agent(self, agent_did: str, function_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Call a function on an agent on the Coral Protocol server.
        
        Args:
            agent_did: DID of the agent
            function_name: Name of the function to call
            **kwargs: Arguments for the function
            
        Returns:
            Result of the function call if successful, None otherwise
        """
        try:
            logger.info(f"Calling function {function_name} on agent {agent_did}")
            
            # This would create a thread, send a message with the function call,
            # and wait for a response
            
            # Create thread
            thread_id = self.create_thread()
            if not thread_id:
                logger.error("Failed to create thread for function call")
                return None
            
            # Prepare message
            message = {
                "function": function_name,
                "arguments": kwargs
            }
            
            # Send message
            agent_id = agent_did.split(':')[-1]
            success = self.send_message(thread_id, str(message), [agent_id])
            if not success:
                logger.error(f"Failed to send message for function call to agent {agent_did}")
                return None
            
            # For now, we'll return a placeholder
            logger.info(f"Simulating function call {function_name} on agent {agent_did}")
            
            return {
                "success": True,
                "result": f"Result of {function_name} call"
            }
        except Exception as e:
            logger.error(f"Error calling function {function_name} on agent {agent_did}: {str(e)}")
            return None
    
    def start_server(self, host: str = '0.0.0.0', port: int = 5002):
        """
        Start the Coral server for the Angus agent.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        try:
            logger.info(f"Starting Coral server for Angus agent on {host}:{port}")
            
            # Start the Coral runnable
            self.coral_runnable.start()
            
            # Keep the server running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping Coral server for Angus agent")
                self.coral_runnable.stop()
            
        except Exception as e:
            logger.error(f"Error starting Coral server for Angus agent: {str(e)}")
            self.coral_runnable.stop()
