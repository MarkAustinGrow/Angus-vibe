# Angus Coral Integration

This document provides instructions for integrating Agent Angus with the Coral Protocol server, allowing Angus to communicate with other agents like Yona.

## Overview

The Coral Protocol integration enables Agent Angus to:

1. Connect to the Coral server
2. Register itself with specific capabilities
3. Create threads with other agents (like Yona)
4. Send and receive messages in these threads
5. Process and respond to messages from other agents

## Prerequisites

Before using the Coral integration, ensure you have:

1. Python 3.7 or higher
2. Required Python packages:
   - requests
   - sseclient-py
   - All dependencies for Agent Angus

You can install the required packages using:

```bash
pip install requests sseclient-py
```

## Files

The Coral integration consists of the following files:

1. `angus_coral_adapter.py` - Adapter class that extends SimpleCoralAgent for Angus
2. `simple_coral_agent.py` - Base class for connecting to the Coral server
3. `run_angus_coral.py` - Main script for running Angus with Coral integration
4. `run_angus_coral.bat` - Windows batch file for running the integration
5. `run_angus_coral.sh` - Unix/Linux/macOS shell script for running the integration
6. `test_angus_coral_adapter.py` - Test script for the Coral adapter

## Configuration

The Coral integration can be configured using environment variables or command-line arguments:

- `CORAL_SERVER_URL` - URL of the Coral server (default: http://coral.pushcollective.club:3001)
- `AGENT_ID` - Unique identifier for Agent Angus (default: did:web:angus.ai)

These can be set in the environment or passed as command-line arguments to `run_angus_coral.py`.

## Running the Integration

### Using the Batch/Shell Scripts

#### Windows

```
run_angus_coral.bat [options]
```

#### Unix/Linux/macOS

```
./run_angus_coral.sh [options]
```

Make sure to make the shell script executable:

```bash
chmod +x run_angus_coral.sh
```

### Using the Python Script Directly

```
python run_angus_coral.py [options]
```

### Command-Line Options

- `--server-url URL` - URL of the Coral server
- `--agent-id ID` - Agent ID for Coral
- `--daemon` - Run in daemon mode with scheduled tasks
- `--web` - Run the web UI
- `--port PORT` - Port for the web UI (default: 5000)

## Testing the Integration

You can test the Coral integration using the provided test script:

```
python test_angus_coral_adapter.py
```

This script will:

1. Connect to the Coral server
2. Register Agent Angus with capabilities
3. Create a thread with Yona
4. Send a test message to Yona
5. Wait for and process any responses

## Docker Configuration

If you're using Docker Compose, ensure your configuration includes the necessary environment variables:

```yaml
services:
  angus-coral:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - CORAL_SERVER_URL=http://coral.pushcollective.club:3001
      - AGENT_ID=did:web:angus.ai
    volumes:
      - ./:/app
    networks:
      - your_network
```

## Monitoring

You can monitor the Coral integration using the logs:

```
tail -f angus_coral.log
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Coral server:

- Verify that the Coral server URL is correct
- Check that the Coral server is running and accessible
- Look for any error messages in the logs

### Message Delivery Issues

If messages aren't being delivered:

- Ensure that both agents are properly registered
- Check that the thread ID is valid
- Verify that the message format is correct

## Integration with Angus's Functionality

The Coral integration is designed to work alongside Angus's existing functionality. When a message is received from Yona or another agent, it can trigger Angus's music analysis, YouTube publishing, or comment response capabilities.

To customize how Angus responds to messages from other agents, modify the `handle_yona_message` method in `run_angus_coral.py`.

## Next Steps

Once you have basic communication working, you can:

1. Implement more sophisticated message handling
2. Add error recovery and reconnection logic
3. Integrate specific Angus capabilities with Coral communication
4. Implement additional agent-to-agent interactions
