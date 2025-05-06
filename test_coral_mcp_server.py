#!/usr/bin/env python3
"""
Test script for Coral MCP Server

This script tests the connectivity to the Coral Protocol server and verifies
that the MCP tools are working correctly.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import the Coral MCP Server
try:
    from coral_mcp_server import CoralMCPServer
    logger.info("Successfully imported CoralMCPServer")
except ImportError as e:
    logger.error(f"Failed to import CoralMCPServer: {str(e)}")
    raise

async def test_connection():
    """Test connection to the Coral Protocol server."""
    logger.info("Testing connection to Coral Protocol server...")
    
    # Get the server URL from environment variables or use default
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club/sse")
    
    # Create the Coral MCP Server
    coral_server = CoralMCPServer(server_url=server_url)
    
    try:
        # Connect to the server
        await coral_server.connect()
        logger.info("✅ Successfully connected to Coral Protocol server")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to connect to Coral Protocol server: {str(e)}")
        return False

async def test_agent_registration():
    """Test agent registration with the Coral Protocol server."""
    logger.info("Testing agent registration...")
    
    # Get the server URL from environment variables or use default
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club/sse")
    
    # Create the Coral MCP Server
    coral_server = CoralMCPServer(server_url=server_url)
    
    try:
        # Connect to the server
        await coral_server.connect()
        
        # Get the register agent tool
        register_tool = coral_server.get_register_agent_tool()
        
        # Register a test agent
        result = await register_tool.acoroutine("test_agent", ["testing"])
        
        logger.info(f"Registration result: {result}")
        logger.info("✅ Successfully registered test agent")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to register test agent: {str(e)}")
        return False

async def test_list_agents():
    """Test listing agents from the Coral Protocol server."""
    logger.info("Testing agent listing...")
    
    # Get the server URL from environment variables or use default
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club/sse")
    
    # Create the Coral MCP Server
    coral_server = CoralMCPServer(server_url=server_url)
    
    try:
        # Connect to the server
        await coral_server.connect()
        
        # Get the list agents tool
        list_tool = coral_server.get_list_agents_tool()
        
        # List agents
        result = await list_tool.acoroutine(True)
        
        logger.info(f"Agent list: {result}")
        logger.info("✅ Successfully listed agents")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to list agents: {str(e)}")
        return False

async def test_create_thread():
    """Test creating a thread on the Coral Protocol server."""
    logger.info("Testing thread creation...")
    
    # Get the server URL from environment variables or use default
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club/sse")
    
    # Create the Coral MCP Server
    coral_server = CoralMCPServer(server_url=server_url)
    
    try:
        # Connect to the server
        await coral_server.connect()
        
        # Register a test agent
        register_tool = coral_server.get_register_agent_tool()
        await register_tool.acoroutine("test_agent_1", ["testing"])
        await register_tool.acoroutine("test_agent_2", ["testing"])
        
        # Get the create thread tool
        thread_tool = coral_server.get_create_thread_tool()
        
        # Create a thread
        result = await thread_tool.acoroutine(
            participants=["test_agent_1", "test_agent_2"],
            initial_message="Hello from test_agent_1"
        )
        
        logger.info(f"Thread creation result: {result}")
        logger.info("✅ Successfully created thread")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create thread: {str(e)}")
        return False

async def test_send_message():
    """Test sending a message on the Coral Protocol server."""
    logger.info("Testing message sending...")
    
    # Get the server URL from environment variables or use default
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club/sse")
    
    # Create the Coral MCP Server
    coral_server = CoralMCPServer(server_url=server_url)
    
    try:
        # Connect to the server
        await coral_server.connect()
        
        # Register test agents
        register_tool = coral_server.get_register_agent_tool()
        await register_tool.acoroutine("sender_agent", ["testing"])
        await register_tool.acoroutine("receiver_agent", ["testing"])
        
        # Create a thread
        thread_tool = coral_server.get_create_thread_tool()
        thread_result = await thread_tool.acoroutine(
            participants=["sender_agent", "receiver_agent"],
            initial_message="Thread created for testing"
        )
        
        # Extract thread ID from result
        import re
        thread_id_match = re.search(r"thread ([a-zA-Z0-9-]+)", thread_result)
        if not thread_id_match:
            logger.error("❌ Failed to extract thread ID from result")
            return False
            
        thread_id = thread_id_match.group(1)
        
        # Get the send message tool
        message_tool = coral_server.get_send_message_tool()
        
        # Send a message
        result = await message_tool.acoroutine(
            recipient="receiver_agent",
            content="Hello from sender_agent",
            thread_id=thread_id
        )
        
        logger.info(f"Message sending result: {result}")
        logger.info("✅ Successfully sent message")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send message: {str(e)}")
        return False

async def run_all_tests():
    """Run all tests for the Coral MCP Server."""
    logger.info("Running all Coral MCP Server tests...")
    
    # Test connection
    connection_result = await test_connection()
    
    if not connection_result:
        logger.error("❌ Connection test failed. Skipping remaining tests.")
        return False
    
    # Test agent registration
    registration_result = await test_agent_registration()
    
    if not registration_result:
        logger.error("❌ Agent registration test failed. Skipping remaining tests.")
        return False
    
    # Test listing agents
    list_result = await test_list_agents()
    
    if not list_result:
        logger.error("❌ Agent listing test failed. Skipping remaining tests.")
        return False
    
    # Test creating a thread
    thread_result = await test_create_thread()
    
    if not thread_result:
        logger.error("❌ Thread creation test failed. Skipping remaining tests.")
        return False
    
    # Test sending a message
    message_result = await test_send_message()
    
    if not message_result:
        logger.error("❌ Message sending test failed.")
        return False
    
    logger.info("✅ All tests passed successfully!")
    return True

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_all_tests())
