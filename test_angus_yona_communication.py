#!/usr/bin/env python3
"""
Test script for Agent Angus communication with Agent Yona through the Coral Protocol.

This script tests the communication between Agent Angus and Agent Yona by:
1. Creating a thread with Yona
2. Sending a message to Yona
3. Waiting for and processing responses from Yona
"""
import logging
import time
import sys
import json
from angus_coral_adapter import AngusCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('angus_yona_test.log')
    ]
)
logger = logging.getLogger("angus_yona_test")

def test_yona_communication():
    """
    Test communication with Yona.
    """
    logger.info("Starting Angus-Yona communication test")
    
    # Create the adapter with a consistent session ID
    adapter = AngusCoralAdapter(session_id="angus-agent", use_devmode=True)
    
    # Register the agent
    agent_id = adapter.register_agent()
    if not agent_id:
        logger.error("Failed to register Agent Angus")
        return False
    
    logger.info(f"Agent Angus registered with ID: {agent_id}")
    
    # Create a thread with Yona
    thread_id = adapter.create_thread_with_yona(metadata={"topic": "Music Creation Test"})
    if not thread_id:
        logger.error("Failed to create thread with Yona")
        return False
    
    logger.info(f"Thread created with ID: {thread_id}")
    
    # Send a message to Yona requesting a song
    message = "Can you create a song about artificial intelligence and creativity?"
    message_id = adapter.send_message_to_yona(thread_id, message)
    if not message_id:
        logger.error("Failed to send message to Yona")
        return False
    
    logger.info(f"Message sent to Yona with ID: {message_id}")
    
    # Define a message handler to process responses from Yona
    received_response = [False]  # Use a list to allow modification in the nested function
    
    def handle_message(data):
        sender_id = data.get('sender_id')
        content = data.get('content', '')
        msg_thread_id = data.get('thread_id')
        
        logger.info(f"Received message from {sender_id} in thread {msg_thread_id}")
        
        # Check if the message is from Yona and in our thread
        if sender_id == adapter.yona_agent_id and msg_thread_id == thread_id:
            logger.info(f"Message from Yona: {content[:100]}...")
            
            # Check if Yona created a song
            if "Created song" in content:
                logger.info("Yona created a song!")
                received_response[0] = True
                
                # Extract song information
                lines = content.split('\n')
                song_info = {
                    "title": lines[0].replace("Created song '", "").replace("'", ""),
                    "audio_url": next((line.replace("Audio: ", "") for line in lines if line.startswith("Audio: ")), None),
                    "lyrics": '\n'.join(lines[3:]) if len(lines) > 3 else ""
                }
                
                logger.info(f"Song information: {json.dumps(song_info, indent=2)}")
                
                # Send a thank you message
                thank_you = f"Thanks for creating '{song_info['title']}'! It sounds great!"
                adapter.send_message_to_yona(thread_id, thank_you)
    
    # Start listening for events
    adapter.coral_client.start_listening({
        "message": handle_message
    })
    
    logger.info("Listening for responses from Yona")
    
    # Wait for a response from Yona (with timeout)
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while not received_response[0] and time.time() - start_time < timeout:
        # Process mentions to keep the connection alive
        adapter.process_mentions(timeout_seconds=10)
        time.sleep(1)
        
        # Log progress every 30 seconds
        elapsed = time.time() - start_time
        if elapsed % 30 < 1:
            logger.info(f"Waiting for response from Yona... ({int(elapsed)}s elapsed)")
    
    if received_response[0]:
        logger.info("Test successful! Received response from Yona.")
        return True
    else:
        logger.error(f"Test failed. No response received from Yona within {timeout} seconds.")
        return False

def main():
    """
    Main entry point.
    """
    try:
        success = test_yona_communication()
        if success:
            logger.info("Angus-Yona communication test completed successfully!")
            return 0
        else:
            logger.error("Angus-Yona communication test failed.")
            return 1
    except Exception as e:
        logger.exception(f"Error during test: {str(e)}")
        return 1
    finally:
        logger.info("Test completed.")

if __name__ == "__main__":
    sys.exit(main())
