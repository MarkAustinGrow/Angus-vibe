#!/usr/bin/env python3
"""
Test script for Angus-Yona communication via Coral Protocol.

This script tests the communication between Agent Angus and Yona using the Coral Protocol.
It performs three tests:
1. Create a thread and send a simple message
2. Test Yona's music capabilities
3. Test feedback processing
"""
import time
import logging
import json
import argparse
from angus_coral_adapter import AngusCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test Angus-Yona communication via Coral Protocol')
    parser.add_argument('--server', default='http://coral.pushcollective.club:3001', help='Coral server URL')
    parser.add_argument('--agent-id', default='did:web:angus.ai', help='Agent Angus ID')
    parser.add_argument('--yona-id', default='did:web:yona.ai', help='Yona agent ID')
    parser.add_argument('--session', default='session1', help='Session ID')
    parser.add_argument('--wait-time', type=int, default=60, help='Time to wait for responses (seconds)')
    args = parser.parse_args()
    
    # Initialize the Angus Coral Adapter
    logger.info(f"Initializing AngusCoralAdapter with server: {args.server}, agent_id: {args.agent_id}")
    angus_agent = AngusCoralAdapter(
        server_url=args.server,
        agent_id=args.agent_id,
        session_id=args.session
    )
    
    # Connect to the Coral server
    logger.info("Connecting to Coral server...")
    if not angus_agent.connect():
        logger.error("Failed to connect to Coral server")
        return
    
    logger.info("Successfully connected to Coral server")
    
    # Register Agent Angus with capabilities
    logger.info("Registering Agent Angus with capabilities...")
    if not angus_agent.register_with_capabilities(
        name="Agent Angus",
        description="A music analysis and YouTube publishing agent",
        capabilities=["music_analysis", "youtube_publishing", "comment_response"]
    ):
        logger.error("Failed to register Agent Angus")
        return
    
    logger.info("Successfully registered Agent Angus")
    
    # Register a message handler to log incoming messages
    def message_handler(data):
        logger.info(f"Received message: {json.dumps(data, indent=2)}")
    
    angus_agent.register_message_handler("thread_message", message_handler)
    
    # Test 1: Create a thread with Yona and send a simple message
    logger.info("Test 1: Creating thread with Yona...")
    thread_id = angus_agent.create_thread_with_yona()
    if not thread_id:
        logger.error("Failed to create thread with Yona")
        return
    
    logger.info(f"Created thread with ID: {thread_id}")
    
    # Send initial message
    logger.info("Sending initial message to Yona...")
    if not angus_agent.send_message_to_yona(
        thread_id=thread_id,
        content="Hello Yona, this is Agent Angus. Can you help me with music creation?"
    ):
        logger.error("Failed to send initial message")
        return
    
    logger.info("Successfully sent initial message to Yona")
    
    # Wait for response
    logger.info("Waiting for response (10 seconds)...")
    time.sleep(10)  # Wait for Yona to process and respond
    
    # Process any incoming messages
    logger.info("Processing incoming messages...")
    angus_agent.process_messages(timeout=5)
    
    # Test 2: Test Yona's music capabilities
    logger.info("Test 2: Testing Yona's music capabilities...")
    if not angus_agent.send_message_to_yona(
        thread_id=thread_id,
        content="Yona, can you create a K-pop song about skateboarding?"
    ):
        logger.error("Failed to send music request")
        return
    
    logger.info("Successfully sent music request to Yona")
    
    # Wait for response
    logger.info("Waiting for response (15 seconds)...")
    time.sleep(15)  # Wait longer for music creation request
    
    # Process any incoming messages
    logger.info("Processing incoming messages...")
    angus_agent.process_messages(timeout=5)
    
    # Test 3: Test feedback processing
    logger.info("Test 3: Testing feedback processing...")
    if not angus_agent.send_message_to_yona(
        thread_id=thread_id,
        content="I listened to the skateboarding song. The beat is great, but could you make the chorus more energetic?"
    ):
        logger.error("Failed to send feedback")
        return
    
    logger.info("Successfully sent feedback to Yona")
    
    # Process messages for a while to see responses
    logger.info(f"Processing messages for {args.wait_time} seconds...")
    end_time = time.time() + args.wait_time
    while time.time() < end_time:
        angus_agent.process_messages(timeout=5)
        time.sleep(1)
        logger.info(f"Time remaining: {int(end_time - time.time())} seconds")
    
    logger.info("Tests completed successfully")

if __name__ == "__main__":
    main()
