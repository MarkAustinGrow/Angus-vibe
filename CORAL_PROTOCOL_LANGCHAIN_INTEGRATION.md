# Coral Protocol LangChain Integration for Agent Angus

This document provides detailed information about the Coral Protocol LangChain integration for Agent Angus, which allows Angus to share its tools with other agents and use tools from other agents through the Coral Protocol.

## Overview

The Coral Protocol is a communication protocol that enables AI agents to discover and interact with each other. By integrating Agent Angus with the Coral Protocol using LangChain, we enable Angus to:

1. Register with a Coral Protocol server
2. Expose its tools (upload videos, manage comments, analyze music) to other agents
3. Discover other agents on the Coral Protocol network
4. Call functions on other agents
5. Receive and handle function calls from other agents

This integration bridges three systems:
- Core Agent Angus functionality
- The CrewAI integration
- The Coral Protocol with LangChain

## Architecture

The integration consists of several components:

1. **Core LangChain Integration**:
   - `src/coral_protocol/langchain/config.py`: Configuration for the Coral Protocol integration
   - `src/coral_protocol/langchain/runnable.py`: Main class for interacting with the Coral Protocol
   - `src/coral_protocol/langchain/__init__.py`: Package initialization

2. **Angus Adapter**:
   - `angus_coral_langchain_adapter.py`: Adapter that connects Angus to the Coral Protocol

3. **CrewAI Integration**:
   - `coral_protocol_tool.py`: CrewAI tool for interacting with the Coral Protocol

4. **Scripts**:
   - `test_angus_coral_langchain.py`: Test script for the integration
   - `run_angus_coral_langchain.py`: Run script for the integration
   - `run_angus_coral_langchain.bat`: Windows batch script
   - `run_angus_coral_langchain.sh`: Unix/Linux/macOS shell script

## Exposed Tools

Agent Angus exposes the following tools through the Coral Protocol:

1. **upload_videos**: Upload pending songs from Supabase to YouTube
   - Parameters:
     - `limit` (integer, default: 5): Maximum number of videos to upload

2. **manage_comments**: Fetch comments from YouTube videos and respond using OpenAI
   - Parameters:
     - `limit` (integer, default: 10): Maximum number of videos to process
     - `max_replies` (integer, default: 5): Maximum number of replies to post

3. **analyze_music**: Analyze music using OpenAI to extract insights
   - Parameters:
     - `url` (string): URL of the music file or YouTube video
     - `is_youtube` (boolean, default: false): Whether the URL is a YouTube video
     - `model` (string, default: "gpt-4o"): OpenAI model to use

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure that the necessary environment variables are set:
   - `OPENAI_API_KEY`: API key for OpenAI
   - `SUPABASE_URL`: URL for Supabase
   - `SUPABASE_KEY`: API key for Supabase
   - `YOUTUBE_CLIENT_ID`: Client ID for YouTube API
   - `YOUTUBE_CLIENT_SECRET`: Client secret for YouTube API
   - `YOUTUBE_API_KEY`: API key for YouTube API
   - `YOUTUBE_CHANNEL_ID`: Channel ID for YouTube

## Usage

### Running Agent Angus with Coral Protocol

To run Agent Angus with the Coral Protocol LangChain integration:

```bash
# Windows
run_angus_coral_langchain.bat

# Unix/Linux/macOS
./run_angus_coral_langchain.sh
```

You can customize the behavior with command-line options:

```bash
# Windows
run_angus_coral_langchain.bat --server-url "http://coral.example.com/sse" --host "127.0.0.1" --port 5001 --no-discover

# Unix/Linux/macOS
./run_angus_coral_langchain.sh --server-url "http://coral.example.com/sse" --host "127.0.0.1" --port 5001 --no-discover
```

### Testing the Integration

To test the Coral Protocol LangChain integration:

```bash
# Test the connection to the Coral server
python test_angus_coral_langchain.py --test connection

# Test getting the capabilities of an agent
python test_angus_coral_langchain.py --test capabilities --agent-did "did:web:example.com"

# Test calling a function on another agent
python test_angus_coral_langchain.py --test call --agent-did "did:web:example.com" --function "analyze_text" --args '{"text": "Hello, world!"}'

# Start a server to listen for requests
python test_angus_coral_langchain.py --test server
```

### Using the CrewAI Tool

To use the Coral Protocol in a CrewAI workflow:

```python
from coral_protocol_tool import CoralProtocolTool
from angus_coral_langchain_adapter import AngusCoralLangChainAdapter
from crewai import Agent, Task, Crew

# Initialize the Coral adapter
coral_adapter = AngusCoralLangChainAdapter(
    coral_server_url="http://coral.example.com/sse"
)

# Create the Coral Protocol tool
coral_tool = CoralProtocolTool(coral_adapter)

# Create an agent with the Coral Protocol tool
agent = Agent(
    name="Coral Agent",
    tools=[coral_tool],
    # ... other agent parameters
)

# Create a task that uses the Coral Protocol tool
task = Task(
    description="Call the analyze_music function on Agent Yona",
    agent=agent,
    expected_output="Music analysis results"
)

# Create a crew with the agent and task
crew = Crew(
    agents=[agent],
    tasks=[task]
)

# Run the crew
result = crew.kickoff()
```

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Ensure that the Coral server URL is correct and accessible
   - Check network connectivity and firewall settings

2. **Authentication Errors**:
   - Ensure that the DID and private key are valid
   - Check that the agent is properly registered with the Coral server

3. **Function Call Errors**:
   - Ensure that the target agent exists and is registered with the Coral server
   - Check that the function name and parameters are correct

### Logging

The integration uses Python's logging module to log information, warnings, and errors. You can adjust the logging level in the scripts to get more or less detailed logs:

```python
# More detailed logs
logging.basicConfig(level=logging.DEBUG)

# Less detailed logs
logging.basicConfig(level=logging.WARNING)
```

## Development

### Adding New Tools

To add a new tool to Agent Angus and expose it through the Coral Protocol:

1. Add the tool to the `AngusTools` class in `angus_tools.py`
2. Add a handler method to the `AngusCoralLangChainAdapter` class in `angus_coral_langchain_adapter.py`
3. Add the tool to the capability document in the `_create_capability_document` method

### Customizing the Integration

You can customize the integration by modifying the following:

1. **Capability Document**: Modify the `_create_capability_document` method in `angus_coral_langchain_adapter.py` to change the exposed tools and their descriptions
2. **Error Handling**: Modify the handler methods in `angus_coral_langchain_adapter.py` to change how errors are handled
3. **Authentication**: Modify the `_sign_payload` method in `src/coral_protocol/langchain/runnable.py` to change how payloads are signed

## References

- [Coral Protocol Documentation](https://coral-protocol.org/docs)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Agent Angus Documentation](https://github.com/MarkAustinGrow/Angus-vibe)
