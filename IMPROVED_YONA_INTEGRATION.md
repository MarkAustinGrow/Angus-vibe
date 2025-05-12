# Improved Angus-Yona Integration

This document describes the improved integration between Angus and Yona agents using the Coral Protocol.

## Overview

The improved Angus-Yona integration enhances the communication between Angus and Yona using the Coral Protocol. The key improvements include:

1. **Enhanced Agent Description**: Adding a proper agent description to improve discoverability
2. **Dynamic Session ID Handling**: Robust handling of session IDs for reliable connections
3. **MCP Tools Approach**: Using the MCP tools approach for agent discovery and communication
4. **Thread-Based Communication**: Implementing thread-based communication for function calls

## Architecture

The integration consists of the following components:

1. **Angus Agent**: The core Angus agent that provides music analysis capabilities
2. **Coral Protocol Adapter**: An adapter that connects Angus to the Coral Protocol
3. **Coral Protocol Server**: A server that facilitates communication between agents
4. **Yona Agent**: The Yona agent that provides song creation capabilities

The communication flow is as follows:

```
Angus Agent <-> Coral Protocol Adapter <-> Coral Protocol Server <-> Yona Agent
```

## Implementation

The implementation includes the following files:

- `angus_coral_adapter.py`: Updated adapter for connecting Angus to the Coral Protocol
- `src/coral_protocol/langchain/runnable.py`: Updated runnable implementation for the Coral Protocol
- `test_improved_yona_communication.py`: Test script for the improved Angus-Yona communication
- `run_improved_yona_test.sh` and `run_improved_yona_test.bat`: Scripts to run the test

### Key Improvements

1. **Enhanced Agent Description**:
   - Added agent description parameter to the SSE connection URL
   - Improved agent identification and discoverability

2. **Dynamic Session ID Handling**:
   - Robust extraction of session IDs from endpoint events
   - Proper handling of session IDs for API calls

3. **MCP Tools Approach**:
   - Using the MCP tools approach for agent discovery and capabilities retrieval
   - Leveraging the SSE connection for agent discovery

4. **Thread-Based Communication**:
   - Implementing thread-based communication for function calls
   - Proper handling of function responses

## Usage

### Running the Test Script

To test the improved Angus-Yona communication, run the following command:

```bash
# On Linux/macOS
./run_improved_yona_test.sh

# On Windows
run_improved_yona_test.bat
```

By default, the script will run all tests. You can specify a specific test to run:

```bash
# Test discovering Yona
./run_improved_yona_test.sh --test discover

# Test getting Yona's capabilities
./run_improved_yona_test.sh --test capabilities

# Test calling Yona's create_song function
./run_improved_yona_test.sh --test call --prompt "Create a happy K-pop song about friendship between AI agents"
```

### Command-Line Arguments

The test script accepts the following command-line arguments:

- `--server-url`: URL of the Coral Protocol server (default: `http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse`)
- `--openai-api-key`: OpenAI API key (default: from environment variable `OPENAI_API_KEY`)
- `--did-domain`: Domain for the DID (default: `angus.ai`)
- `--private-key-path`: Path to the private key file (default: None)
- `--simulation-mode`: Run in simulation mode (default: False)
- `--test`: Test to run (`discover`, `capabilities`, `call`, or `all`) (default: `all`)
- `--yona-did`: DID of the Yona agent (if known) (default: None)
- `--prompt`: Prompt for the song creation (default: `Create a happy K-pop song about friendship between AI agents`)
- `--agent-description`: Description of the Angus agent (default: `Angus is a music analysis agent that can analyze songs and provide feedback`)

## Docker Integration

To run the improved Angus-Yona integration in Docker, you can use the existing Docker setup with the updated code:

```bash
# Build the Docker image
docker-compose build angus_coral

# Run the Docker container
docker-compose up -d angus_coral
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Coral Protocol server:

1. Check that the server URL is correct
2. Ensure that the server is running
3. Check the logs for any error messages

### Agent Discovery Issues

If you're having trouble discovering the Yona agent:

1. Check that the Yona agent is registered with the Coral Protocol server
2. Ensure that the session ID is being properly extracted
3. Check the logs for any error messages

### Function Call Issues

If you're having trouble calling functions on Yona:

1. Check that Yona is registered with the Coral Protocol server
2. Ensure that the function name is correct
3. Check that the function parameters are correct
4. Look for error messages in the logs

## Future Improvements

1. **Full MCP Client Implementation**: Implement the full `MultiServerMCPClient` from `langchain_mcp_adapters.client`
2. **Asynchronous Function Calls**: Implement asynchronous function calls to avoid blocking the main thread
3. **Function Call Timeouts**: Add timeouts for function calls to prevent hanging
4. **Function Call Retries**: Implement retries for failed function calls
5. **Function Call Validation**: Validate function parameters before sending the call
