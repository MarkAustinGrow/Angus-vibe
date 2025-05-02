#!/usr/bin/env python3
"""
Angus Coral Adapter - Integration between Agent Angus and the Coral Protocol

This module provides an adapter that allows Agent Angus to connect to the Coral server
and communicate with other agents like Yona.
"""
import json
import uuid
import time
import logging
import threading
import queue
from typing import Dict, Any, List, Optional

# Import the SimpleCoralAgent as the base class
from simple_coral_agent import SimpleCoralAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AngusCoralAdapter(SimpleCoralAgent):
    """
    Adapter class that extends SimpleCoralAgent to integrate Agent Angus with the Coral server.
    """
    
    def __init__(self, server_url: str, agent_id: str = "did:web:angus.ai", session_id: str = "session1"):
        """
        Initialize the Angus Coral Adapter.
        
        Args:
            server_url: URL of the Coral server
            agent_id: Unique identifier for Agent Angus (default: did:web:angus.ai)
            session_id: Session ID for the Coral server (default: session1)
        """
        super().__init__(server_url, agent_id)
        self.session_id = session_id
        self.sse_url = f"{server_url}/devmode/exampleApplication/privkey/{self.session_id}/sse?agentId={self.agent_id}"
        self.message_handlers = {}
        self.active_threads = {}
        logger.info(f"Initialized AngusCoralAdapter with agent_id: {agent_id}")
    
    def register_with_capabilities(self, name: str, description: str, capabilities: List[str]) -> bool:
        """
        Register Agent Angus with specific capabilities.
        
        Args:
            name: Name of the agent
            description: Description of the agent
            capabilities: List of capabilities the agent has
            
        Returns:
            True if registration was successful, False otherwise
        """
        if not self.transport_session_id:
            logger.error("Not connected to server, cannot register")
            return False
            
        message_url = f"{self.server_url}/devmode/exampleApplication/privkey/{self.session_id}/message?sessionId={self.transport_session_id}"
        
        # Updated payload format to match what the Coral server expects
        payload = {
            "type": "tool_call",
            "tool": "register_agent",
            "arguments": {
                "agent_id": self.agent_id,
                "name": name,
                "description": description,
                "capabilities": capabilities
            }
        }
        
        logger.info(f"Registering agent {self.agent_id} with capabilities: {capabilities}")
        logger.info(f"Sending registration message: {json.dumps(payload, indent=2)}")  # Added for debugging
        try:
            response = self.send_message_to_server(message_url, payload)
            logger.info(f"Registration response: {response}")
            return True
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return False
    
    def send_message_to_server(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to the Coral server.
        
        Args:
            url: URL to send the message to
            payload: Message payload
            
        Returns:
            Server response as a dictionary
            
        Raises:
            Exception: If there's an error sending the message
        """
        import requests
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message to server: {str(e)}")
            raise
    
    def register_message_handler(self, handler_type: str, handler_func):
        """
        Register a function to handle messages of a specific type.
        
        Args:
            handler_type: Type of message to handle
            handler_func: Function to call when a message of this type is received
        """
        self.message_handlers[handler_type] = handler_func
        logger.info(f"Registered handler for message type: {handler_type}")
    
    def process_messages(self, timeout=5):
        """
        Process incoming messages from the Coral server.
        
        Args:
            timeout: Maximum time to wait for messages (in seconds)
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                data = self.event_queue.get(block=False)
                logger.info(f"Received message: {data}")
                
                # Extract message type and content
                message_type = data.get("type", "unknown")
                
                # Call the appropriate handler if registered
                if message_type in self.message_handlers:
                    try:
                        self.message_handlers[message_type](data)
                    except Exception as e:
                        logger.error(f"Error in message handler for {message_type}: {str(e)}")
                else:
                    # Default handling based on message type
                    if message_type == "thread_message":
                        self.handle_thread_message(data)
                    elif message_type == "thread_created":
                        self.handle_thread_created(data)
                    else:
                        logger.info(f"No handler for message type: {message_type}")
                
            except queue.Empty:
                time.sleep(0.1)
                continue
    
    def handle_thread_message(self, data: Dict[str, Any]):
        """
        Handle a message received in a thread.
        
        Args:
            data: Message data
        """
        thread_id = data.get("thread_id")
        sender_id = data.get("sender_id")
        content = data.get("content", "")
        
        logger.info(f"Thread message from {sender_id} in thread {thread_id}: {content[:50]}...")
        
        # Store the thread ID if it's not already in active_threads
        if thread_id and thread_id not in self.active_threads:
            self.active_threads[thread_id] = {
                "last_message": time.time(),
                "participants": data.get("participants", [])
            }
    
    def handle_thread_created(self, data: Dict[str, Any]):
        """
        Handle a thread creation notification.
        
        Args:
            data: Thread creation data
        """
        thread_id = data.get("thread_id")
        participants = data.get("participants", [])
        
        logger.info(f"Thread created: {thread_id} with participants: {participants}")
        
        # Store the thread information
        if thread_id:
            self.active_threads[thread_id] = {
                "created_at": time.time(),
                "participants": participants
            }
    
    def create_thread_with_yona(self) -> Optional[str]:
        """
        Create a thread with the Yona agent.
        
        Returns:
            Thread ID if successful, None otherwise
        """
        return self.create_thread(["did:web:yona.ai", self.agent_id])
    
    def send_message_to_yona(self, thread_id: str, content: str) -> bool:
        """
        Send a message to the Yona agent in a specific thread.
        
        Args:
            thread_id: ID of the thread to send the message to
            content: Message content
            
        Returns:
            True if the message was sent successfully, False otherwise
        """
        return self.send_message(thread_id, content, mentions=["did:web:yona.ai"])
    
    def run_message_loop(self, check_interval=1):
        """
        Run a continuous message processing loop.
        
        Args:
            check_interval: Time between message checks (in seconds)
        """
        logger.info("Starting message processing loop")
        
        try:
            while self.running:
                self.process_messages(timeout=5)
                time.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("Message loop interrupted by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error in message loop: {str(e)}")
            self.running = False
