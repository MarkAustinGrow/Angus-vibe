#!/usr/bin/env python3
"""
Docker-friendly Test Script for Coral Protocol Discovery

This script can be run directly in the Docker container to test agent discovery.
It supports dynamic session ID handling from multiple sources.
"""
import os
import sys
import json
import re
import argparse
import requests
from urllib.parse import urlparse

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Test Coral Protocol Discovery')
    
    parser.add_argument(
        '--server-url',
        type=str,
        default=os.environ.get('CORAL_SERVER_URL', 'http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse'),
        help='URL of the Coral Protocol server'
    )
    
    parser.add_argument(
        '--session-id',
        type=str,
        default=None,
        help='Session ID for the Coral Protocol server'
    )
    
    parser.add_argument(
        '--container-name',
        type=str,
        default='app_angus_coral_1',
        help='Name of the Docker container running the Coral Protocol server'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='/var/log/app.log',
        help='Path to the log file in the container'
    )
    
    return parser.parse_args()

# Get the session ID from various sources
def get_session_id(container_name=None, log_file=None):
    """
    Get the session ID from various sources.
    
    Args:
        container_name: Name of the Docker container
        log_file: Path to the log file
        
    Returns:
        Session ID if found, None otherwise
    """
    try:
        # Priority 1: Environment variable
        if 'CORAL_SESSION_ID' in os.environ:
            print(f"Using session ID from environment variable: {os.environ['CORAL_SESSION_ID']}")
            return os.environ['CORAL_SESSION_ID']
        
        # Priority 2: Docker logs (if container name is provided)
        if container_name:
            try:
                import subprocess
                result = subprocess.run(
                    ["docker", "logs", container_name],
                    capture_output=True,
                    text=True
                )
                
                match = re.search(r"Extracted session ID: ([0-9a-f-]+)", result.stdout)
                if match:
                    session_id = match.group(1)
                    print(f"Extracted session ID from Docker logs: {session_id}")
                    return session_id
            except Exception as e:
                print(f"Error extracting session ID from Docker logs: {str(e)}")
        
        # Priority 3: Container's log file (if running inside the container)
        if log_file:
            try:
                # Check if we're running inside the container
                in_container = False
                try:
                    with open('/proc/self/cgroup', 'r') as f:
                        in_container = 'docker' in f.read()
                except:
                    pass
                
                if in_container:
                    try:
                        # Try to read the log file
                        with open(log_file, 'r') as f:
                            for line in f:
                                match = re.search(r"Extracted session ID: ([0-9a-f-]+)", line)
                                if match:
                                    session_id = match.group(1)
                                    print(f"Extracted session ID from container log file: {session_id}")
                                    return session_id
                    except Exception as e:
                        print(f"Error reading log file: {str(e)}")
            except Exception as e:
                print(f"Error checking if running in container: {str(e)}")
        
        # Priority 4: Process output (if the Coral server is running in the same process)
        try:
            import subprocess
            result = subprocess.run(
                ["grep", "-r", "Extracted session ID", "/proc/*/fd/"],
                capture_output=True,
                text=True
            )
            
            match = re.search(r"Extracted session ID: ([0-9a-f-]+)", result.stdout)
            if match:
                session_id = match.group(1)
                print(f"Extracted session ID from process output: {session_id}")
                return session_id
        except Exception as e:
            print(f"Error extracting session ID from process output: {str(e)}")
        
        print("Could not find session ID from any source")
        return None
    except Exception as e:
        print(f"Error getting session ID: {str(e)}")
        return None

# Initialize session ID to None (will be set later)
session_id = None

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
    
    # Parse command line arguments
    args = parse_args()
    
    # Update global variables
    global server_url, base_url, session_id
    
    # Update server URL if provided
    if args.server_url:
        server_url = args.server_url
        parsed_url = urlparse(server_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
    
    # Priority 1: Command line argument
    if args.session_id:
        session_id = args.session_id
        print(f"Using session ID from command line argument: {session_id}")
    # Priority 2: Get from various sources
    else:
        session_id = get_session_id(args.container_name, args.log_file)
        if not session_id:
            print("Could not get session ID from any source")
            print("Please provide a session ID using one of the following methods:")
            print("  1. Command line argument: --session-id <session_id>")
            print("  2. Environment variable: export CORAL_SESSION_ID=<session_id>")
            print("  3. Docker logs: Make sure the container is running and logs are accessible")
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
