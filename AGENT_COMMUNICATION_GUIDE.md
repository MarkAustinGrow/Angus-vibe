# Agent Communication Guide: Connecting Agent Angus with Agent Yona

This comprehensive guide explains how to configure Agent Angus to communicate with Agent Yona through the Coral Protocol. It provides detailed instructions, code examples, and best practices for establishing reliable agent-to-agent communication.

## Table of Contents

1. [Overview](#overview)
2. [Agent Identifiers](#agent-identifiers)
3. [Setting Up Agent Angus](#setting-up-agent-angus)
4. [Communicating with Agent Yona](#communicating-with-agent-yona)
5. [Handling Responses from Yona](#handling-responses-from-yona)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Integration](#advanced-integration)

## Overview

The Coral Protocol enables AI agents to communicate with each other through a standardized messaging system. This guide focuses on connecting Agent Angus with Agent Yona, which is a music creation agent that can generate songs based on prompts.

Key components:
- **Coral Server**: The central hub that routes messages between agents
- **Agent Yona**: A music creation agent with the fixed ID `yona-agent`
- **Agent Angus**: Your agent that will communicate with Yona

## Agent Identifiers

For reliable communication, agents must use consistent identifiers:

- **Yona Agent ID**: `yona-agent`
- **Angus Agent ID**: Choose a consistent identifier for Angus, e.g., `angus-agent`

## Setting Up Agent Angus

### 1. Install the Coral Client Library

```python
# Install the Coral client library
pip install coral-client
```

### 2. Initialize the Coral Client

```python
from coral_client import CoralClient

# Initialize the Coral client with a consistent session ID for Angus
angus_client = CoralClient(
    session_id="angus-agent",  # Use a consistent session ID
    server_url="https://coral.pushcollective.club",
    use_devmode=True
)
```

### 3. Register Agent Angus with the Coral Server

```python
# Register Angus with the Coral server
angus_id = angus_client.register_agent(
    name="AngusAgent",
    description="An agent that communicates with Yona for music creation"
)

print(f"Angus registered with ID: {angus_id}")
```

## Communicating with Agent Yona

### 1. Create a Thread with Yona

```python
# Create a thread that includes both Angus and Yona
thread_id = angus_client.create_thread(
    participants=["angus-agent", "yona-agent"],
    metadata={"topic": "Music Creation"}
)

print(f"Thread created with ID: {thread_id}")
```

### 2. Send a Message to Yona

To ensure Yona detects your message, use **multiple mention formats**:

```python
# Craft a message with multiple mention formats
message_content = "@yona-agent Hey Yona, can you create a song about AI collaboration?"

# Send the message with an explicit mention in the API call
message_id = angus_client.send_message(
    thread_id=thread_id,
    content=message_content,
    mentions=["yona-agent"]  # Explicit mention in the API call
)

print(f"Message sent with ID: {message_id}")
```

### 3. Mention Formats Recognized by Yona

Yona recognizes the following mention formats (in order of reliability):

1. **Explicit mention in API call**: Include `"yona-agent"` in the `mentions` list
2. **@mention in content**: Include `"@yona-agent"` in the message content
3. **<@mention> in content**: Include `"<@yona-agent>"` in the message content
4. **Name mention in content**: Include `"yona"` (case insensitive) in the message content

For maximum reliability, use multiple mention formats simultaneously.

## Handling Responses from Yona

### 1. Set Up an Event Listener

```python
def message_handler(data):
    """Handle incoming messages."""
    if data.get('sender_id') == "yona-agent":
        print(f"Received message from Yona: {data.get('content')}")
        
        # Extract song information if available
        if "Created song" in data.get('content', ''):
            print("Yona created a song!")
            # Process the song information
            # ...

# Start listening for events
angus_client.start_listening({
    'message': message_handler
})
```

### 2. Expected Response Format from Yona

When Yona successfully creates a song, it responds with a message in this format:

```
Created song 'Song Title'
Audio: https://example.com/song.mp3
Lyrics:
[Song lyrics here]
```

## Troubleshooting

### Common Issues and Solutions

1. **No response from Yona**:
   - Ensure you're using the correct agent ID (`yona-agent`)
   - Use multiple mention formats simultaneously
   - Check if the Coral server is operational

2. **Connection issues**:
   - The SSE connection may time out after 60 seconds; your client should automatically reconnect
   - Verify your network connection to the Coral server

3. **Message not detected as a mention**:
   - Include the agent ID in the `mentions` list
   - Use the `@yona-agent` format in the message content
   - Include the word "yona" in your message

## Advanced Integration

### Continuous Communication

For ongoing communication with Yona:

```python
import time

def run_continuous_mode():
    """Run in continuous mode, periodically checking for messages."""
    while True:
        try:
            # Process any pending messages
            # ...
            
            # Sleep to avoid tight loops
            time.sleep(1)
        except Exception as e:
            print(f"Error in continuous mode: {str(e)}")
            # Reconnect if necessary
            # ...

# Start continuous mode in a separate thread
import threading
threading.Thread(target=run_continuous_mode, daemon=True).start()
```

### Sample Integration Code

Here's a complete example of Agent Angus communicating with Agent Yona:

```python
#!/usr/bin/env python3
"""
Agent Angus - Yona Communication Example

This script demonstrates how Agent Angus can communicate with Agent Yona
through the Coral Protocol to request song creation.
"""

import logging
import time
import threading
import sys
from coral_client import CoralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("angus_agent")

class AngusAgent:
    """Agent Angus implementation."""
    
    def __init__(self):
        """Initialize Agent Angus."""
        self.session_id = "angus-agent"
        self.client = CoralClient(
            session_id=self.session_id,
            server_url="https://coral.pushcollective.club",
            use_devmode=True
        )
        self.agent_id = None
        self.threads = {}
        self.songs = []
    
    def register(self):
        """Register with the Coral server."""
        logger.info("Registering Agent Angus")
        self.agent_id = self.client.register_agent(
            name="AngusAgent",
            description="An agent that communicates with Yona for music creation"
        )
        logger.info(f"Registered with agent ID: {self.agent_id}")
        return self.agent_id
    
    def create_thread_with_yona(self):
        """Create a thread with Yona."""
        logger.info("Creating thread with Yona")
        thread_id = self.client.create_thread(
            participants=[self.session_id, "yona-agent"],
            metadata={"topic": "Music Creation"}
        )
        logger.info(f"Thread created with ID: {thread_id}")
        self.threads[thread_id] = {
            "created_at": time.time(),
            "participants": [self.session_id, "yona-agent"]
        }
        return thread_id
    
    def request_song(self, thread_id, topic):
        """Request a song from Yona."""
        logger.info(f"Requesting song about: {topic}")
        
        # Craft message with multiple mention formats
        message = f"@yona-agent Hey Yona, can you create a song about {topic}?"
        
        # Send the message with an explicit mention
        message_id = self.client.send_message(
            thread_id=thread_id,
            content=message,
            mentions=["yona-agent"]
        )
        
        logger.info(f"Song request sent with message ID: {message_id}")
        return message_id
    
    def handle_message(self, data):
        """Handle incoming messages."""
        sender_id = data.get('sender_id')
        content = data.get('content', '')
        thread_id = data.get('thread_id')
        
        logger.info(f"Received message from {sender_id} in thread {thread_id}")
        
        if sender_id == "yona-agent":
            logger.info("Message is from Yona")
            
            if "Created song" in content:
                logger.info("Yona created a song!")
                
                # Extract song information
                lines = content.split('\n')
                song_info = {
                    "title": lines[0].replace("Created song '", "").replace("'", ""),
                    "audio_url": lines[1].replace("Audio: ", ""),
                    "lyrics": '\n'.join(lines[3:])
                }
                
                self.songs.append(song_info)
                logger.info(f"Added song: {song_info['title']}")
                
                # Send a thank you message
                self.client.send_message(
                    thread_id=thread_id,
                    content=f"Thanks for creating '{song_info['title']}'! It sounds great!",
                    mentions=["yona-agent"]
                )
    
    def start_listening(self):
        """Start listening for events."""
        logger.info("Starting to listen for events")
        
        # Set up event handlers
        event_handlers = {
            'message': self.handle_message
        }
        
        # Start the event listener
        listener_thread = self.client.start_listening(event_handlers)
        return listener_thread
    
    def run(self):
        """Run Agent Angus."""
        # Register with the Coral server
        self.register()
        
        # Start listening for events
        self.start_listening()
        
        # Create a thread with Yona
        thread_id = self.create_thread_with_yona()
        
        # Request a song
        self.request_song(thread_id, "artificial intelligence and creativity")
        
        # Keep the main thread running
        logger.info("Agent Angus is now running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Agent Angus")

def main():
    """Main function."""
    angus = AngusAgent()
    angus.run()
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

By following this guide, you should be able to successfully configure Agent Angus to communicate with Agent Yona through the Coral Protocol. The key is to use consistent agent IDs and multiple mention formats to ensure reliable communication.
