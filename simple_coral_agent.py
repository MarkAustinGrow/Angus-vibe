import json
import uuid
import requests
import sseclient
import threading
import queue
import re
import time

# Configure basic logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCoralAgent:
    def __init__(self, server_url, agent_id):
        self.server_url = server_url
        self.agent_id = agent_id
        self.session_id = "session1"  # Default session ID
        self.sse_url = f"{server_url}/devmode/exampleApplication/privkey/{self.session_id}/sse?agentId={self.agent_id}"
        self.transport_session_id = None
        self.event_queue = queue.Queue()
        self.running = True
        
    def connect(self):
        """Connect to the Coral server via SSE."""
        logger.info(f"Connecting to Coral server at {self.sse_url}")
        
        # Start SSE connection in a separate thread
        def sse_worker():
            try:
                logger.info(f"Starting SSE connection to {self.sse_url}")
                response = requests.get(self.sse_url, stream=True)
                client = sseclient.SSEClient(response)
                
                for event in client.events():
                    if not self.running:
                        break
                        
                    logger.info(f"Received event: {event.event}, data: {event.data[:100]}...")
                    
                    # Special handling for the endpoint event which contains the session ID
                    if event.event == 'endpoint':
                        try:
                            # Extract the session ID from the URL
                            endpoint_url = event.data.strip()
                            session_id_match = re.search(r'sessionId=([^&]+)', endpoint_url)
                            if session_id_match:
                                self.transport_session_id = session_id_match.group(1)
                                logger.info(f"Extracted session ID: {self.transport_session_id}")
                        except Exception as e:
                            logger.error(f"Error processing endpoint event: {str(e)}")
                    elif event.event == 'message':
                        try:
                            data = json.loads(event.data)
                            self.event_queue.put(data)
                            logger.info(f"Added event to queue: {data}")
                        except Exception as e:
                            logger.error(f"Error processing message event: {str(e)}")
            except Exception as e:
                logger.error(f"Error in SSE connection: {str(e)}")
        
        # Start the SSE thread
        self.sse_thread = threading.Thread(target=sse_worker, daemon=True)
        self.sse_thread.start()
        
        # Wait for transport session ID
        timeout = 30  # seconds
        start_time = time.time()
        while not self.transport_session_id and time.time() - start_time < timeout:
            time.sleep(0.5)
            
        if not self.transport_session_id:
            logger.error("Failed to get transport session ID within timeout")
            return False
            
        logger.info(f"Successfully connected with session ID: {self.transport_session_id}")
        return True
        
    def register_agent(self, name, description):
        """Register the agent with the Coral server."""
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
                "capabilities": []
            }
        }
        
        logger.info(f"Registering agent {self.agent_id} with Coral server")
        logger.info(f"Sending registration message: {json.dumps(payload, indent=2)}")  # Added for debugging
        try:
            response = requests.post(message_url, json=payload)
            response_data = response.json()
            logger.info(f"Registration response: {response_data}")
            return True
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return False
            
    def create_thread(self, participants):
        """Create a new thread with the specified participants."""
        if not self.transport_session_id:
            logger.error("Not connected to server, cannot create thread")
            return None
            
        message_url = f"{self.server_url}/devmode/exampleApplication/privkey/{self.session_id}/message?sessionId={self.transport_session_id}"
        
        # Updated payload format to match what the Coral server expects
        payload = {
            "type": "tool_call",
            "tool": "create_thread",
            "arguments": {
                "participants": participants,
                "metadata": {}
            }
        }
        
        logger.info(f"Creating thread with participants: {participants}")
        logger.info(f"Sending create thread message: {json.dumps(payload, indent=2)}")  # Added for debugging
        try:
            response = requests.post(message_url, json=payload)
            response_data = response.json()
            logger.info(f"Create thread response: {response_data}")
            return response_data.get("thread_id")
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            return None
            
    def send_message(self, thread_id, content, mentions=[]):
        """Send a message to a thread."""
        if not self.transport_session_id:
            logger.error("Not connected to server, cannot send message")
            return False
            
        message_url = f"{self.server_url}/devmode/exampleApplication/privkey/{self.session_id}/message?sessionId={self.transport_session_id}"
        
        # Updated payload format to match what the Coral server expects
        payload = {
            "type": "tool_call",
            "tool": "send_message",
            "arguments": {
                "thread_id": thread_id,
                "sender_id": self.agent_id,
                "content": content,
                "mentions": mentions
            }
        }
        
        logger.info(f"Sending message to thread {thread_id}")
        logger.info(f"Sending message payload: {json.dumps(payload, indent=2)}")  # Added for debugging
        try:
            response = requests.post(message_url, json=payload)
            response_data = response.json()
            logger.info(f"Send message response: {response_data}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
            
    def process_messages(self, timeout=5):
        """Process any received messages for a specified time."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                data = self.event_queue.get(block=False)
                logger.info(f"Processing message: {data}")
                # Handle the message based on your requirements
                # For example, you might want to respond to certain messages
            except queue.Empty:
                time.sleep(0.1)
                continue
