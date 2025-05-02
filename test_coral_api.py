#!/usr/bin/env python3
"""
Test script for the Coral API.

This script tests different message formats to identify the correct format
that the Coral server expects.
"""
import json
import uuid
import requests
import logging
import http.client as http_client
import argparse
import time

# Configure enhanced logging for HTTP debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable HTTP connection debugging
http_client.HTTPConnection.debuglevel = 1

# Configure detailed logging for requests
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def test_list_agents(session_id, server_url="http://coral.pushcollective.club:3001"):
    """Test the list_agents tool with different message formats."""
    message_url = f"{server_url}/devmode/exampleApplication/privkey/session1/message?sessionId={session_id}"
    
    # Test different message formats
    payloads = [
        # Format 1: Basic tool_call
        {
            "type": "tool_call",
            "tool": "list_agents",
            "arguments": {}
        },
        # Format 2: With ID
        {
            "id": str(uuid.uuid4()),
            "type": "tool_call",
            "tool": "list_agents",
            "arguments": {}
        },
        # Format 3: Different structure
        {
            "action": "list_agents",
            "payload": {}
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    for i, payload in enumerate(payloads):
        print(f"\n--- Testing Format {i+1} ---")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(message_url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code < 400:
                print(f"SUCCESS: Format {i+1} worked!")
                return payload  # Return the successful format
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nAll formats failed.")
    return None

def test_register_agent(session_id, agent_id="angus", server_url="http://coral.pushcollective.club:3001"):
    """Test the register_agent tool with different message formats."""
    message_url = f"{server_url}/devmode/exampleApplication/privkey/session1/message?sessionId={session_id}"
    
    # Test different message formats
    payloads = [
        # Format 1: Basic tool_call
        {
            "type": "tool_call",
            "tool": "register_agent",
            "arguments": {
                "agent_id": agent_id,
                "name": "Agent Angus",
                "description": "YouTube publishing agent"
            }
        },
        # Format 2: With ID
        {
            "id": str(uuid.uuid4()),
            "type": "tool_call",
            "tool": "register_agent",
            "arguments": {
                "agent_id": agent_id,
                "name": "Agent Angus",
                "description": "YouTube publishing agent"
            }
        },
        # Format 3: With did:web: prefix
        {
            "type": "tool_call",
            "tool": "register_agent",
            "arguments": {
                "agent_id": f"did:web:{agent_id}",
                "name": "Agent Angus",
                "description": "YouTube publishing agent"
            }
        },
        # Format 4: Different structure
        {
            "action": "register_agent",
            "payload": {
                "agent_id": agent_id,
                "name": "Agent Angus",
                "description": "YouTube publishing agent"
            }
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    for i, payload in enumerate(payloads):
        print(f"\n--- Testing Format {i+1} ---")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(message_url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code < 400:
                print(f"SUCCESS: Format {i+1} worked!")
                return payload  # Return the successful format
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nAll formats failed.")
    return None

def connect_to_sse(agent_id="angus", server_url="http://coral.pushcollective.club:3001"):
    """Connect to the SSE endpoint and get a session ID."""
    import requests
    import re
    
    sse_url = f"{server_url}/devmode/exampleApplication/privkey/session1/sse?agentId={agent_id}"
    
    print(f"Connecting to SSE endpoint: {sse_url}")
    
    try:
        # Make a GET request to the SSE endpoint
        response = requests.get(sse_url, stream=True)
        
        # Read the first few lines to get the session ID
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Received: {decoded_line}")
                
                # Check if this is the endpoint event
                if decoded_line.startswith("event: endpoint"):
                    # The next line should contain the data
                    data_line = next(response.iter_lines()).decode('utf-8')
                    print(f"Endpoint data: {data_line}")
                    
                    # Extract the session ID from the data
                    if data_line.startswith("data:"):
                        endpoint_url = data_line[5:].strip()
                        session_id_match = re.search(r'sessionId=([^&]+)', endpoint_url)
                        if session_id_match:
                            session_id = session_id_match.group(1)
                            print(f"Extracted session ID: {session_id}")
                            return session_id
                    
                    break
        
        print("Failed to extract session ID")
        return None
        
    except Exception as e:
        print(f"Error connecting to SSE: {str(e)}")
        return None

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test the Coral API with different message formats.')
    parser.add_argument('--session-id', help='Session ID to use for the requests')
    parser.add_argument('--agent-id', default='angus', help='Agent ID to use for registration')
    parser.add_argument('--server-url', default='http://coral.pushcollective.club:3001', help='Coral server URL')
    parser.add_argument('--test', choices=['list', 'register', 'all'], default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    session_id = args.session_id
    
    if not session_id:
        print("No session ID provided, connecting to SSE to get one...")
        session_id = connect_to_sse(args.agent_id, args.server_url)
        
        if not session_id:
            print("Failed to get session ID, exiting.")
            return
    
    if args.test == 'list' or args.test == 'all':
        print("\n=== Testing list_agents ===")
        list_format = test_list_agents(session_id, args.server_url)
        
        if list_format:
            print(f"\nSuccessful list_agents format: {json.dumps(list_format, indent=2)}")
    
    if args.test == 'register' or args.test == 'all':
        print("\n=== Testing register_agent ===")
        register_format = test_register_agent(session_id, args.agent_id, args.server_url)
        
        if register_format:
            print(f"\nSuccessful register_agent format: {json.dumps(register_format, indent=2)}")

if __name__ == "__main__":
    main()
