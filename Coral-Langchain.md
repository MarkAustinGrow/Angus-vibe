# Integrating Angus with Coral Protocol using LangChain

This document outlines the plan for integrating Angus with the Coral Protocol using LangChain, allowing Angus to participate in a multi-agent ecosystem while preserving its current functionality.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Implementation Plan](#implementation-plan)
5. [Docker Configuration](#docker-configuration)
6. [Tool Definitions](#tool-definitions)
7. [Agent Registration and Communication](#agent-registration-and-communication)
8. [Deployment Strategy](#deployment-strategy)
9. [Testing and Validation](#testing-and-validation)
10. [Usage Examples](#usage-examples)

## Introduction

Angus is a powerful agent for YouTube publishing and feedback collection. By integrating it with the Coral Protocol, we can expose Angus's capabilities to other AI agents in a standardized way, enabling collaborative workflows while maintaining Angus's existing functionality.

### Benefits of Integration

- **Interoperability**: Angus can communicate with other AI agents using a standardized protocol
- **Extended Capabilities**: Angus can leverage capabilities of other agents in the ecosystem
- **Preserved Functionality**: The integration doesn't modify Angus's core functionality
- **Scalability**: New capabilities can be added to the ecosystem without modifying Angus directly

## Architecture Overview

The integration follows a sidecar pattern, where a new component (Angus Coral Agent) runs alongside the existing Angus service:

```
┌─────────────────────────────────────┐      ┌─────────────────────────┐
│           Existing Setup            │      │    New Components       │
│                                     │      │                         │
│  ┌─────────┐         ┌─────────┐    │      │    ┌───────────────┐    │
│  │         │         │         │    │      │    │               │    │
│  │  Angus  │◄───────►│  Web UI │    │      │    │ Angus Coral   │    │
│  │         │         │         │    │      │    │    Agent      │    │
│  └─────────┘         └─────────┘    │      │    │               │    │
│        ▲                            │      │    └───────┬───────┘    │
└────────┼────────────────────────────┘      └────────────┼────────────┘
         │                                                 │
         │                                                 ▼
         │                                    ┌─────────────────────────┐
         │                                    │                         │
         └────────────────────────────────────┤   Coral Protocol Server │
                                              │                         │
                                              └─────────────────────────┘
                                                         ▲
                                                         │
                                              ┌──────────┴──────────────┐
                                              │                         │
                                              │     Other AI Agents     │
                                              │                         │
                                              └─────────────────────────┘
```

The Angus Coral Agent:
- Connects to the Coral Protocol Server (coral.pushcollective.club/sse)
- Registers as an agent with specific capabilities
- Listens for requests from other agents
- Translates these requests into calls to Angus's functionality
- Returns results back to the requesting agents

## Prerequisites

To implement this integration, you'll need:

1. **Python 3.12.10** or later
2. **LangChain libraries**:
   - langchain
   - langchain_mcp_adapters
   - langchain-openai
3. **Access to the Coral Protocol Server** at coral.pushcollective.club/sse
4. **OpenAI API key** for LangChain functionality (set as OPENAI_API_KEY in environment variables)

## Implementation Plan

The implementation consists of several key components:

### 1. Angus Coral Agent (angus_coral_agent.py)

This is the main script that:
- Registers with the Coral Protocol Server
- Defines tools that map to Angus functionality
- Listens for and processes messages from other agents

### 2. Tool Definitions

Define JSON schema for each Angus capability, including:
- YouTube video upload and management
- Comment retrieval and response
- Music analysis

### 3. Docker Container

A separate container that runs the Angus Coral Agent alongside the existing Angus services.

## Docker Configuration

Add a new service to your existing docker-compose.yml:

```yaml
services:
  # Existing services
  angus:
    # ... existing configuration ...
  
  web:
    # ... existing configuration ...
    
  # New Coral agent service
  angus_coral:
    build:
      context: .
      dockerfile: Dockerfile.coral
    volumes:
      - ./data:/app/data  # Share the data directory with the main Angus container
    environment:
      - CORAL_SERVER_URL=https://coral.pushcollective.club/sse
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - angus  # Ensure Angus is running first
```

Create a new Dockerfile.coral:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy necessary files
COPY requirements.coral.txt .
COPY supabase_client.py .
COPY youtube_client.py .
COPY angus_coral_agent.py .
# Add any other necessary files

# Install dependencies
RUN pip install --no-cache-dir -r requirements.coral.txt

# Run the Coral agent
CMD ["python", "angus_coral_agent.py"]
```

Create requirements.coral.txt:

```
requests
langchain
langchain_mcp_adapters
langchain-openai
# Any other dependencies needed
```

## Tool Definitions

The Angus Coral Agent will expose the following tools:

### 1. Upload Video Tool

```python
upload_video_tool = {
    "name": "upload_video",
    "description": "Upload a video to YouTube",
    "parameters": {
        "type": "object",
        "properties": {
            "video_url": {
                "type": "string",
                "description": "URL of the video file to upload"
            },
            "title": {
                "type": "string",
                "description": "Title of the video"
            },
            "description": {
                "type": "string",
                "description": "Description of the video"
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Tags for the video"
            }
        },
        "required": ["video_url", "title"]
    }
}
```

### 2. Fetch Comments Tool

```python
fetch_comments_tool = {
    "name": "fetch_comments",
    "description": "Fetch comments for a YouTube video",
    "parameters": {
        "type": "object",
        "properties": {
            "youtube_id": {
                "type": "string",
                "description": "YouTube video ID"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of comments to retrieve"
            }
        },
        "required": ["youtube_id"]
    }
}
```

### 3. Analyze Music Tool

```python
analyze_music_tool = {
    "name": "analyze_music",
    "description": "Analyze music and generate a description",
    "parameters": {
        "type": "object",
        "properties": {
            "audio_url": {
                "type": "string",
                "description": "URL of the audio file to analyze"
            },
            "analysis_type": {
                "type": "string",
                "enum": ["basic", "detailed"],
                "description": "Type of analysis to perform"
            }
        },
        "required": ["audio_url"]
    }
}
```

## Agent Registration and Communication

The Angus Coral Agent will register with the Coral Protocol Server and handle communication using the following approach:

```python
import requests
import json
import time
from typing import Dict, Any, List, Optional
import logging

# Import Angus components
from supabase_client import SupabaseClient
from youtube_client import YouTubeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AngusCoral:
    def __init__(self, coral_server_url="https://coral.pushcollective.club/sse"):
        # Initialize Angus components
        self.supabase = SupabaseClient()
        self.youtube = YouTubeClient()
        
        # Coral server connection
        self.coral_url = coral_server_url
        self.agent_id = "angus_agent"
        self.agent_description = "Angus is a YouTube publishing and feedback collection agent that can upload videos, retrieve comments, and analyze music."
        self.agent_did = None  # Will be assigned by Coral server
        
        # Define tools
        self.tools = [
            upload_video_tool,
            fetch_comments_tool,
            analyze_music_tool
        ]
        
        # Tool implementations
        self.tool_implementations = {
            "upload_video": self.upload_video,
            "fetch_comments": self.fetch_comments,
            "analyze_music": self.analyze_music
        }
        
    def register_agent(self):
        """Register with the Coral server"""
        # Registration code based on Coral Protocol examples
        registration_data = {
            "agentId": self.agent_id,
            "agentDescription": self.agent_description,
            "tools": self.tools,
            "waitForAgents": 2  # Wait for at least 2 agents to be available
        }
        
        # Send registration request
        response = requests.post(
            f"{self.coral_url}/register",
            json=registration_data
        )
        
        if response.status_code == 200:
            result = response.json()
            self.agent_did = result.get("agentDid")
            logger.info(f"Successfully registered with Coral server. Agent DID: {self.agent_did}")
            return True
        else:
            logger.error(f"Failed to register with Coral server: {response.text}")
            return False
    
    def listen_for_messages(self):
        """Listen for messages from other agents"""
        # Connect to SSE endpoint
        sse_url = f"{self.coral_url}/events?agentId={self.agent_id}"
        
        # Implementation would use SSE client to listen for events
        # For simplicity, we'll use a polling approach here
        while True:
            try:
                # Poll for new messages
                response = requests.get(f"{self.coral_url}/messages?agentId={self.agent_id}")
                
                if response.status_code == 200:
                    messages = response.json()
                    
                    for message in messages:
                        self.process_message(message)
                
                # Wait before polling again
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error listening for messages: {str(e)}")
                time.sleep(5)  # Wait longer after an error
    
    def process_message(self, message: Dict[str, Any]):
        """Process a message from another agent"""
        # Extract message details
        thread_id = message.get("threadId")
        sender_id = message.get("senderId")
        content = message.get("content", {})
        
        # Check if this is a tool invocation
        tool_name = content.get("tool")
        tool_params = content.get("parameters", {})
        
        if tool_name and tool_name in self.tool_implementations:
            # Execute the tool
            logger.info(f"Executing tool: {tool_name} with parameters: {tool_params}")
            
            try:
                result = self.tool_implementations[tool_name](tool_params)
                
                # Send the result back
                self.send_message(thread_id, sender_id, {
                    "result": result,
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                
                # Send error message
                self.send_message(thread_id, sender_id, {
                    "error": str(e),
                    "status": "error"
                })
    
    def send_message(self, thread_id: str, recipient_id: str, content: Dict[str, Any]):
        """Send a message to another agent"""
        message_data = {
            "threadId": thread_id,
            "senderId": self.agent_id,
            "recipientId": recipient_id,
            "content": content
        }
        
        response = requests.post(
            f"{self.coral_url}/send",
            json=message_data
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent message to {recipient_id}")
            return True
        else:
            logger.error(f"Failed to send message: {response.text}")
            return False
    
    # Tool implementations
    def upload_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a video to YouTube"""
        title = params.get("title")
        video_url = params.get("video_url")
        description = params.get("description", "")
        tags = params.get("tags", [])
        
        # Call Angus's upload functionality
        youtube_id = self.youtube.upload_video(
            video_url=video_url,
            title=title,
            description=description,
            tags=tags
        )
        
        if youtube_id == "URL_EXPIRED":
            return {
                "success": False,
                "error": "Video URL has expired",
                "status": "url_expired"
            }
        
        return {
            "success": youtube_id is not None,
            "youtube_id": youtube_id,
            "message": f"Video '{title}' uploaded successfully" if youtube_id else "Upload failed"
        }
    
    def fetch_comments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch comments for a YouTube video"""
        youtube_id = params.get("youtube_id")
        max_results = params.get("max_results", 100)
        
        # Call Angus's comment fetching functionality
        comments = self.youtube.fetch_comments(youtube_id, max_results=max_results)
        
        return {
            "success": True,
            "comments": comments,
            "count": len(comments)
        }
    
    def analyze_music(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze music and generate a description"""
        # This would integrate with Angus's music analysis capabilities
        # For now, we'll return a placeholder
        return {
            "success": True,
            "analysis": "Music analysis would be performed here",
            "details": params
        }
    
    def run(self):
        """Run the Angus Coral agent"""
        if self.register_agent():
            logger.info("Starting to listen for messages")
            self.listen_for_messages()
        else:
            logger.error("Failed to register agent. Exiting.")

if __name__ == "__main__":
    agent = AngusCoral()
    agent.run()
```

## Deployment Strategy

The deployment strategy follows these steps:

1. **Develop and Test Locally**:
   - Create the Angus Coral Agent script
   - Test with the Coral Protocol Server
   - Verify tool functionality

2. **Containerize**:
   - Create Dockerfile.coral
   - Build the container
   - Test the containerized agent

3. **Update docker-compose.yml**:
   - Add the angus_coral service
   - Configure environment variables
   - Set up volume sharing

4. **Deploy**:
   - Deploy the updated docker-compose.yml
   - Monitor logs for successful registration and operation

## Testing and Validation

To test the integration:

1. **Agent Registration Test**:
   - Verify the Angus Coral Agent successfully registers with the Coral Protocol Server
   - Check logs for the assigned agent DID

2. **Tool Invocation Tests**:
   - Test each tool with valid parameters
   - Verify correct handling of error cases (e.g., expired URLs)

3. **Integration Tests**:
   - Use another agent to send requests to Angus
   - Verify the correct execution of requested actions
   - Check response formatting and error handling

## Usage Examples

Here are examples of how other agents can interact with Angus through the Coral Protocol:

### Example 1: Uploading a Video

```python
# Another agent sending a request to upload a video
message = {
    "tool": "upload_video",
    "parameters": {
        "video_url": "https://example.com/video.mp4",
        "title": "Test Video Upload",
        "description": "This is a test video uploaded via Coral Protocol"
    }
}

# Send to Angus agent
send_message(thread_id, "angus_agent", message)
```

### Example 2: Fetching Comments

```python
# Another agent requesting comments for a video
message = {
    "tool": "fetch_comments",
    "parameters": {
        "youtube_id": "dQw4w9WgXcQ",
        "max_results": 10
    }
}

# Send to Angus agent
send_message(thread_id, "angus_agent", message)
```

### Example 3: Multi-Agent Workflow

A more complex workflow might involve multiple agents:

1. A user interface agent receives a request to "create and upload a music video about cats"
2. The user interface agent delegates to a content creation agent to generate the video
3. The content creation agent produces a video URL
4. The user interface agent sends the video URL to Angus for uploading to YouTube
5. Angus uploads the video and returns the YouTube ID
6. The user interface agent presents the result to the user

This demonstrates how Angus can participate in a collaborative workflow with other specialized agents.

## Conclusion

By integrating Angus with the Coral Protocol using LangChain, we enable it to participate in a multi-agent ecosystem while preserving its current functionality. This integration opens up new possibilities for collaborative workflows and extends the capabilities of the overall system.

The sidecar pattern used in this integration ensures minimal disruption to the existing Angus services while providing a standardized interface for other agents to interact with Angus's capabilities.
