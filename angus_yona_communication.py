#!/usr/bin/env python3
"""
Angus-Yona Communication over Coral Protocol

This script implements communication between Angus and Yona using the Coral Protocol.
It follows the best practices recommended by the Coral server team, including:
- Direct tool invocation approach
- Standardized message format
- Error handling and reconnection logic
- Heartbeat mechanism
- Correlation IDs for tracking requests and responses
"""
import os
import sys
import json
import uuid
import asyncio
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('angus_yona_communication.log')
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

try:
    import aiohttp
except ImportError:
    logger.error("aiohttp is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp>=3.8.5"])
    import aiohttp

class AngusYonaCommunicator:
    """
    Class for handling communication between Angus and Yona over the Coral Protocol.
    """
    def __init__(self, server_url: str, agent_id: str, target_agent_id: str, 
                 session_id: str = "session1", timeout: int = 300, wait_for_agents: int = 2):
        """
        Initialize the communicator.
        
        Args:
            server_url: Base URL of the Coral Protocol server
            agent_id: ID of this agent (Angus)
            target_agent_id: ID of the target agent (Yona)
            session_id: Session ID for the Coral Protocol server
            timeout: Timeout for operations in seconds
            wait_for_agents: Number of agents to wait for
        """
        self.base_server_url = server_url
        self.agent_id = agent_id
        self.target_agent_id = target_agent_id
        self.session_id = session_id
        self.timeout = timeout
        self.wait_for_agents = wait_for_agents
        self.client = None
        self.thread_id = None
        self.heartbeat_task = None
        self.connected = False
    
    async def connect(self, agent_description: str = "Angus is a music analysis agent that can analyze songs and provide feedback"):
        """
        Connect to the Coral Protocol server.
        
        Args:
            agent_description: Description of this agent
            
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Construct the SSE URL with agent parameters
            params = {
                "agentId": self.agent_id,
                "waitForAgents": self.wait_for_agents,
                "agentDescription": agent_description
            }
            query_string = urllib.parse.urlencode(params)
            server_url = f"{self.base_server_url}/devmode/exampleApplication/privkey/{self.session_id}/sse?{query_string}"
            
            logger.info(f"Connecting to Coral Protocol server: {server_url}")
            
            # Create the MCP client
            self.client = MultiServerMCPClient(
                connections={
                    "coral": {
                        "transport": "sse",
                        "url": server_url,
                        "timeout": self.timeout,
                        "sse_read_timeout": self.timeout,
                    }
                }
            )
            await self.client.__aenter__()
            logger.info("Connected to Coral Protocol server")
            
            # Start the heartbeat task
            self.heartbeat_task = asyncio.create_task(self.heartbeat())
            self.connected = True
            
            return True
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False
    
    async def disconnect(self):
        """
        Disconnect from the Coral Protocol server.
        """
        try:
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            if self.client:
                await self.client.__aexit__(None, None, None)
                logger.info("Disconnected from Coral Protocol server")
                self.connected = False
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
    
    async def heartbeat(self):
        """
        Send periodic heartbeats to keep the connection alive.
        """
        while True:
            try:
                await asyncio.sleep(60)  # Send heartbeat every 60 seconds
                if self.client and self.connected:
                    # Get the tools from the client
                    tools = self.client.get_tools()
                    
                    # Find the list_agents tool
                    list_agents_tool = None
                    for tool in tools:
                        if tool.name == "list_agents":
                            list_agents_tool = tool
                            break
                    
                    if list_agents_tool:
                        # Call the list_agents tool as a simple heartbeat
                        await list_agents_tool.invoke({})
                        logger.debug("Heartbeat sent")
                    else:
                        logger.warning("list_agents tool not found for heartbeat")
            except asyncio.CancelledError:
                logger.debug("Heartbeat task cancelled")
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
                # Don't break the loop on error, just continue
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agents
        """
        try:
            # Get the tools from the client
            tools = self.client.get_tools()
            
            # Find the list_agents tool
            list_agents_tool = None
            for tool in tools:
                if tool.name == "list_agents":
                    list_agents_tool = tool
                    break
            
            if not list_agents_tool:
                logger.error("list_agents tool not found")
                return []
            
            # Call the list_agents tool
            result = await list_agents_tool.invoke({"includeDetails": True})
            
            # Handle string response
            if isinstance(result, str):
                try:
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
    
    async def find_target_agent(self) -> Optional[Dict[str, Any]]:
        """
        Find the target agent (Yona) in the list of registered agents.
        
        Returns:
            Agent data if found, None otherwise
        """
        agents = await self.list_agents()
        
        for agent in agents:
            agent_id = agent.get("id", "").lower()
            if self.target_agent_id.lower() in agent_id:
                logger.info(f"Found target agent: {agent}")
                return agent
        
        logger.error(f"Target agent '{self.target_agent_id}' not found")
        return None
    
    async def create_thread(self, participants: List[str], metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Create a thread with the specified participants.
        
        Args:
            participants: List of participant agent IDs
            metadata: Thread metadata
            
        Returns:
            Thread ID if successful, None otherwise
        """
        try:
            # Get the tools from the client
            tools = self.client.get_tools()
            
            # Find the create_thread tool
            create_thread_tool = None
            for tool in tools:
                if tool.name == "create_thread":
                    create_thread_tool = tool
                    break
            
            if not create_thread_tool:
                logger.error("create_thread tool not found")
                return None
            
            # Call the create_thread tool
            result = await create_thread_tool.invoke({
                "participants": participants,
                "metadata": metadata or {"purpose": "Angus-Yona communication"}
            })
            
            # Handle string response
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse result as JSON: {result}")
                    return None
            
            # Log the result
            logger.info(f"Created thread: {result}")
            
            # Extract the thread ID
            thread_id = result.get("thread_id")
            self.thread_id = thread_id
            
            return thread_id
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            return None
    
    async def send_message(self, thread_id: str, content: str, mentions: List[str]) -> bool:
        """
        Send a message to a thread.
        
        Args:
            thread_id: ID of the thread
            content: Message content
            mentions: List of agent IDs to mention
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the tools from the client
            tools = self.client.get_tools()
            
            # Find the send_message tool
            send_message_tool = None
            for tool in tools:
                if tool.name == "send_message":
                    send_message_tool = tool
                    break
            
            if not send_message_tool:
                logger.error("send_message tool not found")
                return False
            
            # Call the send_message tool
            result = await send_message_tool.invoke({
                "thread_id": thread_id,
                "content": content,
                "mentions": mentions
            })
            
            # Handle string response
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse result as JSON: {result}")
            
            # Log the result
            logger.info(f"Sent message: {result}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def wait_for_mentions(self, timeout_ms: int = 30000) -> List[Dict[str, Any]]:
        """
        Wait for mentions.
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Returns:
            List of mentions
        """
        try:
            # Get the tools from the client
            tools = self.client.get_tools()
            
            # Find the wait_for_mentions tool
            wait_for_mentions_tool = None
            for tool in tools:
                if tool.name == "wait_for_mentions":
                    wait_for_mentions_tool = tool
                    break
            
            if not wait_for_mentions_tool:
                logger.error("wait_for_mentions tool not found")
                return []
            
            # Call the wait_for_mentions tool
            result = await wait_for_mentions_tool.invoke({
                "timeout_ms": timeout_ms
            })
            
            # Handle string response
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse result as JSON: {result}")
                    return []
            
            # Log the result
            logger.info(f"Received mentions: {result}")
            
            # If result is a list, return it directly
            if isinstance(result, list):
                return result
            # If result is a dictionary with a 'mentions' key, return the mentions
            elif isinstance(result, dict) and 'mentions' in result:
                return result['mentions']
            # Otherwise, return an empty list
            else:
                logger.warning(f"Unexpected result format: {result}")
                return []
        except Exception as e:
            logger.error(f"Error waiting for mentions: {str(e)}")
            return []
    
    async def call_yona_create_song(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Call Yona's create_song function.
        
        Args:
            prompt: Prompt for the song creation
            
        Returns:
            Result of the function call if successful, None otherwise
        """
        try:
            # Check if we have a thread ID
            if not self.thread_id:
                # Find the target agent
                target_agent = await self.find_target_agent()
                if not target_agent:
                    return None
                
                # Create a thread with the target agent
                thread_id = await self.create_thread([self.agent_id, target_agent.get("id")])
                if not thread_id:
                    return None
            
            # Prepare the function call message with the standardized format
            message = {
                "type": "function_call",
                "function": "create_song",
                "arguments": {
                    "prompt": prompt
                },
                "metadata": {
                    "sender": self.agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message_id": str(uuid.uuid4())
                }
            }
            
            # Send the message
            success = await self.send_message(self.thread_id, json.dumps(message), [self.target_agent_id])
            
            if not success:
                logger.error(f"Failed to send function call to Yona")
                return None
            
            # Wait for a response
            mentions = await self.wait_for_mentions(timeout_ms=60000)  # 60 seconds timeout
            
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
                        
                        # Check if it's an error response
                        if response.get("type") == "error":
                            logger.error(f"Error from Yona: {response.get('error')}")
                            return {
                                "error": response.get("error"),
                                "function": response.get("function"),
                                "metadata": response.get("metadata", {})
                            }
                        
                        # Check if it's a function response
                        if response.get("type") == "function_response" and response.get("function") == "create_song":
                            return response.get("result", {})
                        
                        # Handle other response types
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
    parser = argparse.ArgumentParser(description='Angus-Yona Communication over Coral Protocol')
    
    parser.add_argument(
        '--server-url',
        type=str,
        default=os.environ.get('CORAL_SERVER_URL', 'http://coral.pushcollective.club:5555'),
        help='Base URL of the Coral Protocol server'
    )
    
    parser.add_argument(
        '--agent-id',
        type=str,
        default='angus_agent',
        help='ID of this agent (Angus)'
    )
    
    parser.add_argument(
        '--target-agent-id',
        type=str,
        default='yona',
        help='ID of the target agent (Yona)'
    )
    
    parser.add_argument(
        '--session-id',
        type=str,
        default='session1',
        help='Session ID for the Coral Protocol server'
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
    
    args = parser.parse_args()
    
    # Create the communicator
    communicator = AngusYonaCommunicator(
        server_url=args.server_url,
        agent_id=args.agent_id,
        target_agent_id=args.target_agent_id,
        session_id=args.session_id,
        timeout=args.timeout,
        wait_for_agents=args.wait_for_agents
    )
    
    try:
        # Connect to the Coral Protocol server
        connected = await communicator.connect()
        if not connected:
            logger.error("Failed to connect to the Coral Protocol server")
            return 1
        
        # Find the target agent (Yona)
        target_agent = await communicator.find_target_agent()
        if not target_agent:
            logger.error(f"Target agent '{args.target_agent_id}' not found")
            return 1
        
        logger.info(f"Found target agent: {target_agent}")
        
        # Create a thread with the target agent
        thread_id = await communicator.create_thread([args.agent_id, target_agent.get("id")])
        if not thread_id:
            logger.error("Failed to create a thread with the target agent")
            return 1
        
        logger.info(f"Created thread: {thread_id}")
        
        # Call Yona's create_song function
        result = await communicator.call_yona_create_song(args.prompt)
        
        if not result:
            logger.error("Failed to call Yona's create_song function")
            return 1
        
        logger.info(f"Successfully called Yona's create_song function: {result}")
        
        # Print the result in a formatted way
        if isinstance(result, dict):
            print("\n=== Song Created by Yona ===")
            if "title" in result:
                print(f"Title: {result['title']}")
            if "lyrics" in result:
                print(f"\nLyrics:\n{result['lyrics']}")
            if "melody" in result:
                print(f"\nMelody: {result['melody']}")
            if "created_at" in result:
                print(f"\nCreated at: {result['created_at']}")
            print("============================\n")
        else:
            print(f"\n=== Result from Yona ===\n{result}\n=======================\n")
        
        return 0
    except Exception as e:
        logger.error(f"Error running Angus-Yona communication: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Disconnect from the Coral Protocol server
        await communicator.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
