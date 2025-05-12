#!/usr/bin/env python3
"""
Test Direct Communication with Yona

This script tests direct communication with Yona using the MCP adapters approach.
It connects to the Coral Protocol server, lists all registered agents,
looks for Yona, and attempts to communicate with it.
"""
import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_direct_yona_communication.log')
    ]
)
logger = logging.getLogger(__name__)

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:
    logger.error("langchain_mcp_adapters is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain_mcp_adapters==0.0.11"])
    from langchain_mcp_adapters.client import MultiServerMCPClient

try:
    import aiohttp
except ImportError:
    logger.error("aiohttp is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp>=3.8.5"])
    import aiohttp

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Test Direct Communication with Yona')
    
    parser.add_argument(
        '--server-url',
        type=str,
        default=os.environ.get('CORAL_SERVER_URL', 'http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse'),
        help='URL of the Coral Protocol server'
    )
    
    parser.add_argument(
        '--agent-id',
        type=str,
        default='angus_agent',
        help='ID of this agent'
    )
    
    parser.add_argument(
        '--agent-description',
        type=str,
        default='Angus is a music analysis agent that can analyze songs and provide feedback',
        help='Description of this agent'
    )
    
    parser.add_argument(
        '--yona-id',
        type=str,
        default='yona',
        help='ID of the Yona agent'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        default='Create a happy K-pop song about friendship between AI agents',
        help='Prompt for the song creation'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout for operations in seconds'
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
        # Get the list_agents tool
        list_agents_tool = client.get_tool("coral", "list_agents")
        
        # Call the tool
        result = await list_agents_tool.ainvoke({})
        
        # Log the result
        logger.info(f"Registered agents: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return []

async def create_thread(client, participants: List[str], metadata: Dict[str, Any] = None) -> Optional[str]:
    """
    Create a thread with the specified participants.
    
    Args:
        client: MCP client
        participants: List of participant agent IDs
        metadata: Thread metadata
        
    Returns:
        Thread ID if successful, None otherwise
    """
    try:
        # Get the create_thread tool
        create_thread_tool = client.get_tool("coral", "create_thread")
        
        # Call the tool
        result = await create_thread_tool.ainvoke({
            "participants": participants,
            "metadata": metadata or {"purpose": "test"}
        })
        
        # Log the result
        logger.info(f"Created thread: {result}")
        
        # Extract the thread ID
        thread_id = result.get("thread_id")
        
        return thread_id
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}")
        return None

async def send_message(client, thread_id: str, content: str, mentions: List[str]) -> bool:
    """
    Send a message to a thread.
    
    Args:
        client: MCP client
        thread_id: ID of the thread
        content: Message content
        mentions: List of agent IDs to mention
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the send_message tool
        send_message_tool = client.get_tool("coral", "send_message")
        
        # Call the tool
        result = await send_message_tool.ainvoke({
            "thread_id": thread_id,
            "content": content,
            "mentions": mentions
        })
        
        # Log the result
        logger.info(f"Sent message: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

async def wait_for_mentions(client, timeout: int = 30) -> List[Dict[str, Any]]:
    """
    Wait for mentions.
    
    Args:
        client: MCP client
        timeout: Timeout in seconds
        
    Returns:
        List of mentions
    """
    try:
        # Get the wait_for_mentions tool
        wait_for_mentions_tool = client.get_tool("coral", "wait_for_mentions")
        
        # Call the tool
        result = await wait_for_mentions_tool.ainvoke({
            "timeout": timeout
        })
        
        # Log the result
        logger.info(f"Received mentions: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error waiting for mentions: {str(e)}")
        return []

async def call_yona_create_song(client, thread_id: str, yona_id: str, prompt: str) -> Optional[Dict[str, Any]]:
    """
    Call Yona's create_song function.
    
    Args:
        client: MCP client
        thread_id: ID of the thread
        yona_id: ID of the Yona agent
        prompt: Prompt for the song creation
        
    Returns:
        Result of the function call if successful, None otherwise
    """
    try:
        # Prepare the function call message
        message = {
            "type": "function_call",
            "function": "create_song",
            "arguments": {
                "prompt": prompt
            }
        }
        
        # Send the message
        success = await send_message(client, thread_id, json.dumps(message), [yona_id])
        
        if not success:
            logger.error(f"Failed to send function call to Yona")
            return None
        
        # Wait for a response
        mentions = await wait_for_mentions(client)
        
        if not mentions:
            logger.error(f"No response received from Yona")
            return None
        
        # Parse the response
        for mention in mentions:
            content = mention.get("content")
            if content:
                try:
                    response = json.loads(content)
                    logger.info(f"Received response from Yona: {response}")
                    return response
                except json.JSONDecodeError:
                    logger.info(f"Received non-JSON response from Yona: {content}")
                    return {"response": content}
        
        return None
    except Exception as e:
        logger.error(f"Error calling Yona's create_song function: {str(e)}")
        return None

async def main():
    """
    Main entry point for the script.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Construct the SSE URL with agent parameters
    import urllib.parse
    params = {
        "agentId": args.agent_id,
        "waitForAgents": 2,
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
            
            # Check if Yona is registered
            yona_agent = None
            for agent in agents:
                agent_id = agent.get("id")
                if agent_id and args.yona_id in agent_id.lower():
                    yona_agent = agent
                    break
            
            if not yona_agent:
                logger.error(f"Yona agent not found")
                return 1
            
            logger.info(f"Found Yona agent: {yona_agent}")
            
            # Create a thread with Yona
            thread_id = await create_thread(client, [args.agent_id, yona_agent.get("id")])
            
            if not thread_id:
                logger.error(f"Failed to create thread with Yona")
                return 1
            
            logger.info(f"Created thread with Yona: {thread_id}")
            
            # Call Yona's create_song function
            result = await call_yona_create_song(client, thread_id, yona_agent.get("id"), args.prompt)
            
            if not result:
                logger.error(f"Failed to call Yona's create_song function")
                return 1
            
            logger.info(f"Successfully called Yona's create_song function: {result}")
            
            return 0
    except Exception as e:
        logger.error(f"Error running test: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    asyncio.run(main())
