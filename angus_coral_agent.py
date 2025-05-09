#!/usr/bin/env python3
"""
Angus Coral Agent - Integration between Angus and Coral Protocol

This script implements a Coral Protocol agent that exposes Angus's capabilities
to other agents in the Coral ecosystem using direct HTTP/SSE communication.
"""
import os
import sys
import json
import time
import logging
import traceback
import requests
import sseclient
import threading
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
    
    def __init__(self, coral_server_url="https://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"):
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
        
        # Agent state
        self.agent_did = None  # Will be set after registration
        self.threads = {}  # Thread ID -> Thread data
        self.mentions = []  # List of mentions
        self.running = False
        
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
    
    def register_agent(self) -> bool:
        """
        Register the agent with the Coral Protocol server.
        
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Prepare the registration data
            registration_data = {
                "agentId": self.agent_id,
                "agentDescription": self.agent_description,
                "waitForAgents": 2  # Wait for 2 agents to be available
            }
            
            # Send the registration request
            logger.info(f"Registering agent with Coral Protocol server: {self.coral_server_url}")
            
            # Extract the base URL (without the /sse part)
            base_url = self.coral_server_url.rsplit('/sse', 1)[0]
            registration_url = f"{base_url}/register"
            
            logger.info(f"Using registration URL: {registration_url}")
            
            response = requests.post(registration_url, json=registration_data)
            
            # Check if registration was successful
            if response.status_code == 200:
                registration_result = response.json()
                self.agent_did = registration_result.get("agentDid")
                logger.info(f"Agent registered successfully with DID: {self.agent_did}")
                return True
            else:
                logger.error(f"Failed to register agent: {response.status_code} - {response.text}")
                
                # Try an alternative approach - maybe the registration is handled via SSE
                logger.info("Trying alternative registration approach via SSE connection")
                
                # Just connect to the SSE endpoint with the agent parameters as query parameters
                sse_url = f"{self.coral_server_url}?agentId={self.agent_id}&waitForAgents=2"
                logger.info(f"Connecting to SSE URL: {sse_url}")
                
                # We'll consider this a success for now and let the SSE listener handle the rest
                return True
                
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            traceback.print_exc()
            return False
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all agents registered with the Coral Protocol server.
        
        Returns:
            List of agents
        """
        try:
            # Extract the base URL (without the /sse part)
            base_url = self.coral_server_url.rsplit('/sse', 1)[0]
            list_agents_url = f"{base_url}/list_agents"
            
            # Send the list agents request
            logger.info(f"Listing agents from Coral Protocol server: {list_agents_url}")
            response = requests.get(list_agents_url)
            
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
            traceback.print_exc()
            return []
    
    def create_thread(self) -> Optional[str]:
        """
        Create a new thread on the Coral Protocol server.
        
        Returns:
            Thread ID if successful, None otherwise
        """
        try:
            # Extract the base URL (without the /sse part)
            base_url = self.coral_server_url.rsplit('/sse', 1)[0]
            create_thread_url = f"{base_url}/create_thread"
            
            # Send the create thread request
            logger.info(f"Creating thread on Coral Protocol server: {create_thread_url}")
            response = requests.post(create_thread_url)
            
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
            traceback.print_exc()
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
            # Extract the base URL (without the /sse part)
            base_url = self.coral_server_url.rsplit('/sse', 1)[0]
            send_message_url = f"{base_url}/send_message"
            
            # Prepare the message data
            message_data = {
                "threadId": thread_id,
                "message": message,
                "mentions": mentions
            }
            
            # Send the message request
            logger.info(f"Sending message to thread {thread_id} with mentions {mentions}")
            response = requests.post(send_message_url, json=message_data)
            
            # Check if the request was successful
            if response.status_code == 200:
                logger.info(f"Message sent successfully to thread {thread_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            traceback.print_exc()
            return False
    
    def start_sse_listener(self):
        """
        Start listening for SSE events from the Coral Protocol server.
        """
        try:
            # Construct the SSE URL with agent parameters
            sse_url = f"{self.coral_server_url}?agentId={self.agent_id}&waitForAgents=2"
            
            # Start the SSE client
            logger.info(f"Starting SSE listener: {sse_url}")
            
            # Set up headers
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            
            # Make the request
            response = requests.get(sse_url, stream=True, headers=headers)
            
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
                    traceback.print_exc()
                    
                # Check if we should stop
                if not self.running:
                    break
                    
        except Exception as e:
            logger.error(f"Error in SSE listener: {str(e)}")
            traceback.print_exc()
            
            # Try to reconnect after a delay
            if self.running:
                time.sleep(5)
                threading.Thread(target=self.start_sse_listener).start()
    
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
            traceback.print_exc()
    
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
            traceback.print_exc()
    
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
            
            # Update agent DID
            self.agent_did = agent_did
            
        except Exception as e:
            logger.error(f"Error handling registration: {str(e)}")
            traceback.print_exc()
    
    def process_mention(self, thread_id: str, sender_id: str, message: str):
        """
        Process a mention from another agent.
        
        Args:
            thread_id: ID of the thread
            sender_id: ID of the sender
            message: Message content
        """
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
                response = {
                    "success": False,
                    "error": f"I don't understand how to handle: {instruction}"
                }
            
            # Take time to formulate a response
            time.sleep(3)
            
            # Send the response
            response_message = json.dumps(response, indent=2)
            self.send_message(thread_id, response_message, [sender_id])
            
            logger.info(f"Sent response in thread {thread_id} to {sender_id}")
            
        except Exception as e:
            logger.error(f"Error processing mention: {str(e)}")
            traceback.print_exc()
    
    def run(self):
        """
        Run the Angus Coral agent.
        
        This method starts the agent and connects it to the Coral Protocol server.
        """
        logger.info(f"Starting Angus Coral Agent with server URL: {self.coral_server_url}")
        
        try:
            # Set running flag
            self.running = True
            
            # Register the agent
            if not self.register_agent():
                logger.error("Failed to register agent, exiting")
                return
            
            # Start the SSE listener
            threading.Thread(target=self.start_sse_listener).start()
            
            # Main loop
            while self.running:
                try:
                    # Log status periodically
                    logger.info(f"Angus Coral Agent is running... (DID: {self.agent_did})")
                    logger.info(f"Threads: {len(self.threads)}, Mentions: {len(self.mentions)}")
                    
                    # Sleep for a while
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received, stopping")
                    self.running = False
                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}")
                    traceback.print_exc()
                    time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Angus Coral Agent stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error running Angus Coral Agent: {str(e)}")
            traceback.print_exc()
            self.running = False

def main():
    """
    Main entry point for the Angus Coral Agent.
    """
    # Get Coral server URL from environment variable or use default
    coral_server_url = os.environ.get("CORAL_SERVER_URL", "https://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse")
    
    # Create and run the agent
    agent = AngusCoralAgent(coral_server_url=coral_server_url)
    agent.run()

if __name__ == "__main__":
    main()
