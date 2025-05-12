#!/usr/bin/env python3
"""
Improved Test Script for Angus-Yona Communication

This script tests the communication between Angus and Yona agents using the improved
Coral Protocol integration based on the MCP tools approach.
"""
import os
import sys
import json
import uuid
import time
import logging
import argparse
from typing import Dict, Any, Optional, List

from angus_agent import AngusAgent
from angus_coral_adapter import AngusCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_improved_yona_communication.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Test Improved Angus-Yona Communication')
    
    parser.add_argument(
        '--server-url',
        type=str,
        default=os.environ.get('CORAL_SERVER_URL', 'http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse'),
        help='URL of the Coral Protocol server'
    )
    
    parser.add_argument(
        '--openai-api-key',
        type=str,
        default=os.environ.get('OPENAI_API_KEY'),
        help='OpenAI API key'
    )
    
    parser.add_argument(
        '--did-domain',
        type=str,
        default='angus.ai',
        help='Domain for the DID'
    )
    
    parser.add_argument(
        '--private-key-path',
        type=str,
        default=None,
        help='Path to the private key file'
    )
    
    parser.add_argument(
        '--simulation-mode',
        action='store_true',
        help='Run in simulation mode'
    )
    
    parser.add_argument(
        '--test',
        choices=['discover', 'capabilities', 'call', 'all'],
        default='all',
        help='Test to run'
    )
    
    parser.add_argument(
        '--yona-did',
        type=str,
        default=None,
        help='DID of the Yona agent (if known)'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        default='Create a happy K-pop song about friendship between AI agents',
        help='Prompt for the song creation'
    )
    
    parser.add_argument(
        '--agent-description',
        type=str,
        default='Angus is a music analysis agent that can analyze songs and provide feedback',
        help='Description of the Angus agent'
    )
    
    return parser.parse_args()

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

def test_discover_yona(adapter: AngusCoralAdapter) -> Optional[Dict[str, Any]]:
    """
    Test discovering the Yona agent on the Coral Protocol server.
    
    Args:
        adapter: Angus Coral adapter
        
    Returns:
        Yona agent if found, None otherwise
    """
    logger.info("Testing discovering Yona agent on Coral Protocol server")
    
    # Wait for the SSE connection to be established and agents to be discovered
    logger.info("Waiting for SSE connection to be established...")
    time.sleep(5)
    
    # Discover agents
    agents = adapter.discover_agents()
    if not agents:
        logger.error("No agents discovered")
        return None
    
    # Find Yona agent
    yona_agent = find_yona_agent(agents)
    if yona_agent:
        logger.info(f"Found Yona agent: {yona_agent.get('name')} ({yona_agent.get('did')})")
        return yona_agent
    else:
        logger.error("Yona agent not found")
        return None

def test_get_yona_capabilities(adapter: AngusCoralAdapter, yona_did: str) -> Optional[Dict[str, Any]]:
    """
    Test getting the capabilities of the Yona agent.
    
    Args:
        adapter: Angus Coral adapter
        yona_did: DID of the Yona agent
        
    Returns:
        Capabilities of the Yona agent if successful, None otherwise
    """
    logger.info(f"Testing getting capabilities for Yona agent {yona_did}")
    
    # Get agent capabilities
    capabilities = adapter.get_agent_capabilities(yona_did)
    if not capabilities:
        logger.error(f"Failed to get capabilities for Yona agent {yona_did}")
        return None
    
    logger.info(f"Successfully retrieved capabilities for Yona agent {yona_did}")
    
    # Log the capabilities
    if "services" in capabilities:
        logger.info(f"Yona agent provides {len(capabilities['services'])} services:")
        for service in capabilities["services"]:
            logger.info(f"  - {service.get('id')}: {service.get('description', 'No description')}")
    
    return capabilities

def test_call_yona_create_song(adapter: AngusCoralAdapter, yona_did: str, prompt: str) -> Optional[Dict[str, Any]]:
    """
    Test calling the create_song function on the Yona agent.
    
    Args:
        adapter: Angus Coral adapter
        yona_did: DID of the Yona agent
        prompt: Prompt for the song creation
        
    Returns:
        Result of the function call if successful, None otherwise
    """
    logger.info(f"Testing calling create_song function on Yona agent {yona_did}")
    
    # Call the function
    result = adapter.call_agent(
        agent_did=yona_did,
        function_name="create_song",
        prompt=prompt
    )
    
    if not result:
        logger.error(f"Failed to call create_song function on Yona agent {yona_did}")
        return None
    
    logger.info(f"Successfully called create_song function on Yona agent {yona_did}")
    logger.info(f"Result: {result}")
    
    return result

def main():
    """
    Main entry point for the test script.
    """
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Initialize Angus agent
        logger.info("Initializing Angus agent")
        angus_agent = AngusAgent(
            openai_api_key=args.openai_api_key,
            simulation_mode=args.simulation_mode,
            did_domain=args.did_domain,
            private_key_path=args.private_key_path
        )
        
        # Update the capability document with the agent description
        angus_agent.capability_generator.capability_document["description"] = args.agent_description
        
        # Initialize Coral adapter
        logger.info(f"Initializing Coral adapter with server URL: {args.server_url}")
        coral_adapter = AngusCoralAdapter(
            angus_agent=angus_agent,
            coral_server_url=args.server_url,
            openai_api_key=args.openai_api_key,
            did_domain=args.did_domain,
            private_key_path=args.private_key_path
        )
        
        # Register with the Coral Protocol server
        logger.info("Registering with Coral Protocol server")
        success = coral_adapter.register_with_coral_server()
        if not success:
            logger.error("Failed to register with Coral Protocol server")
            return 1
        
        logger.info("Successfully registered with Coral Protocol server")
        
        # Wait for the SSE connection to be established
        logger.info("Waiting for SSE connection to be established...")
        time.sleep(5)
        
        # Run the specified test or all tests
        yona_agent = None
        yona_did = args.yona_did
        
        if args.test == 'discover' or args.test == 'all':
            # Test discovering Yona
            yona_agent = test_discover_yona(coral_adapter)
            if yona_agent and not yona_did:
                yona_did = yona_agent.get('did')
        
        if (args.test == 'capabilities' or args.test == 'all') and yona_did:
            # Test getting Yona's capabilities
            capabilities = test_get_yona_capabilities(coral_adapter, yona_did)
            if not capabilities and args.test == 'capabilities':
                logger.error("Failed to get Yona's capabilities")
                return 1
        
        if (args.test == 'call' or args.test == 'all') and yona_did:
            # Test calling Yona's create_song function
            result = test_call_yona_create_song(coral_adapter, yona_did, args.prompt)
            if not result and args.test == 'call':
                logger.error("Failed to call Yona's create_song function")
                return 1
        
        if args.test == 'all':
            if yona_agent and yona_did:
                logger.info("All tests passed")
            else:
                logger.error("Some tests failed")
                return 1
        
        # Keep the connection open for a while to allow for any responses
        logger.info("Keeping connection open for 10 seconds...")
        time.sleep(10)
        
    except Exception as e:
        logger.error(f"Error running test: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
