#!/usr/bin/env python3
"""
Run Coral Protocol Integration Test

This script runs a test of the Coral Protocol integration with Agent Angus.
It verifies that the integration is working correctly by running a simple test.
"""
import os
import sys
import logging
import asyncio
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

# Import CrewAI components
try:
    from crewai import Agent, Task, Crew
    logger.info("Successfully imported CrewAI components")
except ImportError as e:
    logger.error(f"Failed to import CrewAI components: {str(e)}")
    raise

async def run_test():
    """Run a test of the Coral Protocol integration."""
    logger.info("Running Coral Protocol integration test...")
    
    # Get the server URL from environment variables or use default
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse")
    
    # Create the Coral MCP Server
    coral_server = CoralMCPServer(server_url=server_url)
    
    try:
        # Initialize the server
        await coral_server.initialize()
        logger.info("✅ Successfully initialized Coral MCP Server")
        
        # Create a test agent
        agent = coral_server.create_crewai_agent(
            role="Test Agent",
            goal="Test the Coral Protocol integration",
            backstory="You are a test agent that verifies the Coral Protocol integration is working correctly."
        )
        
        # Create a test task
        task = Task(
            description="Test the Coral Protocol integration by listing available agents.",
            agent=agent,
            expected_output="A list of available agents registered with the Coral Protocol."
        )
        
        # Create a crew with the test agent and task
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        # Run the crew
        logger.info("Running test crew...")
        result = crew.kickoff()
        
        logger.info(f"Test result: {result}")
        logger.info("✅ Coral Protocol integration test completed successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Coral Protocol integration test failed: {str(e)}")
        return False

def main():
    """Main function to run the Coral Protocol integration test."""
    logger.info("Starting Coral Protocol integration test...")
    
    # Check if the Coral server URL is set
    server_url = os.getenv("CORAL_SERVER_URL")
    if not server_url:
        logger.warning("CORAL_SERVER_URL environment variable is not set.")
        logger.warning("Using default URL: http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse")
        logger.warning("Make sure the Coral Protocol server is running.")
    
    # Run the test
    success = asyncio.run(run_test())
    
    if success:
        logger.info("✅ Coral Protocol integration test passed")
        sys.exit(0)
    else:
        logger.error("❌ Coral Protocol integration test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
