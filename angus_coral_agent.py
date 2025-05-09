#!/usr/bin/env python3
"""
Angus Coral Agent - Main Script

This script is the main entry point for the Angus Coral agent.
It initializes the Angus agent and connects it to the Coral Protocol server.
"""
import os
import sys
import logging
import argparse
from typing import Dict, Any, Optional

from angus_agent import AngusAgent
from angus_coral_adapter import AngusCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('angus_coral.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Angus Coral Agent')
    
    parser.add_argument(
        '--server-url',
        type=str,
        default=os.environ.get('CORAL_SERVER_URL', 'http://localhost:3001/devmode/default-app/default-key/session1/sse'),
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
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5002,
        help='Port to bind to'
    )
    
    parser.add_argument(
        '--test',
        choices=['connection', 'server', 'discover', 'call'],
        default=None,
        help='Test to run'
    )
    
    return parser.parse_args()

def test_connection(adapter: AngusCoralAdapter) -> bool:
    """
    Test the connection to the Coral Protocol server.
    
    Args:
        adapter: Angus Coral adapter
        
    Returns:
        True if the connection was successful, False otherwise
    """
    logger.info("Testing connection to Coral Protocol server")
    
    # Register with the Coral Protocol server
    success = adapter.register_with_coral_server()
    
    if success:
        logger.info("Connection test successful")
    else:
        logger.error("Connection test failed")
    
    return success

def test_discover(adapter: AngusCoralAdapter) -> bool:
    """
    Test discovering agents on the Coral Protocol server.
    
    Args:
        adapter: Angus Coral adapter
        
    Returns:
        True if the test was successful, False otherwise
    """
    logger.info("Testing discovering agents on Coral Protocol server")
    
    # Register with the Coral Protocol server
    success = adapter.register_with_coral_server()
    if not success:
        logger.error("Failed to register with Coral Protocol server")
        return False
    
    # Discover agents
    agents = adapter.discover_agents()
    
    if agents:
        logger.info(f"Discovered {len(agents)} agents:")
        for agent in agents:
            logger.info(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
        return True
    else:
        logger.error("Failed to discover agents")
        return False

def test_call(adapter: AngusCoralAdapter, agent_did: str = None) -> bool:
    """
    Test calling a function on an agent on the Coral Protocol server.
    
    Args:
        adapter: Angus Coral adapter
        agent_did: DID of the agent to call
        
    Returns:
        True if the test was successful, False otherwise
    """
    logger.info("Testing calling a function on an agent on Coral Protocol server")
    
    # Register with the Coral Protocol server
    success = adapter.register_with_coral_server()
    if not success:
        logger.error("Failed to register with Coral Protocol server")
        return False
    
    # Discover agents if no agent DID is provided
    if not agent_did:
        agents = adapter.discover_agents()
        if not agents:
            logger.error("Failed to discover agents")
            return False
        
        # Use the first agent that is not us
        our_did = adapter.did_manager.did
        for agent in agents:
            agent_did = agent.get('did')
            if agent_did and agent_did != our_did:
                break
        else:
            logger.error("No other agents found")
            return False
    
    # Get agent capabilities
    capabilities = adapter.get_agent_capabilities(agent_did)
    if not capabilities:
        logger.error(f"Failed to get capabilities for agent {agent_did}")
        return False
    
    logger.info(f"Agent capabilities: {capabilities}")
    
    # Call a function on the agent
    result = adapter.call_agent(agent_did, "example_function", param1="test")
    
    if result:
        logger.info(f"Function call result: {result}")
        return True
    else:
        logger.error("Failed to call function")
        return False

def run_server(adapter: AngusCoralAdapter, host: str, port: int):
    """
    Run the Coral server for the Angus agent.
    
    Args:
        adapter: Angus Coral adapter
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Running Coral server for Angus agent on {host}:{port}")
    
    # Start the server
    adapter.start_server(host=host, port=port)

def main():
    """
    Main entry point for the Angus Coral agent.
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
        
        # Initialize Coral adapter
        logger.info(f"Initializing Coral adapter with server URL: {args.server_url}")
        print(f"DEBUG: Using Coral server URL: {args.server_url}")
        coral_adapter = AngusCoralAdapter(
            angus_agent=angus_agent,
            coral_server_url=args.server_url,
            openai_api_key=args.openai_api_key,
            did_domain=args.did_domain,
            private_key_path=args.private_key_path
        )
        
        # Run the specified test or start the server
        if args.test == 'connection':
            test_connection(coral_adapter)
        elif args.test == 'discover':
            test_discover(coral_adapter)
        elif args.test == 'call':
            test_call(coral_adapter)
        elif args.test == 'server':
            run_server(coral_adapter, args.host, args.port)
        else:
            # Default: run the server
            run_server(coral_adapter, args.host, args.port)
    
    except Exception as e:
        logger.error(f"Error running Angus Coral Agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
