#!/usr/bin/env python
"""
Test script for the Coral Protocol LangChain integration with Angus.

This script demonstrates how to use the AngusCoralLangChainAdapter to connect
Angus to a Coral Protocol server using LangChain.
"""
import os
import json
import logging
import argparse
from pprint import pprint

from angus_coral_langchain_adapter import AngusCoralLangChainAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_coral_connection(coral_server_url):
    """
    Test the connection to a Coral Protocol server.
    
    Args:
        coral_server_url: URL of the Coral server
    """
    print(f"\n=== Testing Coral Protocol Connection to {coral_server_url} ===\n")
    
    try:
        # Initialize Coral adapter
        coral_adapter = AngusCoralLangChainAdapter(
            coral_server_url=coral_server_url
        )
        
        # Register with Coral server
        success = coral_adapter.register_with_coral_server()
        
        if success:
            print("Successfully registered with Coral server")
        else:
            print("Failed to register with Coral server")
            return False
        
        # Discover agents
        print("\nDiscovering agents on Coral server...")
        agents = coral_adapter.discover_agents()
        
        if agents:
            print(f"Discovered {len(agents)} agents:")
            for agent in agents:
                print(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
        else:
            print("No agents discovered")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Coral connection: {str(e)}")
        return False

def test_agent_capabilities(coral_server_url, agent_did):
    """
    Test getting the capabilities of an agent.
    
    Args:
        coral_server_url: URL of the Coral server
        agent_did: DID of the agent to get capabilities for
    """
    print(f"\n=== Testing Agent Capabilities for {agent_did} ===\n")
    
    try:
        # Initialize Coral adapter
        coral_adapter = AngusCoralLangChainAdapter(
            coral_server_url=coral_server_url
        )
        
        # Get agent capabilities
        print(f"Getting capabilities for agent {agent_did}...")
        capabilities = coral_adapter.get_agent_capabilities(agent_did)
        
        if capabilities:
            print("Agent capabilities:")
            pprint(capabilities)
        else:
            print("Failed to get agent capabilities")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error testing agent capabilities: {str(e)}")
        return False

def test_agent_call(coral_server_url, agent_did, function_name, **kwargs):
    """
    Test calling a function on another agent.
    
    Args:
        coral_server_url: URL of the Coral server
        agent_did: DID of the agent to call
        function_name: Name of the function to call
        **kwargs: Arguments to pass to the function
    """
    print(f"\n=== Testing Agent Call to {agent_did}.{function_name} ===\n")
    
    try:
        # Initialize Coral adapter
        coral_adapter = AngusCoralLangChainAdapter(
            coral_server_url=coral_server_url
        )
        
        # Call the function
        print(f"Calling {function_name} on agent {agent_did}...")
        result = coral_adapter.call_agent(
            agent_did=agent_did,
            function_name=function_name,
            **kwargs
        )
        
        if result:
            print("Function call result:")
            pprint(result)
        else:
            print("Failed to call function")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error calling agent function: {str(e)}")
        return False

def start_coral_server(coral_server_url, host='0.0.0.0', port=5001):
    """
    Start a Coral server to listen for requests.
    
    Args:
        coral_server_url: URL of the Coral server
        host: Host to bind to
        port: Port to bind to
    """
    print(f"\n=== Starting Coral Server on {host}:{port} ===\n")
    
    try:
        # Initialize Coral adapter
        coral_adapter = AngusCoralLangChainAdapter(
            coral_server_url=coral_server_url
        )
        
        # Start the server
        print(f"Starting Coral server on {host}:{port}...")
        coral_adapter.start_server(host=host, port=port)
        
        print("Coral server started. Press Ctrl+C to stop.")
        
        # Keep the server running until interrupted
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping Coral server...")
        
        return True
    except Exception as e:
        logger.error(f"Error starting Coral server: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test Coral Protocol LangChain integration with Angus')
    
    # Add arguments
    parser.add_argument('--server-url', type=str, default='http://coral.pushcollective.club/sse',
                        help='URL of the Coral server')
    parser.add_argument('--test', type=str, choices=['connection', 'capabilities', 'call', 'server'],
                        default='connection', help='Test to run')
    parser.add_argument('--agent-did', type=str, help='DID of the agent to interact with')
    parser.add_argument('--function', type=str, help='Function to call on the agent')
    parser.add_argument('--args', type=str, help='JSON string of arguments to pass to the function')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind server to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind server to')
    
    args = parser.parse_args()
    
    # Run the specified test
    if args.test == 'connection':
        success = test_coral_connection(args.server_url)
    elif args.test == 'capabilities':
        if not args.agent_did:
            parser.error("--agent-did is required for capabilities test")
        success = test_agent_capabilities(args.server_url, args.agent_did)
    elif args.test == 'call':
        if not args.agent_did or not args.function:
            parser.error("--agent-did and --function are required for call test")
        
        # Parse function arguments
        kwargs = {}
        if args.args:
            try:
                kwargs = json.loads(args.args)
            except json.JSONDecodeError:
                parser.error("--args must be a valid JSON string")
        
        success = test_agent_call(args.server_url, args.agent_did, args.function, **kwargs)
    elif args.test == 'server':
        success = start_coral_server(args.server_url, args.host, args.port)
    else:
        parser.error(f"Unknown test: {args.test}")
    
    # Print result
    if success:
        print("\nTest completed successfully")
        return 0
    else:
        print("\nTest failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
