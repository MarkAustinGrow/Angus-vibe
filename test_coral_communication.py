from simple_coral_agent import SimpleCoralAgent
import time
import uuid

# Create a unique agent ID
agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"

# Initialize the agent
agent = SimpleCoralAgent("http://coral.pushcollective.club:3001", agent_id)

# Connect to the Coral server
if agent.connect():
    print(f"Successfully connected agent {agent_id} to Coral server")
    
    # Register the agent
    if agent.register_agent(f"Test Agent {agent_id}", "A simple test agent for Coral communication"):
        print(f"Successfully registered agent {agent_id}")
        
        # Create a thread with Yona
        thread_id = agent.create_thread(["did:web:yona.ai", agent_id])
        if thread_id:
            print(f"Created thread {thread_id} with Yona")
            
            # Send a message to Yona
            if agent.send_message(thread_id, "Hello Yona! This is a test message."):
                print("Successfully sent message to Yona")
                
                # Process any responses
                print("Waiting for responses...")
                agent.process_messages(timeout=30)
        
    # Keep the agent running to receive messages
    try:
        while True:
            agent.process_messages(timeout=5)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down agent...")
        agent.running = False
else:
    print("Failed to connect to Coral server")
