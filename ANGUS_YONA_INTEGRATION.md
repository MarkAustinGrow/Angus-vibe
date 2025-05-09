# Angus-Yona Integration

This document describes the integration between Angus and Yona agents using the Coral Protocol.

## Overview

The Angus-Yona integration allows Angus to communicate with Yona using the Coral Protocol. This enables Angus to:

1. Discover Yona on the Coral Protocol server
2. Retrieve Yona's capabilities
3. Call functions on Yona, such as `create_song`
4. Respond to function calls from Yona

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

- `angus_coral_adapter.py`: Adapter for connecting Angus to the Coral Protocol
- `src/coral_protocol/langchain/runnable.py`: Runnable implementation for the Coral Protocol
- `test_angus_yona_communication.py`: Test script for the Angus-Yona communication
- `run_angus_yona_test.sh` and `run_angus_yona_test.bat`: Scripts to run the test

### Key Features

1. **Robust Connection Handling**:
   - Graceful handling of registration failures
   - Exponential backoff for reconnection attempts
   - Heartbeat monitoring to detect disconnections

2. **Comprehensive Event Handling**:
   - Specialized handlers for different event types
   - Proper JSON parsing with error handling
   - Session ID extraction from endpoint URLs

3. **Agent Discovery and Capabilities**:
   - Session-based agent discovery
   - Retrieval of agent capabilities
   - Tracking of known agents

4. **Function Calling**:
   - Direct function calls using the message endpoint
   - Fallback to thread-based approach if needed
   - Proper handling of function responses

## Usage

### Running the Test Script

To test the Angus-Yona communication, run the following command:

```bash
# On Linux/macOS
./run_angus_yona_test.sh

# On Windows
run_angus_yona_test.bat
```

By default, the script will run all tests. You can specify a specific test to run:

```bash
# Test discovering Yona
./run_angus_yona_test.sh --test discover

# Test getting Yona's capabilities
./run_angus_yona_test.sh --test capabilities

# Test calling Yona's create_song function
./run_angus_yona_test.sh --test call --prompt "Create a happy K-pop song about friendship between AI agents"
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

## Extending the Integration

### Adding New Functions to Angus

To add new functions that Angus can expose to other agents, modify the `_create_coral_runnable` method in `angus_coral_adapter.py`:

```python
def _create_coral_runnable(self) -> CoralRunnable:
    """
    Create a Coral runnable for the Angus agent.
    
    Returns:
        CoralRunnable instance
    """
    # Define the functions to expose through Coral
    functions = {
        "upload_video": self.angus_agent.upload_video,
        "fetch_comments": self.angus_agent.fetch_comments,
        "analyze_music": self.angus_agent.analyze_music,
        "new_function": self.angus_agent.new_function  # Add your new function here
    }
    
    # Create the Coral runnable
    coral_runnable = CoralRunnable(
        functions=functions,
        config=self.coral_config
    )
    
    return coral_runnable
```

### Calling New Functions on Yona

To call new functions on Yona, use the `call_agent` method:

```python
result = adapter.call_agent(
    agent_did=yona_did,
    function_name="new_function",
    param1="value1",
    param2="value2"
)
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Coral Protocol server:

1. Check that the server URL is correct
2. Ensure that the server is running
3. Check the logs for any error messages

### Function Call Issues

If you're having trouble calling functions on Yona:

1. Check that Yona is registered with the Coral Protocol server
2. Ensure that the function name is correct
3. Check that the function parameters are correct
4. Look for error messages in the logs

## Future Improvements

1. **Asynchronous Function Calls**: Implement asynchronous function calls to avoid blocking the main thread
2. **Function Call Timeouts**: Add timeouts for function calls to prevent hanging
3. **Function Call Retries**: Implement retries for failed function calls
4. **Function Call Validation**: Validate function parameters before sending the call
5. **Function Call Logging**: Improve logging for function calls and responses
