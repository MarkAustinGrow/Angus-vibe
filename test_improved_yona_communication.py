#!/usr/bin/env python3
"""
Test script for the improved Angus-Yona communication through the Coral Protocol.

This script tests the enhanced communication between Agent Angus and Agent Yona by:
1. Creating a thread with Yona using the improved thread creation
2. Sending a message to Yona with enhanced message delivery verification
3. Waiting for and processing responses from Yona using direct message checking
"""
import logging
import time
import sys
import json
import argparse
from angus_coral_adapter_improved import AngusCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('improved_yona_test.log')
    ]
)
logger = logging.getLogger("improved_yona_test")

def test_yona_communication(message=None, timeout=300, verify_delivery=True):
    """
    Test improved communication with Yona.
    
    Args:
        message (str, optional): Custom message to send to Yona. Defaults to a song request.
        timeout (int, optional): Maximum time to wait for a response in seconds. Defaults to 300.
        verify_delivery (bool, optional): Whether to verify message delivery. Defaults to True.
        
    Returns:
        bool: True if the test was successful, False otherwise
    """
    logger.info("Starting Improved Angus-Yona communication test")
    
    # Create the adapter with a consistent session ID
    adapter = AngusCoralAdapter(session_id="angus-agent", use_devmode=True)
    
    # Register the agent
    agent_id = adapter.register_agent()
    if not agent_id:
        logger.error("Failed to register Agent Angus")
        return False
    
    logger.info(f"Agent Angus registered with ID: {agent_id}")
    
    # Create a thread with Yona using the improved thread creation
    thread_id = adapter.create_thread_with_yona(
        metadata={"topic": "Music Creation Test", "test_id": "improved_test"},
        wait_for_real_id=True,
        timeout=60
    )
    if not thread_id:
        logger.error("Failed to create thread with Yona")
        return False
    
    logger.info(f"Thread created with ID: {thread_id}")
    
    # Send a message to Yona requesting a song
    if not message:
        message = "Can you create a song about artificial intelligence and creativity? I'd like something upbeat and inspiring."
    
    message_id = adapter.send_message_to_yona(
        thread_id=thread_id,
        content=message,
        verify_delivery=verify_delivery,
        timeout=30
    )
    if not message_id:
        logger.error("Failed to send message to Yona")
        return False
    
    logger.info(f"Message sent to Yona with ID: {message_id}")
    
    # Define a message handler to process responses from Yona
    received_response = [False]  # Use a list to allow modification in the nested function
    song_info = [None]  # Store song information
    
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
                song_data = {
                    "title": lines[0].replace("Created song '", "").replace("'", ""),
                    "audio_url": next((line.replace("Audio: ", "") for line in lines if line.startswith("Audio: ")), None),
                    "lyrics": '\n'.join(lines[3:]) if len(lines) > 3 else ""
                }
                
                song_info[0] = song_data
                logger.info(f"Song information: {json.dumps(song_data, indent=2)}")
                
                # Send a thank you message
                thank_you = f"Thanks for creating '{song_data['title']}'! It sounds great!"
                adapter.send_message_to_yona(thread_id, thank_you)
    
    # Start listening for events
    adapter.coral_client.start_listening({
        "message": handle_message
    })
    
    logger.info("Listening for responses from Yona")
    
    # Wait for a response from Yona (with timeout)
    start_time = time.time()
    
    while not received_response[0] and time.time() - start_time < timeout:
        # Process mentions to keep the connection alive
        adapter.process_mentions(timeout_seconds=10)
        
        # If we haven't received a response yet, check for messages directly
        if not received_response[0]:
            # Check for messages from Yona in this thread
            yona_messages = adapter.check_for_yona_messages(thread_id=thread_id)
            
            for msg in yona_messages:
                content = msg.get("content", "")
                
                # Check if Yona created a song
                if "Created song" in content:
                    logger.info("Found song creation message through direct checking!")
                    received_response[0] = True
                    
                    # Extract song information
                    lines = content.split('\n')
                    song_data = {
                        "title": lines[0].replace("Created song '", "").replace("'", ""),
                        "audio_url": next((line.replace("Audio: ", "") for line in lines if line.startswith("Audio: ")), None),
                        "lyrics": '\n'.join(lines[3:]) if len(lines) > 3 else ""
                    }
                    
                    song_info[0] = song_data
                    logger.info(f"Song information: {json.dumps(song_data, indent=2)}")
                    
                    # Send a thank you message
                    thank_you = f"Thanks for creating '{song_data['title']}'! It sounds great!"
                    adapter.send_message_to_yona(thread_id, thank_you)
                    break
        
        time.sleep(1)
        
        # Log progress every 30 seconds
        elapsed = time.time() - start_time
        if elapsed % 30 < 1:
            logger.info(f"Waiting for response from Yona... ({int(elapsed)}s elapsed)")
    
    if received_response[0]:
        logger.info("Test successful! Received response from Yona.")
        if song_info[0]:
            logger.info(f"Song title: {song_info[0]['title']}")
            if song_info[0]['audio_url']:
                logger.info(f"Audio URL: {song_info[0]['audio_url']}")
        return True
    else:
        logger.error(f"Test failed. No response received from Yona within {timeout} seconds.")
        return False

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description='Test improved Angus-Yona communication')
    parser.add_argument('--message', type=str, help='Custom message to send to Yona')
    parser.add_argument('--timeout', type=int, default=300, help='Maximum time to wait for a response in seconds')
    parser.add_argument('--no-verify', action='store_true', help='Disable message delivery verification')
    
    args = parser.parse_args()
    
    try:
        success = test_yona_communication(
            message=args.message,
            timeout=args.timeout,
            verify_delivery=not args.no_verify
        )
        if success:
            logger.info("Improved Angus-Yona communication test completed successfully!")
            return 0
        else:
            logger.error("Improved Angus-Yona communication test failed.")
            return 1
    except Exception as e:
        logger.exception(f"Error during test: {str(e)}")
        return 1
    finally:
        logger.info("Test completed.")

if __name__ == "__main__":
    sys.exit(main())
