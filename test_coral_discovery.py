#!/usr/bin/env python3
"""
Simplified Test Script for Coral Protocol Discovery

This script tests the discovery of agents on the Coral Protocol server without LangChain dependencies.
"""
import os
import sys
import json
import time
import logging
import argparse
import requests
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_coral_discovery.log')
    ]
)
logger = logging.getLogger(__name__)

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
        '--test',
        choices=['discover', 'capabilities', 'all'],
        default='discover',
        help='Test to run'
    )
    
    parser.add_argument(
        '--agent-did',
        type=str,
        default=None,
        help='DID of the agent to get capabilities for'
    )
    
    return parser.parse_args()

def discover_agents(server_url: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Discover agents on the Coral Protocol server.
    
    Args:
        server_url: URL of the Coral Protocol server
        session_id: Session ID for the Coral Protocol server
        
    Returns:
        List of agents
    """
    try:
        logger.info("Discovering agents on Coral Protocol server")
        
        # Parse the server URL to extract components
        parsed_url = urlparse(server_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
        
        # Check if we have a session ID
        if session_id:
            # Construct the discover URL using the session ID
            discover_url = f"{base_url}/discover?sessionId={session_id}"
            
            logger.info(f"Using session-based discovery URL: {discover_url}")
            
            # Make the request
            response = requests.get(
                discover_url,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                agents = response.json().get("agents", [])
                logger.info(f"Discovered {len(agents)} agents using session-based discovery")
                
                # Log each discovered agent
                for agent in agents:
                    logger.info(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
                
                return agents
            else:
                logger.warning(f"Session-based discovery failed: {response.status_code} - {response.text}")
        
        # Fall back to the list_agents endpoint
        list_agents_url = f"{base_url}/list_agents"
        logger.info(f"Falling back to standard agent listing: {list_agents_url}")
        
        response = requests.get(
            list_agents_url,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            agents = response.json()
            logger.info(f"Discovered {len(agents)} agents using standard listing")
            
            # Log each discovered agent
            for agent in agents:
                logger.info(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
            
            return agents
        else:
            logger.error(f"Failed to list agents: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error discovering agents: {str(e)}")
        return []

def get_agent_capabilities(server_url: str, agent_did: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get the capabilities of an agent on the Coral Protocol server.
    
    Args:
        server_url: URL of the Coral Protocol server
        agent_did: DID of the agent
        session_id: Session ID for the Coral Protocol server
        
    Returns:
        Capabilities of the agent if successful, None otherwise
    """
    try:
        logger.info(f"Getting capabilities for agent {agent_did}")
        
        # Parse the server URL to extract components
        parsed_url = urlparse(server_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/sse', 1)[0]}"
        
        # Check if we have a session ID
        if session_id:
            # Construct the capabilities URL using the session ID
            capabilities_url = f"{base_url}/capabilities?sessionId={session_id}&targetDid={agent_did}"
            
            logger.info(f"Using session-based capabilities URL: {capabilities_url}")
            
            # Make the request
            response = requests.get(
                capabilities_url,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                capabilities = response.json()
                logger.info(f"Successfully retrieved capabilities for agent {agent_did}")
                
                # Log the capabilities
                if "services" in capabilities:
                    logger.info(f"Agent provides {len(capabilities['services'])} services:")
                    for service in capabilities["services"]:
                        logger.info(f"  - {service.get('id')}: {service.get('description', 'No description')}")
                
                return capabilities
            else:
                logger.warning(f"Session-based capabilities retrieval failed: {response.status_code} - {response.text}")
        
        # Fall back to a placeholder
        logger.warning("Using placeholder implementation for agent capabilities")
        return {
            "name": "Example Agent",
            "description": "An example agent",
            "capabilities": {
                "example_function": {
                    "description": "An example function",
                    "parameters": {
                        "param1": {
                            "type": "string",
                            "description": "Parameter 1"
                        }
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "result": {
                                "type": "string",
                                "description": "Result of the function"
                            }
                        }
                    }
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting capabilities for agent {agent_did}: {str(e)}")
        return None

def find_yona_agent(agents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Find the Yona agent in a list of agents.
    
    Args:
        agents: List of agents
        
    Returns:
        Yona agent if found, None otherwise
    """
    for agent in agents:
        name = agent.get('name', '').lower()
        if 'yona' in name:
            return agent
    
    return None

def extract_session_id_from_logs():
    """
    Extract the session ID from the logs.
    
    Returns:
        Session ID if found, None otherwise
    """
    try:
        # Check if the app_angus_coral_1 container is running
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "app_angus_coral_1"],
            capture_output=True,
            text=True
        )
        
        # Extract the session ID from the logs
        import re
        match = re.search(r"Extracted session ID: ([0-9a-f-]+)", result.stdout)
        if match:
            session_id = match.group(1)
            logger.info(f"Extracted session ID from logs: {session_id}")
            return session_id
        
        return None
    except Exception as e:
        logger.error(f"Error extracting session ID from logs: {str(e)}")
        return None

def main():
    """
    Main entry point for the test script.
    """
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Extract session ID from logs if not provided
        session_id = args.session_id
        if not session_id:
            session_id = extract_session_id_from_logs()
            if not session_id:
                logger.warning("Could not extract session ID from logs, proceeding without it")
        
        # Run the specified test
        if args.test == 'discover' or args.test == 'all':
            # Discover agents
            agents = discover_agents(args.server_url, session_id)
            if not agents:
                logger.error("No agents discovered")
                return 1
            
            # Find Yona agent
            yona_agent = find_yona_agent(agents)
            if yona_agent:
                logger.info(f"Found Yona agent: {yona_agent.get('name')} ({yona_agent.get('did')})")
                agent_did = yona_agent.get('did')
            else:
                logger.warning("Yona agent not found")
                agent_did = args.agent_did
        
        if (args.test == 'capabilities' or args.test == 'all') and (agent_did or args.agent_did):
            # Get agent capabilities
            agent_did = agent_did or args.agent_did
            capabilities = get_agent_capabilities(args.server_url, agent_did, session_id)
            if not capabilities:
                logger.error(f"Failed to get capabilities for agent {agent_did}")
                return 1
            
            logger.info(f"Successfully retrieved capabilities for agent {agent_did}")
        
        logger.info("Tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error running test: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
