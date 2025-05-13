# Angus-Yona Communication over Coral Protocol

This document explains how to use the improved implementation for communication between Angus and Yona over the Coral Protocol.

## Overview

The implementation follows the best practices recommended by the Coral server team:

- Uses the direct tool invocation approach for more control and lower latency
- Implements standardized message formats with metadata for tracking
- Includes error handling and reconnection logic
- Implements a heartbeat mechanism to keep the connection alive
- Uses correlation IDs to link requests and responses

## Files

- `angus_yona_communication.py`: Main implementation of the Angus-Yona communication
- `run_angus_yona.sh`: Shell script to run the communication on Linux/macOS
- `run_angus_yona.bat`: Batch script to run the communication on Windows

## Prerequisites

- Python 3.7 or higher
- OpenAI API key (set in the environment or .env file)
- langchain_mcp_adapters==0.0.10 (will be installed automatically if not present)
- aiohttp>=3.8.5 (will be installed automatically if not present)

## Usage

### Linux/macOS

```bash
# Make the script executable
chmod +x run_angus_yona.sh

# Run with default parameters
./run_angus_yona.sh

# Run with custom parameters
./run_angus_yona.sh --prompt "Create a jazz song about AI" --wait-for-agents 1
```

### Windows

```batch
# Run with default parameters
run_angus_yona.bat

# Run with custom parameters
run_angus_yona.bat --prompt "Create a jazz song about AI" --wait-for-agents 1
```

## Command Line Arguments

- `--server-url`: Base URL of the Coral Protocol server (default: http://coral.pushcollective.club:5555)
- `--agent-id`: ID of this agent (default: angus_agent)
- `--target-agent-id`: ID of the target agent (default: yona)
- `--session-id`: Session ID for the Coral Protocol server (default: session1)
- `--prompt`: Prompt for the song creation (default: "Create a happy K-pop song about friendship between AI agents")
- `--timeout`: Timeout for operations in seconds (default: 300)
- `--wait-for-agents`: Number of agents to wait for (default: 2)

## Environment Variables

- `CORAL_SERVER_URL`: Base URL of the Coral Protocol server (overrides the default)

## How It Works

1. **Connection**: The script connects to the Coral Protocol server using the specified parameters.
2. **Agent Discovery**: It lists all registered agents and looks for the target agent (Yona).
3. **Thread Creation**: It creates a thread with the target agent for communication.
4. **Function Call**: It sends a function call to the target agent to create a song.
5. **Response Handling**: It waits for a response from the target agent and processes it.
6. **Result Display**: It displays the result in a formatted way.

## Message Format

### Function Call

```json
{
    "type": "function_call",
    "function": "create_song",
    "arguments": {
        "prompt": "Create a happy K-pop song about friendship between AI agents"
    },
    "metadata": {
        "sender": "angus_agent",
        "timestamp": "2025-05-13T09:00:00Z",
        "message_id": "unique_id"
    }
}
```

### Expected Response

```json
{
    "type": "function_response",
    "function": "create_song",
    "result": {
        "title": "Song about AI",
        "lyrics": "This is a song about AI...",
        "melody": "C G Am F C G F C",
        "created_at": "2025-05-13T09:05:00Z"
    },
    "metadata": {
        "sender": "yona_agent",
        "timestamp": "2025-05-13T09:05:00Z",
        "correlation_id": "unique_id"
    }
}
```

## Troubleshooting

### No Agents Found

If no agents are found, check:

1. That both Angus and Yona are connected to the same session
2. That both agents are using the same application ID and privacy key
3. That both agents are connected at the same time

### Connection Issues

If you have connection issues, check:

1. That the server URL is correct
2. That the server is running
3. That your network allows connections to the server

### No Response from Yona

If you don't receive a response from Yona, check:

1. That Yona is properly connected to the server
2. That Yona is listening for messages
3. That the thread ID is correct
4. That the target agent ID is correct

## Coordination with Team Yona

To ensure successful communication, coordinate with Team Yona on:

1. **Session ID**: Both teams should use the same session ID (default: session1)
2. **Agent IDs**: Angus uses "angus_agent" and Yona should use an ID containing "yona"
3. **Connection Timing**: Both agents should be connected at the same time
4. **Message Format**: Yona should expect function calls in the format described above
5. **Response Format**: Yona should send responses in the format described above

## Logs

The script logs all operations to:

- Console (stdout)
- `angus_yona_communication.log` file

Check these logs for detailed information about the communication process.
