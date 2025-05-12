#!/usr/bin/env python3
"""
MCP Discovery Script for Coral Protocol

This script uses the LangChain MCP adapters to discover agents and get their capabilities.
It connects to the Coral Protocol server using the SSE transport and uses the list_agents tool.
"""
import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Dict, Any, List, Optional
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_discovery.log')
    ]
)
logger = logging.getLogger(__name__)

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:
    logger.error("langchain_mcp_adapters is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain_mcp_adapters==0.0.10"])
    from langchain_mcp_adapters.client import MultiServerMCPClient

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='MCP Discovery for Coral Protocol')
    
    parser.add_argument(
        '--server-url',
        type=str,
        default=os.environ.get('CORAL_SERVER_URL', 'http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse'),
        help='URL of the Coral Protocol server'
    )
    
    parser.add_argument(
        '--agent-id',
        type=str,
        default='discovery_agent',
        help='ID of this agent'
    )
    
    parser.add_argument(
        '--agent-description',
        type=str,
        default='Agent for discovering other agents',
        help='Description of this agent'
    )
    
    parser.add_argument(
        '--wait-for-agents',
        type=int,
        default=2,
        help='Number of agents to wait for'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Timeout for operations in seconds'
    )
    
    parser.add_argument(
        '--yona-id',
        type=str,
        default='yona',
        help='ID of the Yona agent to look for'
    )
    
    return parser.parse_args()

async def list_agents(client) -> List[Dict[str, Any]]:
    """
    List all registered agents.
    
    Args:
        client: MCP client
        
    Returns:
        List of agents
    """
    try:
        # Call the list_agents tool using the connection object
        result = await client.connections["coral"].invoke_tool("list_agents", {})
        
        # Handle string response
        if isinstance(result, str):
            try:
                import json
                result = json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse result as JSON: {result}")
        
        # Log the result
        logger.info(f"Registered agents: {result}")
        
        # If result is a list, return it directly
        if isinstance(result, list):
            return result
        # If result is a dictionary with an 'agents' key, return the agents
        elif isinstance(result, dict) and 'agents' in result:
            return result['agents']
        # Otherwise, return an empty list
        else:
            logger.warning(f"Unexpected result format: {result}")
            return []
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return []

async def get_agent_capabilities(client, agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the capabilities of an agent.
    
    Args:
        client: MCP client
        agent_id: ID of the agent
        
    Returns:
        Agent capabilities if successful, None otherwise
    """
    try:
        # Call the get_agent_capabilities tool using the connection object
        # Note: This tool might not exist in the current version of the Coral Protocol server
        # If it doesn't exist, we'll need to use a different approach
        try:
            result = await client.connections["coral"].invoke_tool("get_agent_capabilities", {
                "agent_id": agent_id
            })
        except Exception as e:
            logger.warning(f"Error calling get_agent_capabilities tool: {str(e)}")
            logger.info("Trying to get capabilities from agent description")
            
            # Get the agent description from the list of agents
            agents = await list_agents(client)
            for agent in agents:
                if agent.get("id") == agent_id:
                    return {
                        "description": agent.get("description", "No description available"),
                        "id": agent_id
                    }
            
            return None
        
        # Handle string response
        if isinstance(result, str):
            try:
                import json
                result = json.loads(result)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse result as JSON: {result}")
                return None
        
        # Log the result
        logger.info(f"Agent capabilities: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error getting agent capabilities: {str(e)}")
        return None

async def main():
    """
    Main entry point for the script.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Construct the SSE URL with agent parameters
    params = {
        "agentId": args.agent_id,
        "waitForAgents": args.wait_for_agents,
        "agentDescription": args.agent_description
    }
    query_string = urllib.parse.urlencode(params)
    server_url = f"{args.server_url}?{query_string}"
    
    logger.info(f"Connecting to Coral Protocol server: {server_url}")
    
    try:
        # Create the MCP client
        async with MultiServerMCPClient(
            connections={
                "coral": {
                    "transport": "sse",
                    "url": server_url,
                    "timeout": args.timeout,
                    "sse_read_timeout": args.timeout,
                }
            }
        ) as client:
            # List all registered agents
            agents = await list_agents(client)
            
            if not agents:
                logger.error("No agents found")
                return 1
            
            logger.info(f"Found {len(agents)} agents:")
            for agent in agents:
                agent_id = agent.get("id", "Unknown")
                agent_description = agent.get("description", "No description")
                logger.info(f"  - {agent_id}: {agent_description}")
            
            # Look for Yona agent
            yona_agent = None
            for agent in agents:
                agent_id = agent.get("id", "").lower()
                if args.yona_id.lower() in agent_id:
                    yona_agent = agent
                    break
            
            if yona_agent:
                logger.info(f"Found Yona agent: {yona_agent.get('id')}")
                
                # Get Yona's capabilities
                capabilities = await get_agent_capabilities(client, yona_agent.get("id"))
                
                if capabilities:
                    logger.info(f"Yona capabilities: {capabilities}")
                else:
                    logger.warning("Could not get Yona capabilities")
            else:
                logger.warning(f"Yona agent not found (looking for ID containing '{args.yona_id}')")
            
            return 0
    except Exception as e:
        logger.error(f"Error running discovery: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    asyncio.run(main())
