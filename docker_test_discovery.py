#!/usr/bin/env python3
"""
Docker-friendly Test Script for Coral Protocol Discovery

This script can be run directly in the Docker container to test agent discovery.
"""
import os
import sys
import json
import re
import requests
from urllib.parse import urlparse

# Get the session ID from the logs
def get_session_id():
    try:
        # Try to extract from environment variable
        if 'CORAL_SESSION_ID' in os.environ:
            return os.environ['CORAL_SESSION_ID']
        
        # Try to extract from Docker logs
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "app_angus_coral_1"],
            capture_output=True,
            text=True
        )
        
        match = re.search(r"Extracted session ID: ([0-9a-f-]+)", result.stdout)
        if match:
            return match.group(1)
        
        # Try to extract directly from the container's logs
        with open('/proc/self/cmdline', 'r') as f:
            cmdline = f.read().split('\0')
            if 'app_angus_coral_1' in cmdline:
                with open('/var/log/app.log', 'r') as log:
                    for line in log:
                        match = re.search(r"Extracted session ID: ([0-9a-f-]+)", line)
                        if match:
                            return match.group(1)
        
        return None
    except Exception as e:
        print(f"Error getting session ID: {str(e)}")
        return None

# Manually specify the session ID if known
session_id = "c6ee7b66-7a7f-4e1c-8983-4c8aa31bbf10"  # Replace with the actual session ID from the logs

# Get the server URL
server_url = os.environ.get('CORAL_SERVER_URL', 'http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse')

# Parse the server URL to extract components
parsed_url = urlparse(server_url)
base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"

# Discover agents
def discover_agents():
    print(f"Discovering agents on Coral Protocol server: {base_url}")
    
    # Construct the discover URL using the session ID
    discover_url = f"{base_url}/discover?sessionId={session_id}"
    
    print(f"Using discovery URL: {discover_url}")
    
    try:
        # Make the request
        response = requests.get(
            discover_url,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            agents = response.json().get("agents", [])
            print(f"Discovered {len(agents)} agents:")
            
            # Print each discovered agent
            for agent in agents:
                print(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
            
            return agents
        else:
            print(f"Failed to discover agents: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error discovering agents: {str(e)}")
        return []

# Get agent capabilities
def get_agent_capabilities(agent_did):
    print(f"Getting capabilities for agent {agent_did}")
    
    # Construct the capabilities URL using the session ID
    capabilities_url = f"{base_url}/capabilities?sessionId={session_id}&targetDid={agent_did}"
    
    print(f"Using capabilities URL: {capabilities_url}")
    
    try:
        # Make the request
        response = requests.get(
            capabilities_url,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            capabilities = response.json()
            print(f"Successfully retrieved capabilities for agent {agent_did}")
            
            # Print the capabilities
            if "services" in capabilities:
                print(f"Agent provides {len(capabilities['services'])} services:")
                for service in capabilities["services"]:
                    print(f"  - {service.get('id')}: {service.get('description', 'No description')}")
            
            return capabilities
        else:
            print(f"Failed to get capabilities: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting capabilities: {str(e)}")
        return None

# Find Yona agent
def find_yona_agent(agents):
    for agent in agents:
        name = agent.get('name', '').lower()
        if 'yona' in name:
            return agent
    
    return None

# Main function
def main():
    print("Starting Coral Protocol discovery test")
    
    # Get the session ID
    global session_id
    if not session_id:
        session_id = get_session_id()
        if not session_id:
            print("Could not get session ID, please specify it manually in the script")
            return 1
    
    print(f"Using session ID: {session_id}")
    
    # Discover agents
    agents = discover_agents()
    if not agents:
        print("No agents discovered")
        return 1
    
    # Find Yona agent
    yona_agent = find_yona_agent(agents)
    if yona_agent:
        print(f"Found Yona agent: {yona_agent.get('name')} ({yona_agent.get('did')})")
        
        # Get Yona's capabilities
        yona_did = yona_agent.get('did')
        capabilities = get_agent_capabilities(yona_did)
        if not capabilities:
            print(f"Failed to get capabilities for Yona agent {yona_did}")
    else:
        print("Yona agent not found")
    
    print("Test completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
