# Agent Angus - Yona Integration Guide

This document explains how Agent Angus has been configured to communicate with Agent Yona through the Coral Protocol. It provides details on the implementation, testing procedures, and troubleshooting tips.

## Overview

Agent Angus has been enhanced to communicate with Agent Yona, a music creation agent, through the Coral Protocol. The integration enables Angus to:

1. Create threads with Yona
2. Send messages to Yona with reliable mention formats
3. Process responses from Yona, including song creation results
4. Maintain a persistent connection with improved reconnection logic

## Implementation Details

### Key Changes to `angus_coral_adapter.py`

1. **Consistent Session ID**: The adapter now uses a fixed session ID (`angus-agent`) to ensure consistent identification across restarts.

2. **Yona Integration Methods**:
   - `create_thread_with_yona()`: Creates a thread that includes both Angus and Yona
   - `send_message_to_yona()`: Sends messages to Yona using multiple mention formats for reliability
   - `handle_yona_response()`: Processes responses from Yona, including song creation results

3. **Improved Reconnection Logic**:
   - Exponential backoff for retries
   - Automatic re-registration after maximum retries
   - Proper error handling and logging

4. **Thread Tracking**:
   - The adapter now maintains a record of created threads
   - This enables better context management for ongoing conversations

## Testing the Integration

A test script (`test_angus_yona_communication.py`) has been provided to verify the communication between Agent Angus and Agent Yona.

### Running the Test

#### On Windows:

```
run_angus_yona_test.bat
```

#### On Unix/Linux:

```bash
chmod +x run_angus_yona_test.sh
./run_angus_yona_test.sh
```

### Test Process

The test script performs the following steps:

1. Initializes the Angus Coral Adapter with a consistent session ID
2. Registers Agent Angus with the Coral server
3. Creates a thread with Yona
4. Sends a message to Yona requesting a song
5. Listens for responses from Yona
6. Processes any song creation responses
7. Sends a thank you message when a song is received

The test has a timeout of 5 minutes (300 seconds) and will log progress every 30 seconds.

### Expected Output

If the test is successful, you should see output similar to:

```
INFO - Starting Angus-Yona communication test
INFO - Angus Coral Adapter initialized with session ID: angus-agent
INFO - Registering Agent Angus with Coral server
INFO - Agent Angus registered with ID: [agent-id]
INFO - Creating thread with Yona
INFO - Thread created with ID: [thread-id]
INFO - Sending message to Yona in thread [thread-id]
INFO - Message sent to Yona with ID: [message-id]
INFO - Listening for responses from Yona
INFO - Waiting for response from Yona... (30s elapsed)
...
INFO - Received message from yona-agent in thread [thread-id]
INFO - Message from Yona: Created song 'AI Creativity'...
INFO - Yona created a song!
INFO - Song information: {"title":"AI Creativity","audio_url":"https://example.com/song.mp3","lyrics":"..."}
INFO - Sending message to Yona in thread [thread-id]
INFO - Message sent to Yona with ID: [message-id]
INFO - Test successful! Received response from Yona.
INFO - Angus-Yona communication test completed successfully!
```

## Troubleshooting

### Common Issues

#### 1. Agent Registration Fails

**Symptoms**:
- "Failed to register Agent Angus" error
- No agent ID returned

**Solutions**:
- Verify the Coral server URL is correct
- Check that the server is running
- Try using a different session ID
- Check network connectivity

#### 2. Thread Creation Fails

**Symptoms**:
- "Failed to create thread with Yona" error
- No thread ID returned

**Solutions**:
- Verify that Agent Angus was registered successfully
- Check that Yona is registered on the Coral server
- Verify the Yona agent ID is correct (`yona-agent`)

#### 3. No Response from Yona

**Symptoms**:
- Test times out waiting for a response
- No messages received from Yona

**Solutions**:
- Verify that Yona is running and connected to the Coral server
- Check that the message was sent with the correct mention formats
- Try sending a different message
- Check the Coral server logs for any errors

#### 4. Connection Issues

**Symptoms**:
- "Error processing mentions" errors
- Connection timeouts

**Solutions**:
- Check network connectivity
- Verify the Coral server is running
- Try restarting the test
- Check for firewall or proxy issues

## Advanced Configuration

### Customizing the Session ID

If you need to use a different session ID for Agent Angus, modify the initialization in both the adapter and test script:

```python
adapter = AngusCoralAdapter(session_id="your-custom-id", use_devmode=True)
```

### Modifying Timeout Values

To change the test timeout, modify the `timeout` variable in `test_yona_communication()`:

```python
timeout = 600  # 10 minutes
```

### Changing the Yona Agent ID

If Yona uses a different agent ID, modify the `yona_agent_id` attribute in the `AngusCoralAdapter` class:

```python
self.yona_agent_id = "different-yona-id"
```

## Deployment

To deploy the updated Angus Coral adapter to your server:

1. Copy the updated `angus_coral_adapter.py` file to your server
2. Restart the Coral Protocol adapter:

```bash
# On the server
cd /opt/angus
docker-compose restart coral
```

3. Check the logs to verify the adapter is running with the correct session ID:

```bash
docker logs angus_coral_1
```

## Conclusion

With these changes, Agent Angus should now be able to reliably communicate with Agent Yona through the Coral Protocol. The consistent session ID and improved mention formats ensure that messages are properly detected, while the enhanced reconnection logic improves reliability.

If you encounter any issues not covered in the troubleshooting section, please check the Coral Protocol documentation or contact the development team for assistance.
