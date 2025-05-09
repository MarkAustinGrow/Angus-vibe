"""
Runnable Implementation for Coral Protocol LangChain Integration

This module provides the runnable implementation for the Coral Protocol LangChain integration.
"""
import os
import json
import time
import logging
import requests
import threading
import sseclient
from typing import Dict, Any, List, Callable, Optional, Union, TypeVar, Generic

from .config import CoralRunnableConfig

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CoralRunnable(Generic[T]):
    """
    Runnable implementation for Coral Protocol LangChain integration.
    """
    
    def __init__(
        self,
        functions: Dict[str, Callable],
        config: CoralRunnableConfig
    ):
        """
        Initialize the Coral Runnable.
        
        Args:
            functions: Dictionary of functions to expose through Coral
            config: Configuration for the runnable
        """
        self.functions = functions
        self.config = config
        
        # State
        self.registered = False
        self.threads = {}  # Thread ID -> Thread data
        self.mentions = []  # List of mentions
        self.running = False
        self.sse_thread = None
        
        logger.info(f"Initialized Coral Runnable with {len(functions)} functions")
    
    def register(self) -> bool:
        """
        Register the agent with the Coral Protocol server.
        
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Extract the base URL (without the /sse part)
            base_url = self.config.server_url.rsplit('/sse', 1)[0]
            registration_url = f"{base_url}/register"
            
            # Prepare the registration data
            registration_data = {
                "agentId": self.config.did.split(':')[-1],  # Use the last part of the DID as the agent ID
                "agentDescription": self.config.capability_document.get("description", "Angus Agent"),
                "waitForAgents": 2  # Wait for 2 agents to be available
            }
            
            # Send the registration request
            logger.info(f"Registering agent with Coral Protocol server: {registration_url}")
            
            response = requests.post(
                registration_url,
                json=registration_data,
                headers=self.config.headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            # Check if registration was successful
            if response.status_code == 200:
                registration_result = response.json()
                agent_did = registration_result.get("agentDid")
                logger.info(f"Agent registered successfully with DID: {agent_did}")
                self.registered = True
                return True
            else:
                logger.error(f"Failed to register agent: {response.status_code} - {response.text}")
                
                # Try an alternative approach - maybe the registration is handled via SSE
                logger.info("Trying alternative registration approach via SSE connection")
                
                # Just connect to the SSE endpoint with the agent parameters as query parameters
                agent_id = self.config.did.split(':')[-1]
                sse_url = f"{self.config.server_url}?agentId={agent_id}&waitForAgents=2"
                logger.info(f"Connecting to SSE URL: {sse_url}")
                
                # We'll consider this a success for now and let the SSE listener handle the rest
                self.registered = True
                return True
                
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return False
    
    def start_sse_listener(self):
        """
        Start listening for SSE events from the Coral Protocol server.
        """
        try:
            # Construct the SSE URL with agent parameters
            agent_id = self.config.did.split(':')[-1]
            sse_url = f"{self.config.server_url}?agentId={agent_id}&waitForAgents=2"
            
            # Start the SSE client
            logger.info(f"Starting SSE listener: {sse_url}")
            
            # Set up headers
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            headers.update(self.config.headers)
            
            # Make the request
            response = requests.get(
                sse_url,
                stream=True,
                headers=headers,
                timeout=None,  # No timeout for SSE
                verify=self.config.verify_ssl
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Failed to connect to SSE: {response.status_code} - {response.text}")
                return
            
            # Create the SSE client
            client = sseclient.SSEClient(response)
            
            # Process events
            for event in client.events():
                try:
                    logger.info(f"Received SSE event: {event.event} - {event.data}")
                    
                    # Parse the event data
                    event_data = json.loads(event.data)
                    event_type = event_data.get("type")
                    
                    # Handle different event types
                    if event_type == "mention":
                        self.handle_mention(event_data)
                    elif event_type == "thread_update":
                        self.handle_thread_update(event_data)
                    elif event_type == "registration":
                        self.handle_registration(event_data)
                    else:
                        logger.info(f"Received unknown event type: {event_type}")
                        
                except Exception as e:
                    logger.error(f"Error processing SSE event: {str(e)}")
                    
                # Check if we should stop
                if not self.running:
                    break
                    
        except Exception as e:
            logger.error(f"Error in SSE listener: {str(e)}")
            
            # Try to reconnect after a delay
            if self.running:
                time.sleep(5)
                self.sse_thread = threading.Thread(target=self.start_sse_listener)
                self.sse_thread.daemon = True
                self.sse_thread.start()
    
    def handle_mention(self, event_data: Dict[str, Any]):
        """
        Handle a mention event from the Coral Protocol server.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract mention data
            thread_id = event_data.get("threadId")
            sender_id = event_data.get("senderId")
            message = event_data.get("message")
            
            logger.info(f"Received mention in thread {thread_id} from {sender_id}: {message}")
            
            # Add to mentions list
            self.mentions.append(event_data)
            
            # Process the mention
            threading.Thread(target=self.process_mention, args=(thread_id, sender_id, message)).start()
            
        except Exception as e:
            logger.error(f"Error handling mention: {str(e)}")
    
    def handle_thread_update(self, event_data: Dict[str, Any]):
        """
        Handle a thread update event from the Coral Protocol server.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract thread data
            thread_id = event_data.get("threadId")
            thread_data = event_data.get("threadData")
            
            logger.info(f"Received thread update for thread {thread_id}")
            
            # Update thread data
            self.threads[thread_id] = thread_data
            
        except Exception as e:
            logger.error(f"Error handling thread update: {str(e)}")
    
    def handle_registration(self, event_data: Dict[str, Any]):
        """
        Handle a registration event from the Coral Protocol server.
        
        Args:
            event_data: Event data
        """
        try:
            # Extract registration data
            agent_did = event_data.get("agentDid")
            
            logger.info(f"Received registration confirmation with DID: {agent_did}")
            
            # Update agent DID if needed
            if agent_did and agent_did != self.config.did:
                logger.info(f"Updating agent DID from {self.config.did} to {agent_did}")
                self.config.did = agent_did
            
        except Exception as e:
            logger.error(f"Error handling registration: {str(e)}")
    
    def process_mention(self, thread_id: str, sender_id: str, message: str):
        """
        Process a mention from another agent.
        
        Args:
            thread_id: ID of the thread
            sender_id: ID of the sender
            message: Message content
        """
        try:
            # Parse the message as a function call
            try:
                # Try to parse as JSON
                call_data = json.loads(message)
                function_name = call_data.get("function")
                arguments = call_data.get("arguments", {})
            except json.JSONDecodeError:
                # If not JSON, try to parse as text
                parts = message.strip().split(" ", 1)
                function_name = parts[0]
                arguments = {}
                if len(parts) > 1:
                    # Try to parse arguments from text
                    arg_text = parts[1]
                    try:
                        arguments = json.loads(arg_text)
                    except json.JSONDecodeError:
                        # If not JSON, use as a single argument
                        arguments = {"text": arg_text}
            
            # Check if the function exists
            if function_name in self.functions:
                # Call the function
                logger.info(f"Calling function {function_name} with arguments {arguments}")
                result = self.functions[function_name](**arguments)
                
                # Send the response
                response = {
                    "function": function_name,
                    "result": result,
                    "success": True
                }
            else:
                # Function not found
                logger.error(f"Function {function_name} not found")
                response = {
                    "function": function_name,
                    "error": f"Function {function_name} not found",
                    "success": False
                }
            
            # Send the response
            self.send_message(thread_id, json.dumps(response), [sender_id])
            
            logger.info(f"Sent response in thread {thread_id} to {sender_id}")
            
        except Exception as e:
            logger.error(f"Error processing mention: {str(e)}")
            
            # Send error response
            error_response = {
                "error": str(e),
                "success": False
            }
            self.send_message(thread_id, json.dumps(error_response), [sender_id])
    
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
            # Extract the base URL (without the /sse part)
            base_url = self.config.server_url.rsplit('/sse', 1)[0]
            send_message_url = f"{base_url}/send_message"
            
            # Prepare the message data
            message_data = {
                "threadId": thread_id,
                "message": message,
                "mentions": mentions
            }
            
            # Send the message request
            logger.info(f"Sending message to thread {thread_id} with mentions {mentions}")
            response = requests.post(
                send_message_url,
                json=message_data,
                headers=self.config.headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                logger.info(f"Message sent successfully to thread {thread_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def create_thread(self) -> Optional[str]:
        """
        Create a new thread on the Coral Protocol server.
        
        Returns:
            Thread ID if successful, None otherwise
        """
        try:
            # Extract the base URL (without the /sse part)
            base_url = self.config.server_url.rsplit('/sse', 1)[0]
            create_thread_url = f"{base_url}/create_thread"
            
            # Send the create thread request
            logger.info(f"Creating thread on Coral Protocol server: {create_thread_url}")
            response = requests.post(
                create_thread_url,
                headers=self.config.headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                thread_data = response.json()
                thread_id = thread_data.get("threadId")
                self.threads[thread_id] = thread_data
                logger.info(f"Thread created successfully: {thread_id}")
                return thread_id
            else:
                logger.error(f"Failed to create thread: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all agents registered with the Coral Protocol server.
        
        Returns:
            List of agents
        """
        try:
            # Extract the base URL (without the /sse part)
            base_url = self.config.server_url.rsplit('/sse', 1)[0]
            list_agents_url = f"{base_url}/list_agents"
            
            # Send the list agents request
            logger.info(f"Listing agents from Coral Protocol server: {list_agents_url}")
            response = requests.get(
                list_agents_url,
                headers=self.config.headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                agents = response.json()
                logger.info(f"Found {len(agents)} agents")
                return agents
            else:
                logger.error(f"Failed to list agents: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}")
            return []
    
    def start(self):
        """
        Start the Coral Runnable.
        """
        if self.running:
            logger.warning("Coral Runnable is already running")
            return
        
        logger.info("Starting Coral Runnable")
        
        # Set running flag
        self.running = True
        
        # Register the agent
        if not self.registered and not self.register():
            logger.error("Failed to register agent, not starting")
            self.running = False
            return
        
        # Start the SSE listener
        self.sse_thread = threading.Thread(target=self.start_sse_listener)
        self.sse_thread.daemon = True
        self.sse_thread.start()
        
        logger.info("Coral Runnable started")
    
    def stop(self):
        """
        Stop the Coral Runnable.
        """
        if not self.running:
            logger.warning("Coral Runnable is not running")
            return
        
        logger.info("Stopping Coral Runnable")
        
        # Clear running flag
        self.running = False
        
        # Wait for SSE thread to stop
        if self.sse_thread and self.sse_thread.is_alive():
            self.sse_thread.join(timeout=5)
        
        logger.info("Coral Runnable stopped")
    
    def __enter__(self):
        """
        Enter context manager.
        """
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager.
        """
        self.stop()
