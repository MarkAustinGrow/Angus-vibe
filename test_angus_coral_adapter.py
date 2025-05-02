#!/usr/bin/env python3
"""
Test script for the Angus Coral Adapter

This script tests the integration between Agent Angus and the Coral server
by connecting to the server, registering the agent, creating a thread with Yona,
and sending a test message.
"""
import time
import logging
from angus_coral_adapter import AngusCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to test the Angus Coral Adapter.
    """
    # Initialize the adapter with the Coral server URL and Angus's agent ID
    server_url = "http://coral.pushcollective.club:3001"
    agent_id = "did:web:angus.ai"
    
    logger.info(f"Initializing Angus Coral Adapter with agent_id: {agent_id}")
    adapter = AngusCoralAdapter(server_url, agent_id)
    
    # Connect to the Coral server
    logger.info("Connecting to Coral server...")
    if adapter.connect():
        logger.info("Successfully connected to Coral server")
        
        # Register Agent Angus with capabilities
        capabilities = [
            "music_analysis",
            "youtube_publishing",
            "comment_response"
        ]
        
        if adapter.register_with_capabilities(
            name="Agent Angus",
            description="A music analysis and YouTube publishing agent",
            capabilities=capabilities
        ):
            logger.info("Successfully registered Agent Angus with capabilities")
            
            # Create a thread with Yona
            logger.info("Creating a thread with Yona...")
            thread_id = adapter.create_thread_with_yona()
            
            if thread_id:
                logger.info(f"Successfully created thread with Yona: {thread_id}")
                
                # Send a test message to Yona
                test_message = "Hello Yona! This is Agent Angus. I'm now connected to the Coral server and ready to collaborate."
                
                if adapter.send_message_to_yona(thread_id, test_message):
                    logger.info("Successfully sent test message to Yona")
                    
                    # Process any responses for 30 seconds
                    logger.info("Waiting for responses from Yona...")
                    
                    # Define a custom message handler for thread messages
                    def handle_yona_message(data):
                        sender_id = data.get("sender_id")
                        content = data.get("content", "")
                        
                        if sender_id == "did:web:yona.ai":
                            logger.info(f"Received message from Yona: {content}")
                            
                            # Send a response back to Yona
                            response = f"Thanks for your message, Yona! This is an automated response from Agent Angus."
                            adapter.send_message_to_yona(thread_id, response)
                    
                    # Register the custom handler
                    adapter.register_message_handler("thread_message", handle_yona_message)
                    
                    # Process messages for 30 seconds
                    end_time = time.time() + 30
                    while time.time() < end_time:
                        adapter.process_messages(timeout=5)
                        time.sleep(1)
                    
                else:
                    logger.error("Failed to send test message to Yona")
            else:
                logger.error("Failed to create thread with Yona")
        else:
            logger.error("Failed to register Agent Angus")
    else:
        logger.error("Failed to connect to Coral server")
    
    logger.info("Test completed")

if __name__ == "__main__":
    main()
