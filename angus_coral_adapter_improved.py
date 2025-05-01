#!/usr/bin/env python3
"""
Agent Angus Coral Protocol Adapter (Improved Version)

This module provides an adapter to integrate Agent Angus with the Coral Protocol server,
allowing all of Agent Angus's functionality to be accessible through the Coral Protocol.

This improved version includes:
- Better thread creation with polling for real thread IDs
- Enhanced message sending with verification
- Direct message checking as a fallback for wait_for_mentions
- Improved error handling and logging
"""
import os
import sys
import time
import logging
import json
import re
import threading
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple

# Import Coral client
from coral_client import CoralClient

# Import Agent Angus
from angus import AgentAngus

# Import OpenAI utilities
from openai_utils import analyze_music, generate_response

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

class AngusCoralAdapter:
    """
    Adapter to integrate Agent Angus with the Coral Protocol server.
    """
    
    def __init__(self, session_id="angus-agent", server_url="https://coral.pushcollective.club", use_devmode=True):
        """
        Initialize the Angus Coral Adapter.
        
        Args:
            session_id (str, optional): Unique session identifier. Defaults to "angus-agent".
            server_url (str, optional): Base URL of the Coral server. Defaults to "https://coral.pushcollective.club".
            use_devmode (bool, optional): Whether to use DevMode endpoints. Defaults to True.
        """
        # Initialize Agent Angus
        self.angus = AgentAngus()
        
        # Initialize Coral client with a consistent session ID
        self.coral_client = CoralClient(
            session_id=session_id,
            server_url=server_url,
            use_devmode=use_devmode
        )
        
        self.agent_id = None
        self.logger = logging.getLogger("angus_coral_adapter")
        self.threads = {}  # Store thread information
        self.messages = {}  # Store message information
        self.yona_agent_id = "yona-agent"  # Yona's fixed agent ID
        
        self.logger.info(f"Angus Coral Adapter initialized with session ID: {session_id}")
    
    def register_agent(self, max_retries=3, retry_delay=5):
        """
        Register Agent Angus with the Coral server.
        
        Args:
            max_retries (int, optional): Maximum number of registration attempts. Defaults to 3.
            retry_delay (int, optional): Delay between retries in seconds. Defaults to 5.
            
        Returns:
            str: The agent ID assigned by the server, or None if registration failed.
        """
        self.logger.info("Registering Agent Angus with Coral server")
        
        for attempt in range(max_retries):
            try:
                self.agent_id = self.coral_client.register_agent(
                    name="Agent Angus",
                    description="An AI agent that automates YouTube publishing and audience feedback collection for AI-generated music videos."
                )
                
                if self.agent_id and self.agent_id != "pending":
                    self.logger.info(f"Agent Angus registered with ID: {self.agent_id}")
                    return self.agent_id
                elif self.agent_id == "pending":
                    self.logger.info("Agent registration pending, waiting for confirmation...")
                    # Wait for real agent ID through event handling
                    # The event handler in main() will update self.agent_id when registration is confirmed
                    time.sleep(retry_delay)
                else:
                    self.logger.warning(f"Registration attempt {attempt+1}/{max_retries} failed, retrying...")
                    time.sleep(retry_delay)
            except Exception as e:
                self.logger.error(f"Error during registration attempt {attempt+1}/{max_retries}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        self.logger.error(f"Failed to register Agent Angus after {max_retries} attempts")
        return None
    
    def wait_for_real_thread_id(self, pending_id, timeout=60, poll_interval=2):
        """
        Wait for a real thread ID to be assigned.
        
        Args:
            pending_id (str): The pending thread ID
            timeout (int, optional): Maximum time to wait in seconds. Defaults to 60.
            poll_interval (int, optional): Time between polls in seconds. Defaults to 2.
            
        Returns:
            str: The real thread ID, or None if timeout is reached
        """
        self.logger.info(f"Waiting for real thread ID for pending ID: {pending_id}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if we've received a real thread ID through event handling
            if pending_id in self.threads and "real_id" in self.threads[pending_id]:
                real_id = self.threads[pending_id]["real_id"]
                self.logger.info(f"Real thread ID received: {real_id}")
                return real_id
            
            # Try listing threads to see if we can find our thread
            # This is a fallback mechanism and might not be supported by the Coral server
            try:
                threads = self.coral_client._send_tool_call("list_threads", {})
                if threads and "result" in threads and "threads" in threads["result"]:
                    for thread in threads["result"]["threads"]:
                        # Look for a thread that matches our criteria (has both agents as participants)
                        if (self.agent_id in thread.get("participants", []) and 
                            self.yona_agent_id in thread.get("participants", [])):
                            thread_id = thread.get("thread_id")
                            self.logger.info(f"Found matching thread with ID: {thread_id}")
                            # Update our threads dictionary
                            self.threads[pending_id]["real_id"] = thread_id
                            return thread_id
            except Exception as e:
                self.logger.debug(f"Error listing threads: {str(e)}")
            
            time.sleep(poll_interval)
            self.logger.debug(f"Still waiting for real thread ID... ({int(time.time() - start_time)}s elapsed)")
        
        self.logger.warning(f"Timeout waiting for real thread ID after {timeout}s")
        return None
    
    def create_thread_with_yona(self, metadata=None, wait_for_real_id=True, timeout=60):
        """
        Create a thread with Yona.
        
        Args:
            metadata (dict, optional): Additional metadata for the thread. Defaults to None.
            wait_for_real_id (bool, optional): Whether to wait for a real thread ID. Defaults to True.
            timeout (int, optional): Maximum time to wait for a real thread ID in seconds. Defaults to 60.
            
        Returns:
            str: The thread ID assigned by the server, or None if thread creation failed.
        """
        self.logger.info("Creating thread with Yona")
        
        if not self.agent_id:
            self.logger.error("Cannot create thread: Agent not registered")
            return None
        
        # Generate a request ID to track this thread creation
        request_id = str(uuid.uuid4())
        
        # Create a thread with both Angus and Yona
        thread_id = self.coral_client.create_thread(
            participants=[self.agent_id, self.yona_agent_id],
            metadata=metadata or {"topic": "Music Creation", "request_id": request_id}
        )
        
        if not thread_id:
            self.logger.error("Failed to create thread with Yona")
            return None
            
        self.logger.info(f"Thread creation request accepted, initial ID: {thread_id}")
        
        # Store thread information
        self.threads[thread_id] = {
            "created_at": time.time(),
            "participants": [self.agent_id, self.yona_agent_id],
            "metadata": metadata or {"topic": "Music Creation"},
            "request_id": request_id,
            "messages": []
        }
        
        # If the thread ID is "pending" and wait_for_real_id is True, wait for a real ID
        if thread_id == "pending" and wait_for_real_id:
            real_id = self.wait_for_real_thread_id(thread_id, timeout=timeout)
            if real_id:
                # Update our threads dictionary
                self.threads[real_id] = self.threads[thread_id]
                self.threads[real_id]["real_id"] = real_id
                # Keep a reference from pending ID to real ID
                self.threads[thread_id]["real_id"] = real_id
                thread_id = real_id
        
        self.logger.info(f"Thread created with final ID: {thread_id}")
        return thread_id
    
    def get_real_thread_id(self, thread_id):
        """
        Get the real thread ID for a given thread ID.
        
        Args:
            thread_id (str): The thread ID to check
            
        Returns:
            str: The real thread ID, or the original ID if it's already real
        """
        if thread_id in self.threads and "real_id" in self.threads[thread_id]:
            return self.threads[thread_id]["real_id"]
        return thread_id
    
    def send_message_to_yona(self, thread_id, content, verify_delivery=True, timeout=30):
        """
        Send a message to Yona using multiple mention formats for maximum reliability.
        
        Args:
            thread_id (str): The ID of the thread to send the message to
            content (str): The content of the message
            verify_delivery (bool, optional): Whether to verify message delivery. Defaults to True.
            timeout (int, optional): Maximum time to wait for delivery verification in seconds. Defaults to 30.
            
        Returns:
            str: The message ID assigned by the server, or None if sending failed
        """
        # Get the real thread ID if available
        real_thread_id = self.get_real_thread_id(thread_id)
        self.logger.info(f"Sending message to Yona in thread {real_thread_id}")
        
        # Generate a unique message identifier to include in the content
        message_uuid = str(uuid.uuid4())[:8]
        
        # Ensure the content includes @mention format if not already present
        if not f"@{self.yona_agent_id}" in content:
            content = f"@{self.yona_agent_id} {content}"
        
        # Add a hidden message ID for verification
        content += f"\n<!-- message-id: {message_uuid} -->"
        
        # Send the message with explicit mention in the API call
        message_id = self.coral_client.send_message(
            thread_id=real_thread_id,
            content=content,
            mentions=[self.yona_agent_id]  # Explicit mention in the API call
        )
        
        if not message_id:
            self.logger.error("Failed to send message to Yona")
            return None
            
        self.logger.info(f"Message send request accepted, initial ID: {message_id}")
        
        # Store message information
        self.messages[message_id] = {
            "sent_at": time.time(),
            "thread_id": real_thread_id,
            "content": content,
            "uuid": message_uuid,
            "recipient": self.yona_agent_id
        }
        
        # If the message ID is "pending" and verify_delivery is True, verify delivery
        if message_id == "pending" and verify_delivery:
            # Wait for message delivery confirmation
            # This could come through event handling or by checking the thread
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if we've received a real message ID through event handling
                if message_id in self.messages and "real_id" in self.messages[message_id]:
                    real_id = self.messages[message_id]["real_id"]
                    self.logger.info(f"Message delivery confirmed with ID: {real_id}")
                    message_id = real_id
                    break
                
                # Try checking the thread for our message
                try:
                    # This is a fallback mechanism and might not be supported by the Coral server
                    messages = self.check_thread_messages(real_thread_id)
                    for msg in messages:
                        # Look for our message UUID in the content
                        if message_uuid in msg.get("content", ""):
                            self.logger.info(f"Found our message in thread with ID: {msg.get('message_id')}")
                            # Update our messages dictionary
                            self.messages[message_id]["real_id"] = msg.get("message_id")
                            message_id = msg.get("message_id")
                            break
                except Exception as e:
                    self.logger.debug(f"Error checking thread messages: {str(e)}")
                
                time.sleep(2)
                self.logger.debug(f"Waiting for message delivery confirmation... ({int(time.time() - start_time)}s elapsed)")
        
        self.logger.info(f"Message sent to Yona with final ID: {message_id}")
        
        # Add the message to the thread's message list
        if real_thread_id in self.threads:
            self.threads[real_thread_id].setdefault("messages", []).append({
                "id": message_id,
                "content": content,
                "sender": self.agent_id,
                "recipient": self.yona_agent_id,
                "sent_at": time.time()
            })
        
        return message_id
    
    def check_thread_messages(self, thread_id, since=None):
        """
        Check for messages in a thread.
        
        Args:
            thread_id (str): The ID of the thread to check
            since (float, optional): Only return messages newer than this timestamp. Defaults to None.
            
        Returns:
            list: List of messages in the thread
        """
        self.logger.info(f"Checking for messages in thread {thread_id}")
        
        try:
            # Try to use the get_thread_messages tool if available
            response = self.coral_client._send_tool_call("get_thread_messages", {
                "thread_id": thread_id
            })
            
            if response and "result" in response and "messages" in response["result"]:
                messages = response["result"]["messages"]
                self.logger.info(f"Found {len(messages)} messages in thread {thread_id}")
                
                # Filter messages by timestamp if since is provided
                if since is not None:
                    messages = [msg for msg in messages if msg.get("timestamp", 0) > since]
                    self.logger.info(f"Filtered to {len(messages)} messages since {since}")
                
                return messages
            else:
                self.logger.warning(f"No messages found in thread {thread_id}")
                return []
        except Exception as e:
            self.logger.error(f"Error checking thread messages: {str(e)}")
            return []
    
    def check_for_yona_messages(self, thread_id=None, since=None, max_threads=10):
        """
        Check for messages from Yona in one or all threads.
        
        Args:
            thread_id (str, optional): The ID of a specific thread to check. Defaults to None.
            since (float, optional): Only return messages newer than this timestamp. Defaults to None.
            max_threads (int, optional): Maximum number of threads to check if thread_id is None. Defaults to 10.
            
        Returns:
            list: List of messages from Yona
        """
        self.logger.info(f"Checking for messages from Yona{' in thread ' + thread_id if thread_id else ''}")
        
        yona_messages = []
        
        if thread_id:
            # Check a specific thread
            messages = self.check_thread_messages(thread_id, since)
            for msg in messages:
                if msg.get("sender_id") == self.yona_agent_id:
                    yona_messages.append(msg)
        else:
            # Check all threads, newest first
            threads_to_check = sorted(
                [t for t in self.threads.values() if "real_id" in t],
                key=lambda t: t.get("created_at", 0),
                reverse=True
            )[:max_threads]
            
            for thread in threads_to_check:
                thread_id = thread["real_id"]
                messages = self.check_thread_messages(thread_id, since)
                for msg in messages:
                    if msg.get("sender_id") == self.yona_agent_id:
                        yona_messages.append(msg)
        
        self.logger.info(f"Found {len(yona_messages)} messages from Yona")
        return yona_messages
    
    def process_mentions(self, timeout_seconds=30):
        """
        Process mentions of Agent Angus.
        
        Args:
            timeout_seconds (int, optional): Maximum time to wait for mentions in seconds. Defaults to 30.
            
        Returns:
            list: List of responses to mentions
        """
        self.logger.info(f"Waiting for mentions of Agent Angus (timeout: {timeout_seconds}s)")
        
        mentions = self.coral_client.wait_for_mentions(
            self.agent_id,
            timeout_seconds=timeout_seconds
        )
        
        if not mentions:
            self.logger.info("No mentions received from wait_for_mentions, checking threads directly...")
            
            # Fallback: Check for messages directly in threads
            last_check_time = time.time() - 300  # Check messages from the last 5 minutes
            yona_messages = self.check_for_yona_messages(since=last_check_time)
            
            if yona_messages:
                self.logger.info(f"Found {len(yona_messages)} messages from Yona by direct checking")
                
                # Convert to the same format as wait_for_mentions
                mentions = []
                for msg in yona_messages:
                    mentions.append({
                        "thread_id": msg.get("thread_id"),
                        "content": msg.get("content", ""),
                        "sender_id": msg.get("sender_id"),
                        "message_id": msg.get("message_id")
                    })
            else:
                self.logger.info("No messages found by direct checking either")
                return []
        
        self.logger.info(f"Received {len(mentions)} mentions/messages")
        
        responses = []
        for mention in mentions:
            thread_id = mention.get("thread_id")
            content = mention.get("content")
            sender_id = mention.get("sender_id")
            
            self.logger.info(f"Processing mention/message in thread {thread_id}: {content[:50]}...")
            
            # Process the mention
            response = self._process_mention(thread_id, content, sender_id)
            responses.append(response)
        
        return responses
    
    def handle_yona_response(self, data):
        """
        Handle responses from Yona.
        
        Args:
            data (dict): The message data
            
        Returns:
            bool: True if the message was handled, False otherwise
        """
        sender_id = data.get('sender_id')
        content = data.get('content', '')
        thread_id = data.get('thread_id')
        
        # Check if the message is from Yona
        if sender_id != self.yona_agent_id:
            return False
        
        self.logger.info(f"Received message from Yona in thread {thread_id}")
        
        # Check if Yona created a song
        if "Created song" in content:
            self.logger.info("Yona created a song!")
            
            # Extract song information
            lines = content.split('\n')
            song_info = {
                "title": lines[0].replace("Created song '", "").replace("'", ""),
                "audio_url": next((line.replace("Audio: ", "") for line in lines if line.startswith("Audio: ")), None),
                "lyrics": '\n'.join(lines[3:]) if len(lines) > 3 else ""
            }
            
            self.logger.info(f"Song information: {json.dumps(song_info, indent=2)}")
            
            # Send a thank you message
            thank_you = f"Thanks for creating '{song_info['title']}'! It sounds great!"
            self.send_message_to_yona(thread_id, thank_you)
            
            return True
        
        return False

def main():
    """
    Main entry point for the Angus Coral Adapter.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting Angus Coral Adapter")
    
    # Create the adapter with a consistent session ID
    adapter = AngusCoralAdapter(session_id="angus-agent", use_devmode=True)
    
    # Register the agent
    agent_id = adapter.register_agent()
    logger.info(f"Agent registered with ID: {agent_id}")
    
    # Define event handlers
    def handle_tool_call(data):
        logger.info(f"Received tool call: {json.dumps(data, indent=2)}")
        # Process tool calls here
        # This would be expanded to handle specific tool calls
    
    def handle_message(data):
        logger.info(f"Received message: {json.dumps(data, indent=2)}")
        
        # Check if the message is from Yona and handle it
        if adapter.handle_yona_response(data):
            logger.info("Message from Yona was handled")
        else:
            # Process other messages here
            pass
    
    # Start listening for events
    adapter.coral_client.start_listening({
        "tool_call": handle_tool_call,
        "message": handle_message
    })
    
    logger.info("Listening for events")
    
    # Run in continuous mode with improved reconnection logic
    try:
        retries = 0
        max_retries = 5
        while True:
            try:
                # Process mentions
                adapter.process_mentions(timeout_seconds=30)
                retries = 0  # Reset retries on success
                time.sleep(1)
            except Exception as e:
                retries += 1
                logger.error(f"Error processing mentions: {str(e)}, retry {retries}/{max_retries}")
                # Exponential backoff
                sleep_time = min(30, 5 * retries)
                logger.info(f"Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
                
                # If we've reached max retries, try to reconnect
                if retries >= max_retries:
                    logger.info("Max retries reached, attempting to reconnect...")
                    try:
                        # Re-register the agent
                        adapter.register_agent()
                        retries = 0
                    except Exception as reconnect_error:
                        logger.error(f"Error reconnecting: {str(reconnect_error)}")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")

if __name__ == "__main__":
    main()
