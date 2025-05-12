#!/usr/bin/env python3
"""
Agent-Based Communication with Yona

This script uses the LangChain agent-based approach to communicate with Yona.
It connects to the Coral Protocol server, gets the available tools,
creates an agent with those tools, and uses the agent to interact with Yona.
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
        logging.FileHandler('agent_yona_communication.log')
    ]
)
logger = logging.getLogger(__name__)

# Import required packages
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:
    logger.error("langchain_mcp_adapters is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain_mcp_adapters==0.0.10"])
    from langchain_mcp_adapters.client import MultiServerMCPClient

try:
    from langchain.prompts import ChatPromptTemplate
    from langchain.chat_models import init_chat_model
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    logger.error("langchain packages are not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain>=0.0.335 langchain-openai>=0.0.2"])
    from langchain.prompts import ChatPromptTemplate
    from langchain.chat_models import init_chat_model
    from langchain.agents import create_tool_calling_agent, AgentExecutor

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
    parser = argparse.ArgumentParser(description='Agent-Based Communication with Yona')
    
    parser.add_argument(
        '--server-url',
        type=str,
        default=os.environ.get('CORAL_SERVER_URL', 'http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse'),
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
        help='ID of the Yona agent to look for'
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
        default=300,
        help='Timeout for operations in seconds'
    )
    
    parser.add_argument(
        '--wait-for-agents',
        type=int,
        default=2,
        help='Number of agents to wait for'
    )
    
    parser.add_argument(
        '--openai-api-key',
        type=str,
        default=os.environ.get('OPENAI_API_KEY', ''),
        help='OpenAI API key for the agent'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o-mini',
        help='OpenAI model to use for the agent'
    )
    
    return parser.parse_args()

async def main():
    """
    Main entry point for the script.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Check if OpenAI API key is provided
    if not args.openai_api_key:
        logger.error("OpenAI API key is required. Please provide it using --openai-api-key or set the OPENAI_API_KEY environment variable.")
        return 1
    
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
            logger.info("Connected to Coral Protocol server")
            
            # Get tools from the client
            tools = client.get_tools()
            logger.info(f"Retrieved {len(tools)} tools")
            
            # Print the available tools
            for tool in tools:
                logger.info(f"Tool: {tool.name}, Description: {tool.description}")
            
            # Create a prompt for the agent
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    f"""You are Angus, a music analysis agent that can analyze songs and provide feedback.
                    
                    Your task is to:
                    1. List all connected agents using the list_agents tool
                    2. Find the Yona agent (ID containing '{args.yona_id}')
                    3. Create a thread with Yona using the create_thread tool
                    4. Send a message to Yona asking to create a song with the prompt: '{args.prompt}'
                    5. Wait for a response using the wait_for_mentions tool
                    6. Report the result
                    
                    Be thorough and detailed in your approach. If you encounter any errors, try to troubleshoot them.
                    """
                ),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Initialize the model
            model = init_chat_model(
                model=args.model,
                model_provider="openai",
                api_key=args.openai_api_key,
                temperature=0.3,
                max_tokens=16000
            )
            
            # Create the agent
            agent = create_tool_calling_agent(model, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            
            # Run the agent
            logger.info("Running the agent...")
            result = await agent_executor.ainvoke({})
            
            logger.info(f"Agent execution completed: {result}")
            
            return 0
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    asyncio.run(main())
