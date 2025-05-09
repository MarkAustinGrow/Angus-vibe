#!/usr/bin/env python3
"""
Test script for Angus Coral Agent

This script tests the connection to the Coral Protocol Server and verifies
that the Angus Coral Agent can register and communicate with other agents.
"""
import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_coral_connection(coral_url: str) -> bool:
    """
    Test connection to the Coral Protocol Server.
    
    Args:
        coral_url: URL of the Coral Protocol Server
        
    Returns:
        True if connection is successful, False otherwise
    """
    logger.info(f"Testing connection to Coral server at {coral_url}")
    
    try:
        # Try to connect to the server
        response = requests.get(f"{coral_url}/health")
        
        if response.status_code == 200:
            logger.info("Successfully connected to Coral server")
            return True
        else:
            logger.error(f"Failed to connect to Coral server: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error connecting to Coral server: {str(e)}")
        return False

def test_agent_registration(coral_url: str) -> Optional[str]:
    """
    Test agent registration with the Coral Protocol Server.
    
    Args:
        coral_url: URL of the Coral Protocol Server
        
    Returns:
        Agent DID if registration is successful, None otherwise
    """
    logger.info("Testing agent registration")
    
    # Registration data
    registration_data = {
        "agentId": "test_agent",
        "agentDescription": "Test agent for verifying Coral Protocol integration",
        "tools": [],
        "waitForAgents": 1
    }
    
    try:
        # Send registration request
        response = requests.post(
            f"{coral_url}/register",
            json=registration_data
        )
        
        if response.status_code == 200:
            result = response.json()
            agent_did = result.get("agentDid")
            logger.info(f"Successfully registered test agent. Agent DID: {agent_did}")
            return agent_did
        else:
            logger.error(f"Failed to register test agent: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error registering test agent: {str(e)}")
        return None

def test_list_agents(coral_url: str) -> bool:
    """
    Test listing agents registered with the Coral Protocol Server.
    
    Args:
        coral_url: URL of the Coral Protocol Server
        
    Returns:
        True if listing agents is successful, False otherwise
    """
    logger.info("Testing listing agents")
    
    try:
        # Send list agents request
        response = requests.get(f"{coral_url}/agents")
        
        if response.status_code == 200:
            agents = response.json()
            logger.info(f"Successfully listed agents: {len(agents)} agents found")
            
            # Check if Angus agent is registered
            angus_agent = next((agent for agent in agents if agent.get("agentId") == "angus_agent"), None)
            
            if angus_agent:
                logger.info("Angus agent is registered with the Coral server")
                logger.info(f"Angus agent DID: {angus_agent.get('agentDid')}")
                logger.info(f"Angus agent description: {angus_agent.get('agentDescription')}")
                return True
            else:
                logger.warning("Angus agent is not registered with the Coral server")
                logger.info("Available agents:")
                for agent in agents:
                    logger.info(f"  - {agent.get('agentId')}: {agent.get('agentDescription')}")
                return False
        else:
            logger.error(f"Failed to list agents: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return False

def main():
    """
    Main entry point for the test script.
    """
    # Get Coral server URL from environment variable or use default
    coral_url = os.environ.get("CORAL_SERVER_URL", "https://coral.pushcollective.club/sse")
    
    # Test connection to Coral server
    if not test_coral_connection(coral_url):
        logger.error("Failed to connect to Coral server. Exiting.")
        return
    
    # Test agent registration
    agent_did = test_agent_registration(coral_url)
    if not agent_did:
        logger.error("Failed to register test agent. Exiting.")
        return
    
    # Test listing agents
    if not test_list_agents(coral_url):
        logger.warning("Angus agent is not registered with the Coral server.")
        logger.info("Please make sure the Angus Coral Agent is running.")
    
    logger.info("Tests completed")

if __name__ == "__main__":
    main()
