#!/usr/bin/env python3
"""
Run script for Agent Angus with Coral Protocol integration

This script initializes Agent Angus with the Coral Protocol adapter,
connects to the Coral server, and runs the agent with both its standard
functionality and Coral communication capabilities.
"""
import os
import sys
import time
import logging
import argparse
import threading
from typing import Dict, Any

# Import Agent Angus and the Coral adapter
from angus import AgentAngus
from angus_coral_adapter import AngusCoralAdapter

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

class AngusWithCoral:
    """
    Wrapper class that integrates Agent Angus with the Coral Protocol.
    """
    
    def __init__(self, coral_server_url=None, agent_id=None):
        """
        Initialize Agent Angus with Coral Protocol integration.
        
        Args:
            coral_server_url: URL of the Coral server (default: from environment variable)
            agent_id: Agent ID for Coral (default: from environment variable)
        """
        # Initialize Agent Angus
        self.angus = AgentAngus()
        
        # Get Coral server URL from environment variable or parameter
        self.coral_server_url = coral_server_url or os.environ.get("CORAL_SERVER_URL", "http://coral.pushcollective.club:3001")
        
        # Get agent ID from environment variable or parameter
        self.agent_id = agent_id or os.environ.get("AGENT_ID", "did:web:angus.ai")
        
        # Initialize the Coral adapter
        self.coral_adapter = AngusCoralAdapter(self.coral_server_url, self.agent_id)
        
        # Flag to track if Coral is connected
        self.coral_connected = False
        
        logger.info(f"Initialized AngusWithCoral - Coral server: {self.coral_server_url}, Agent ID: {self.agent_id}")
    
    def connect_to_coral(self):
        """
        Connect to the Coral server and register Agent Angus.
        
        Returns:
            True if connection and registration were successful, False otherwise
        """
        logger.info("Connecting to Coral server...")
        
        try:
            # Connect to the Coral server
            if self.coral_adapter.connect():
                logger.info("Successfully connected to Coral server")
                
                # Register Agent Angus with capabilities
                capabilities = [
                    "music_analysis",
                    "youtube_publishing",
                    "comment_response"
                ]
                
                if self.coral_adapter.register_with_capabilities(
                    name="Agent Angus",
                    description="A music analysis and YouTube publishing agent",
                    capabilities=capabilities
                ):
                    logger.info("Successfully registered Agent Angus with capabilities")
                    self.coral_connected = True
                    return True
                else:
                    logger.error("Failed to register Agent Angus with Coral server")
            else:
                logger.error("Failed to connect to Coral server")
        except Exception as e:
            logger.error(f"Error connecting to Coral server: {str(e)}")
        
        return False
    
    def handle_yona_message(self, data):
        """
        Handle a message from Yona.
        
        Args:
            data: Message data
        """
        sender_id = data.get("sender_id")
        content = data.get("content", "")
        thread_id = data.get("thread_id")
        
        if sender_id == "did:web:yona.ai" and thread_id:
            logger.info(f"Received message from Yona: {content[:50]}...")
            
            # Process the message and generate a response
            # This is where you would integrate with Angus's functionality
            response = f"Thank you for your message, Yona. Agent Angus is processing your request."
            
            # Send the response back to Yona
            self.coral_adapter.send_message_to_yona(thread_id, response)
            logger.info(f"Sent response to Yona in thread {thread_id}")
    
    def run_coral_message_loop(self):
        """
        Run the Coral message processing loop in a separate thread.
        """
        if not self.coral_connected:
            logger.error("Cannot run message loop - not connected to Coral server")
            return
        
        # Register message handlers
        self.coral_adapter.register_message_handler("thread_message", self.handle_yona_message)
        
        # Start the message loop in a separate thread
        self.coral_thread = threading.Thread(target=self.coral_adapter.run_message_loop, daemon=True)
        self.coral_thread.start()
        
        logger.info("Started Coral message processing loop")
    
    def run(self, daemon=False, web=False, port=5000):
        """
        Run Agent Angus with Coral integration.
        
        Args:
            daemon: Whether to run in daemon mode with scheduled tasks
            web: Whether to run the web UI
            port: Port for the web UI
        """
        # Connect to Coral server
        if not self.connect_to_coral():
            logger.warning("Continuing without Coral integration")
        else:
            # Start the Coral message loop
            self.run_coral_message_loop()
        
        # Run Agent Angus
        if daemon:
            logger.info("Running Agent Angus in daemon mode with Coral integration")
            self.angus.run_scheduled_tasks()
        elif web:
            logger.info(f"Running Agent Angus web UI on port {port} with Coral integration")
            from web_ui import run_web_ui
            run_web_ui(port=port, debug=True)
        else:
            logger.info("Running Agent Angus with Coral integration")
            # Run a simple loop to keep the program alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down Agent Angus with Coral integration")
                self.coral_adapter.running = False

def main():
    """
    Main entry point for running Agent Angus with Coral integration.
    """
    parser = argparse.ArgumentParser(description='Agent Angus with Coral Protocol Integration')
    parser.add_argument('--server-url', type=str, help='URL of the Coral server')
    parser.add_argument('--agent-id', type=str, help='Agent ID for Coral')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode with scheduled tasks')
    parser.add_argument('--web', action='store_true', help='Run the web UI')
    parser.add_argument('--port', type=int, default=5000, help='Port for the web UI (default: 5000)')
    
    args = parser.parse_args()
    
    # Initialize and run Agent Angus with Coral integration
    angus_coral = AngusWithCoral(
        coral_server_url=args.server_url,
        agent_id=args.agent_id
    )
    
    angus_coral.run(
        daemon=args.daemon,
        web=args.web,
        port=args.port
    )

if __name__ == "__main__":
    main()
