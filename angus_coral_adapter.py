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
            
            # Check if we have a session ID
            if hasattr(self.coral_runnable, 'session_id') and self.coral_runnable.session_id:
                # Construct the discover URL using the session ID
                from urllib.parse import urlparse, urljoin
                
                parsed_url = urlparse(self.coral_server_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
                discover_url = f"{base_url}/devmode/default-app/default-key/session1/discover?sessionId={self.coral_runnable.session_id}"
                
                logger.info(f"Using session-based discovery URL: {discover_url}")
                
                # Make the request
                response = requests.get(
                    discover_url,
                    headers=self.coral_runnable.config.headers,
                    timeout=self.coral_runnable.config.timeout,
                    verify=self.coral_runnable.config.verify_ssl
                )
                
                if response.status_code == 200:
                    agents = response.json().get("agents", [])
                    logger.info(f"Discovered {len(agents)} agents using session-based discovery")
                    
                    # Log each discovered agent
                    for agent in agents:
                        logger.info(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
                    
                    # Store the discovered agents
                    if hasattr(self.coral_runnable, 'known_agents'):
                        self.coral_runnable.known_agents = agents
                    
                    return agents
                else:
                    logger.warning(f"Session-based discovery failed: {response.status_code} - {response.text}")
            
            # Fall back to the list_agents method
            logger.info("Falling back to standard agent listing")
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
            
            # Check if we have a session ID
            if hasattr(self.coral_runnable, 'session_id') and self.coral_runnable.session_id:
                # Construct the capabilities URL using the session ID
                from urllib.parse import urlparse, urljoin
                
                parsed_url = urlparse(self.coral_server_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
                capabilities_url = f"{base_url}/devmode/default-app/default-key/session1/capabilities?sessionId={self.coral_runnable.session_id}&targetDid={agent_did}"
                
                logger.info(f"Using session-based capabilities URL: {capabilities_url}")
                
                # Make the request
                response = requests.get(
                    capabilities_url,
                    headers=self.coral_runnable.config.headers,
                    timeout=self.coral_runnable.config.timeout,
                    verify=self.coral_runnable.config.verify_ssl
                )
                
                if response.status_code == 200:
                    capabilities = response.json()
                    logger.info(f"Successfully retrieved capabilities for agent {agent_did}")
                    
                    # Log the capabilities
                    if "services" in capabilities:
                        logger.info(f"Agent provides {len(capabilities['services'])} services:")
                        for service in capabilities["services"]:
                            logger.info(f"  - {service.get('id')}: {service.get('description', 'No description')}")
                    
                    return capabilities
                else:
                    logger.warning(f"Session-based capabilities retrieval failed: {response.status_code} - {response.text}")
            
            # Fall back to the placeholder implementation
            logger.warning("Using placeholder implementation for agent capabilities")
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
            
            # Check if we have a message endpoint and session ID
            if (hasattr(self.coral_runnable, 'message_endpoint') and self.coral_runnable.message_endpoint and
                hasattr(self.coral_runnable, 'session_id') and self.coral_runnable.session_id):
                
                import uuid
                
                # Construct the message payload
                payload = {
                    "type": "function_call",
                    "source": self.did_manager.did,
                    "target": agent_did,
                    "function": function_name,
                    "arguments": kwargs,
                    "id": str(uuid.uuid4())
                }
                
                # Construct the message URL
                from urllib.parse import urlparse, urljoin
                
                parsed_url = urlparse(self.coral_server_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                # Check if the message endpoint is a relative URL
                message_endpoint = self.coral_runnable.message_endpoint
                if not message_endpoint.startswith('http'):
                    message_url = urljoin(base_url, f"{message_endpoint}?sessionId={self.coral_runnable.session_id}")
                else:
                    # It's an absolute URL
                    message_url = f"{message_endpoint}?sessionId={self.coral_runnable.session_id}"
                
                logger.info(f"Using direct message URL for function call: {message_url}")
                
                # Send the function call
                response = requests.post(
                    message_url,
                    headers=self.coral_runnable.config.headers,
                    json=payload,
                    timeout=self.coral_runnable.config.timeout,
                    verify=self.coral_runnable.config.verify_ssl
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully sent function call to agent {agent_did}")
                    return {"status": "sent", "message_id": payload["id"]}
                else:
                    logger.warning(f"Direct function call failed: {response.status_code} - {response.text}")
            
            # Fall back to the thread-based approach
            logger.info("Falling back to thread-based function call approach")
            
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
    
    def _handle_function_call(self, message_data: Dict[str, Any]):
        """
        Handle a function call from another agent.
        
        Args:
            message_data: Message data
        """
        try:
            # Extract function call details
            source_did = message_data.get("source")
            function_name = message_data.get("function")
            arguments = message_data.get("arguments", {})
            message_id = message_data.get("id")
            
            logger.info(f"Received function call from {source_did}: {function_name}")
            logger.info(f"Arguments: {arguments}")
            
            # Check if the function exists
            if function_name in self.coral_runnable.functions:
                # Call the function
                try:
                    result = self.coral_runnable.functions[function_name](**arguments)
                    
                    # Send the response
                    self._send_function_response(source_did, message_id, result)
                except Exception as e:
                    logger.error(f"Error executing function {function_name}: {str(e)}")
                    self._send_function_response(source_did, message_id, {"error": str(e)}, success=False)
            else:
                logger.warning(f"Function {function_name} not found")
                self._send_function_response(source_did, message_id, {"error": f"Function {function_name} not found"}, success=False)
        except Exception as e:
            logger.error(f"Error handling function call: {str(e)}")
    
    def _send_function_response(self, target_did: str, message_id: str, result: Any, success: bool = True):
        """
        Send a function response to another agent.
        
        Args:
            target_did: DID of the target agent
            message_id: ID of the message being responded to
            result: Result of the function call
            success: Whether the function call was successful
        """
        try:
            import uuid
            
            # Construct the response payload
            payload = {
                "type": "function_response",
                "source": self.did_manager.did,
                "target": target_did,
                "in_response_to": message_id,
                "success": success,
                "result": result,
                "id": str(uuid.uuid4())
            }
            
            # Check if we have a message endpoint and session ID
            if (hasattr(self.coral_runnable, 'message_endpoint') and self.coral_runnable.message_endpoint and
                hasattr(self.coral_runnable, 'session_id') and self.coral_runnable.session_id):
                
                # Construct the message URL
                from urllib.parse import urlparse, urljoin
                
                parsed_url = urlparse(self.coral_server_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                # Check if the message endpoint is a relative URL
                message_endpoint = self.coral_runnable.message_endpoint
                if not message_endpoint.startswith('http'):
                    message_url = urljoin(base_url, f"{message_endpoint}?sessionId={self.coral_runnable.session_id}")
                else:
                    # It's an absolute URL
                    message_url = f"{message_endpoint}?sessionId={self.coral_runnable.session_id}"
                
                logger.info(f"Using direct message URL for function response: {message_url}")
                
                # Send the function response
                response = requests.post(
                    message_url,
                    headers=self.coral_runnable.config.headers,
                    json=payload,
                    timeout=self.coral_runnable.config.timeout,
                    verify=self.coral_runnable.config.verify_ssl
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully sent function response to agent {target_did}")
                else:
                    logger.error(f"Failed to send function response: {response.status_code} - {response.text}")
            else:
                logger.error("Cannot send function response: no message endpoint or session ID available")
        except Exception as e:
            logger.error(f"Error sending function response: {str(e)}")
    
    def _handle_function_response(self, message_data: Dict[str, Any]):
        """
        Handle a function response from another agent.
        
        Args:
            message_data: Message data
        """
        try:
            # Extract function response details
            source_did = message_data.get("source")
            in_response_to = message_data.get("in_response_to")
            success = message_data.get("success", False)
            result = message_data.get("result")
            
            logger.info(f"Received function response from {source_did} for message {in_response_to}")
            logger.info(f"Success: {success}")
            logger.info(f"Result: {result}")
            
            # TODO: Handle the function response, e.g., by notifying a waiting thread
            
        except Exception as e:
            logger.error(f"Error handling function response: {str(e)}")
    
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
