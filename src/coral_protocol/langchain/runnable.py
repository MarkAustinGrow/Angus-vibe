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
        self.message_endpoint = None  # Endpoint for sending messages
        self.session_id = None  # Session ID for the current connection
        self.connected = False  # Whether we're currently connected to the SSE endpoint
        self.connection_attempts = 0  # Number of connection attempts
        self.last_event_time = 0  # Time of the last received event
        self.known_agents = []  # List of known agents
        
        logger.info(f"Initialized Coral Runnable with {len(functions)} functions")
    
    def register(self) -> bool:
        """
        Register the agent with the Coral Protocol server.
        
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Parse the server URL to extract components
            from urllib.parse import urlparse, urljoin
            
            # Print the server URL for debugging
            print(f"DEBUG: Server URL in runnable.py: {self.config.server_url}")
            
            # Extract the base URL (preserving the full path structure)
            parsed_url = urlparse(self.config.server_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
            registration_url = f"{base_url}/register"
            
            # Print the registration URL for debugging
            print(f"DEBUG: Registration URL: {registration_url}")
            
            # Prepare the registration data
            agent_id = self.config.did.split(':')[-1]  # Use the last part of the DID as the agent ID
            registration_data = {
                "agentId": agent_id,
                "agentDescription": self.config.capability_document.get("description", "Angus Agent"),
                "waitForAgents": 2  # Wait for 2 agents to be available
            }
            
            # Try direct registration first
            try:
                # Send the registration request
                logger.info(f"Attempting direct registration with Coral Protocol server: {registration_url}")
                
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
                    # Don't treat this as an error, just log it
                    logger.info(f"Direct registration returned {response.status_code}, falling back to SSE")
            except Exception as e:
                logger.info(f"Direct registration attempt failed: {str(e)}, falling back to SSE")
            
            # Fall back to SSE registration
            logger.info("Using SSE connection for registration")
            
            # Construct the SSE URL with agent parameters
            sse_url = f"{self.config.server_url}?agentId={agent_id}&waitForAgents=2"
            logger.info(f"Connecting to SSE URL: {sse_url}")
            
            # We'll consider this a success and let the SSE listener handle the rest
            self.registered = True
            return True
                
        except Exception as e:
            logger.error(f"Error in registration process: {str(e)}")
            return False
    
    def start_sse_listener(self):
        """
        Start listening for SSE events from the Coral Protocol server with robust reconnection.
        """
        max_retries = 5
        base_delay = 1  # Start with 1 second delay
        max_delay = 30  # Maximum delay of 30 seconds
        
        # Initialize connection state
        self.connected = False
        self.connection_attempts = 0
        self.last_event_time = time.time()
        
        # Start heartbeat thread
        self._start_heartbeat_thread()
        
        while self.running and self.connection_attempts < max_retries:
            try:
                # Construct the SSE URL with agent parameters
                agent_id = self.config.did.split(':')[-1]
                sse_url = f"{self.config.server_url}?agentId={agent_id}&waitForAgents=2"
                
                # Start the SSE client
                logger.info(f"Starting SSE listener (attempt {self.connection_attempts + 1}/{max_retries}): {sse_url}")
                
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
                    raise requests.exceptions.RequestException(f"Failed to connect to SSE: {response.status_code}")
                
                # Create the SSE client
                client = sseclient.SSEClient(response)
                
                # Reset connection state
                self.connected = True
                self.connection_attempts = 0
                
                # Process events
                for event in client.events():
                    # Update last event time
                    self.last_event_time = time.time()
                    
                    # Process the event
                    self._handle_sse_event(event)
                    
                    # Check if we should stop
                    if not self.running:
                        break
                
                # If we exit the loop, the connection was closed
                logger.warning("SSE event stream ended, will attempt reconnection")
                self.connected = False
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error connecting to SSE: {str(e)}")
                self.connected = False
            except Exception as e:
                logger.error(f"Unexpected error in SSE connection: {str(e)}")
                logger.exception("Full exception details:")
                self.connected = False
            
            # Only increment connection attempts if we're still running
            if self.running:
                self.connection_attempts += 1
                
                # Calculate delay with exponential backoff
                if self.connection_attempts < max_retries:
                    delay = min(base_delay * (2 ** (self.connection_attempts - 1)), max_delay)
                    logger.info(f"Reconnecting in {delay} seconds (attempt {self.connection_attempts}/{max_retries})...")
                    time.sleep(delay)
        
        if self.connection_attempts >= max_retries:
            logger.error(f"Failed to establish stable connection after {max_retries} attempts")
        
        self.connected = False
    
    def _start_heartbeat_thread(self):
        """Start a thread to monitor connection health."""
        def heartbeat_check():
            heartbeat_interval = 30  # Check every 30 seconds
            max_silence = 90  # Consider connection dead after 90 seconds of silence
            
            while self.running:
                time.sleep(heartbeat_interval)
                
                # Check if we've received an event recently
                if self.connected and time.time() - self.last_event_time > max_silence:
                    logger.warning(f"No events received for {max_silence} seconds, reconnecting...")
                    self.connected = False
                    
                    # Start a new SSE listener thread
                    if self.running:
                        new_thread = threading.Thread(target=self.start_sse_listener)
                        new_thread.daemon = True
                        new_thread.start()
                        break
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=heartbeat_check, daemon=True)
        heartbeat_thread.start()
    
    def _handle_sse_event(self, event):
        """
        Handle an SSE event with comprehensive type handling.
        
        Args:
            event: The SSE event to handle
        """
        try:
            # Log the raw event for debugging
            logger.debug(f"Raw SSE event: {event}")
            logger.debug(f"Event data: '{event.data}'")
            logger.debug(f"Event type: '{event.event}'")
            logger.info(f"Received SSE event: {event.event} - {event.data}")
            
            # Handle different event types
            if event.event == "endpoint":
                self._handle_endpoint_event(event.data)
            elif event.event == "message":
                self._handle_message_event(event.data)
            elif event.event == "agent_joined":
                self._handle_agent_joined_event(event.data)
            elif event.event == "agent_left":
                self._handle_agent_left_event(event.data)
            elif event.event == "error":
                self._handle_error_event(event.data)
            elif event.event == "heartbeat" or not event.event:
                # Just log heartbeats
                logger.debug("Received heartbeat event")
            else:
                # For unknown event types, try to handle based on the data
                self._handle_unknown_event(event)
                
        except Exception as e:
            logger.error(f"Error processing SSE event: {str(e)}")
            logger.exception("Full exception details:")
    
    def _handle_endpoint_event(self, data):
        """
        Handle an endpoint event.
        
        Args:
            data: The event data
        """
        logger.info(f"Received endpoint event: {data}")
        
        # Store the endpoint for future use
        self.message_endpoint = data
        
        # Extract session ID if present
        if "sessionId=" in data:
            self.session_id = data.split("sessionId=")[1].split("&")[0]
            logger.info(f"Extracted session ID: {self.session_id}")
    
    def _handle_message_event(self, data):
        """
        Handle a message event.
        
        Args:
            data: The event data
        """
        logger.info(f"Received message event")
        
        # Skip empty events
        if not data or data.isspace():
            logger.debug("Skipping empty message data")
            return
        
        try:
            # Try to parse as JSON
            message_data = json.loads(data)
            logger.info(f"Message content: {message_data}")
            
            # Process the message based on its type
            if "type" in message_data:
                event_type = message_data["type"]
                if event_type == "mention":
                    self.handle_mention(message_data)
                elif event_type == "thread_update":
                    self.handle_thread_update(message_data)
                elif event_type == "registration":
                    self.handle_registration(message_data)
                else:
                    logger.info(f"Received unknown message type: {event_type}")
        except json.JSONDecodeError as e:
            logger.warning(f"Message event data is not valid JSON: {str(e)}")
            logger.warning(f"Raw data: '{data}'")
            # Try to handle non-JSON message data
            logger.info(f"Received message event with non-JSON data: {data}")
    
    def _handle_agent_joined_event(self, data):
        """
        Handle an agent joined event.
        
        Args:
            data: The event data
        """
        logger.info(f"Agent joined: {data}")
        
        try:
            if data and not data.isspace():
                try:
                    agent_data = json.loads(data)
                    logger.info(f"Agent joined: {agent_data.get('name', 'Unknown')} ({agent_data.get('did', 'Unknown DID')})")
                    
                    # Add to known agents
                    self.known_agents.append(agent_data)
                except json.JSONDecodeError:
                    logger.warning(f"Agent joined event data is not valid JSON: {data}")
        except Exception as e:
            logger.error(f"Error handling agent joined event: {str(e)}")
    
    def _handle_agent_left_event(self, data):
        """
        Handle an agent left event.
        
        Args:
            data: The event data
        """
        logger.info(f"Agent left: {data}")
        
        try:
            if data and not data.isspace():
                try:
                    agent_data = json.loads(data)
                    agent_id = agent_data.get('did', agent_data.get('id', None))
                    logger.info(f"Agent left: {agent_data.get('name', 'Unknown')} ({agent_id})")
                    
                    # Remove from known agents
                    if agent_id:
                        self.known_agents = [a for a in self.known_agents if a.get('did', a.get('id', None)) != agent_id]
                except json.JSONDecodeError:
                    logger.warning(f"Agent left event data is not valid JSON: {data}")
        except Exception as e:
            logger.error(f"Error handling agent left event: {str(e)}")
    
    def _handle_error_event(self, data):
        """
        Handle an error event.
        
        Args:
            data: The event data
        """
        logger.error(f"Received error event: {data}")
    
    def _handle_unknown_event(self, event):
        """
        Handle an unknown event type.
        
        Args:
            event: The SSE event
        """
        logger.info(f"Received unknown event type: {event.event}")
        
        # Try to parse the data as JSON
        if event.data and not event.data.isspace():
            try:
                event_data = json.loads(event.data)
                event_type = event_data.get("type")
                
                # Handle based on the event data type
                if event_type == "mention":
                    self.handle_mention(event_data)
                elif event_type == "thread_update":
                    self.handle_thread_update(event_data)
                elif event_type == "registration":
                    self.handle_registration(event_data)
                else:
                    logger.info(f"Received unknown event data type: {event_type}")
            except json.JSONDecodeError:
                logger.warning(f"Unknown event data is not valid JSON: {event.data}")
    
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
            # Use the message endpoint if available
            if self.message_endpoint:
                # The message endpoint might be a relative URL
                from urllib.parse import urlparse, urljoin
                
                # Check if the endpoint is a relative URL
                parsed_endpoint = urlparse(self.message_endpoint)
                if not parsed_endpoint.netloc:
                    # It's a relative URL, so join it with the base URL
                    parsed_url = urlparse(self.config.server_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    send_message_url = urljoin(base_url, self.message_endpoint)
                else:
                    # It's an absolute URL
                    send_message_url = self.message_endpoint
            else:
                # Fall back to constructing the URL from the server URL
                from urllib.parse import urlparse, urljoin
                
                # Extract the base URL (preserving the full path structure)
                parsed_url = urlparse(self.config.server_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
                send_message_url = f"{base_url}/send_message"
            
            # Print the send message URL for debugging
            print(f"DEBUG: Send message URL: {send_message_url}")
            
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
            # Parse the server URL to extract components
            from urllib.parse import urlparse, urljoin
            
            # Extract the base URL (preserving the full path structure)
            parsed_url = urlparse(self.config.server_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
            create_thread_url = f"{base_url}/create_thread"
            
            # Print the create thread URL for debugging
            print(f"DEBUG: Create thread URL: {create_thread_url}")
            
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
            # Parse the server URL to extract components
            from urllib.parse import urlparse, urljoin
            
            # Extract the base URL (preserving the full path structure)
            parsed_url = urlparse(self.config.server_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
            list_agents_url = f"{base_url}/list_agents"
            
            # Print the list agents URL for debugging
            print(f"DEBUG: List agents URL: {list_agents_url}")
            
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
