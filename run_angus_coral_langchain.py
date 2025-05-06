#!/usr/bin/env python
"""
Run script for the Coral Protocol LangChain integration with Angus.

This script starts Agent Angus with the Coral Protocol LangChain integration,
allowing it to share its tools with other agents and use tools from other agents.
"""
import os
import logging
import argparse
import time

from angus_coral_langchain_adapter import AngusCoralLangChainAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_angus_coral_server(coral_server_url, host='0.0.0.0', port=5001, discover=True):
    """
    Run Agent Angus with Coral Protocol LangChain integration.
    
    Args:
        coral_server_url: URL of the Coral server
        host: Host to bind to
        port: Port to bind to
        discover: Whether to discover other agents on startup
    """
    try:
        logger.info(f"Starting Agent Angus with Coral Protocol LangChain integration")
        logger.info(f"Coral server URL: {coral_server_url}")
        logger.info(f"Binding to {host}:{port}")
        
        # Initialize Coral adapter
        coral_adapter = AngusCoralLangChainAdapter(
            coral_server_url=coral_server_url
        )
        
        # Register with Coral server
        success = coral_adapter.register_with_coral_server()
        
        if success:
            logger.info("Successfully registered with Coral server")
        else:
            logger.error("Failed to register with Coral server")
            return False
        
        # Discover agents if requested
        if discover:
            logger.info("Discovering agents on Coral server...")
            agents = coral_adapter.discover_agents()
            
            if agents:
                logger.info(f"Discovered {len(agents)} agents:")
                for agent in agents:
                    logger.info(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
            else:
                logger.info("No agents discovered")
        
        # Start the server
        logger.info(f"Starting Coral server on {host}:{port}...")
        coral_adapter.start_server(host=host, port=port)
        
        logger.info("Coral server started. Press Ctrl+C to stop.")
        
        # Keep the server running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping Coral server...")
        
        return True
    except Exception as e:
        logger.error(f"Error running Angus Coral server: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run Agent Angus with Coral Protocol LangChain integration')
    
    # Add arguments
    parser.add_argument('--server-url', type=str, default='http://coral.pushcollective.club/sse',
                        help='URL of the Coral server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind server to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind server to')
    parser.add_argument('--no-discover', action='store_true', help='Disable agent discovery on startup')
    
    args = parser.parse_args()
    
    # Run the Angus Coral server
    success = run_angus_coral_server(
        coral_server_url=args.server_url,
        host=args.host,
        port=args.port,
        discover=not args.no_discover
    )
    
    # Print result
    if success:
        logger.info("Angus Coral server stopped successfully")
        return 0
    else:
        logger.error("Angus Coral server failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
