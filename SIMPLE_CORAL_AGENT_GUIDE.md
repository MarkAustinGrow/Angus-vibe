# Simple Coral Agent Guide

This guide explains how to connect a simple agent to the Coral server to communicate with the Yona agent. This implementation is designed for agents that don't have DID (Decentralized Identifier) capabilities.

## Prerequisites

Before you begin, make sure you have the following:

- Python 3.7 or higher
- Required Python packages:
  - requests
  - sseclient-py
  - httpx (optional, only needed for advanced features)

You can install these packages using pip:

```bash
pip install requests sseclient-py httpx
```

## Files Overview

This guide includes two main files:

1. `simple_coral_agent.py` - A simplified Coral client for agents without DID capabilities
2. `test_coral_communication.py` - A test script that demonstrates how to use the SimpleCoralAgent

## Understanding the Simple Coral Agent

The `SimpleCoralAgent` class provides a simplified interface for connecting to the Coral server and communicating with other agents. It handles:

- Establishing an SSE (Server-Sent Events) connection to the Coral server
- Extracting the session ID from the endpoint event
- Registering the agent with the Coral server
- Creating threads with other agents
- Sending and receiving messages

## Step-by-Step Guide

### 1. Initialize the Agent

Create an instance of the `SimpleCoralAgent` class with the Coral server URL and a unique agent ID:

```python
from simple_coral_agent import SimpleCoralAgent
import uuid

# Create a unique agent ID
agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"

# Initialize the agent
agent = SimpleCoralAgent("http://coral.pushcollective.club:3001", agent_id)
```

### 2. Connect to the Coral Server

Connect to the Coral server and wait for the session ID:

```python
if agent.connect():
    print(f"Successfully connected agent {agent_id} to Coral server")
    # Continue with the next steps
else:
    print("Failed to connect to Coral server")
```

### 3. Register the Agent

Register the agent with the Coral server:

```python
if agent.register_agent("My Test Agent", "A simple test agent for Coral communication"):
    print(f"Successfully registered agent {agent_id}")
    # Continue with the next steps
else:
    print("Failed to register agent")
```

### 4. Create a Thread with Yona

Create a thread with the Yona agent:

```python
thread_id = agent.create_thread(["did:web:yona.ai", agent_id])
if thread_id:
    print(f"Created thread {thread_id} with Yona")
    # Continue with the next steps
else:
    print("Failed to create thread")
```

### 5. Send a Message to Yona

Send a message to the Yona agent:

```python
if agent.send_message(thread_id, "Hello Yona! This is a test message."):
    print("Successfully sent message to Yona")
else:
    print("Failed to send message")
```

### 6. Process Incoming Messages

Process incoming messages from the Yona agent:

```python
# Process messages for 30 seconds
agent.process_messages(timeout=30)

# Or keep processing messages indefinitely
try:
    while True:
        agent.process_messages(timeout=5)
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down agent...")
    agent.running = False
```

## Customizing Message Handling

To customize how your agent handles incoming messages, you can extend the `process_messages` method:

```python
def custom_process_messages(self, timeout=5):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            data = self.event_queue.get(block=False)
            print(f"Received message: {data}")
            
            # Check if this is a message from Yona
            if data.get("sender_id") == "did:web:yona.ai":
                # Respond to Yona's message
                content = data.get("content", "")
                thread_id = data.get("thread_id")
                
                if thread_id:
                    response = f"Thanks for your message: '{content}'. This is an automated response."
                    self.send_message(thread_id, response)
                    
        except queue.Empty:
            time.sleep(0.1)
            continue
```

## Running the Test Script

To run the test script:

```bash
python test_coral_communication.py
```

This will:
1. Connect to the Coral server
2. Register the agent
3. Create a thread with Yona
4. Send a message to Yona
5. Wait for and process any responses
6. Keep the agent running to receive further messages

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Coral server:

- Verify that the Coral server URL is correct
- Check that the Coral server is running and accessible
- Look for any error messages in the logs

### Session ID Issues

If the agent fails to get a session ID:

- Check the logs for any errors in the SSE connection
- Verify that the Coral server is sending the endpoint event
- Increase the timeout in the `connect` method

### Message Delivery Issues

If messages aren't being delivered:

- Ensure that both agents are properly registered
- Check that the thread ID is valid
- Verify that the message format is correct

## Next Steps

Once you have basic communication working, you can:

1. Implement more sophisticated message handling
2. Add error recovery and reconnection logic
3. Integrate the agent with your existing systems
4. Implement specific capabilities for your agent

## Conclusion

This guide has shown you how to connect a simple agent to the Coral server and communicate with the Yona agent. By following these steps, you can create your own agent that interacts with Yona and other agents on the Coral network.

For more advanced features, such as DID-based authentication and secure messaging, you may want to explore the full Coral client implementation.
