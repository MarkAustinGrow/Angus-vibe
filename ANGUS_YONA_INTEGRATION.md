# Angus-Yona Integration via Coral Protocol

This document describes the integration between Agent Angus and Yona using the Coral Protocol.

## Overview

Agent Angus and Yona are two AI agents that can communicate with each other through the Coral Protocol. This integration enables:

- Agent Angus to request music creation from Yona
- Yona to create music based on Angus's requests
- Angus to provide feedback on the music
- Collaborative workflows between the two agents

## Components

1. **Coral Protocol**: The communication protocol that enables agent-to-agent communication
2. **AngusCoralAdapter**: The adapter that allows Agent Angus to connect to the Coral server
3. **SimpleCoralAgent**: The base class that implements the Coral Protocol
4. **Test Script**: A script to test the communication between Angus and Yona

## Communication Flow

1. Agent Angus connects to the Coral server
2. Angus registers itself with its capabilities
3. Angus creates a thread with Yona
4. Angus sends messages to Yona in the thread
5. Yona processes the messages and responds
6. Angus processes Yona's responses

## Testing the Integration

The `test_angus_yona_communication.py` script tests the communication between Agent Angus and Yona. It performs three tests:

1. **Create a Thread and Send a Message**: Tests basic connectivity
2. **Test Yona's Music Capabilities**: Tests music creation requests
3. **Test Feedback Processing**: Tests providing feedback on music

### Running the Tests

#### On Windows:

```
run_angus_yona_test.bat
```

#### On Linux/macOS:

```
chmod +x run_angus_yona_test.sh
./run_angus_yona_test.sh
```

### Command Line Options

The test script supports the following command line options:

- `--server`: Coral server URL (default: http://coral.pushcollective.club:3001)
- `--agent-id`: Agent Angus ID (default: did:web:angus.ai)
- `--yona-id`: Yona agent ID (default: did:web:yona.ai)
- `--session`: Session ID (default: session1)
- `--wait-time`: Time to wait for responses in seconds (default: 60)

Example:

```
python test_angus_yona_communication.py --wait-time 120
```

### Monitoring the Tests

To monitor the tests, you should:

1. Run the test script on the Angus server
2. Monitor the logs on both the Angus and Yona servers

#### Monitoring Angus Logs:

The test script outputs detailed logs about the communication.

#### Monitoring Yona Logs:

```
docker-compose logs -f yona
```

Look for messages like "Received Coral message" in the Yona logs.

## Troubleshooting

### Common Issues

1. **Connection Failures**: Make sure both agents are connected to the Coral server
2. **Registration Failures**: Ensure the agent IDs are correct and the Coral server is running
3. **Thread Creation Failures**: Check that both agents are registered with the Coral server
4. **Message Sending Failures**: Verify that the thread ID is valid
5. **No Responses**: Make sure Yona is running and processing messages

### Debugging Tips

1. Enable debug logging for more detailed information
2. Check the Coral server logs for any errors
3. Verify that the message format is correct (includes the required "id" field)
4. Ensure that both agents are using the same session ID

## Future Improvements

1. **Enhanced Error Handling**: Add more robust error handling for edge cases
2. **Message Queuing**: Implement a message queue for reliable delivery
3. **Retry Logic**: Add retry logic for failed operations
4. **Automated Testing**: Create automated tests for continuous integration
5. **UI Integration**: Add a user interface for monitoring the communication

## References

- [Coral Protocol Documentation](https://github.com/modelcontextprotocol/protocol)
- [Yona Documentation](https://yona.ai/docs)
- [Agent Angus Documentation](https://github.com/MarkAustinGrow/Angus-vibe)
