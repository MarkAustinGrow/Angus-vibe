#!/usr/bin/env python3
"""
Simple Coral Protocol Connection Test

This script tests basic connectivity to the Coral Protocol server
without complex tool integration.
"""
import os
import sys
import logging
import asyncio
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_coral_connection():
    """Test basic connection to the Coral Protocol server."""
    logger.info("Testing basic connection to Coral Protocol server...")
    
    # Get the server URL from environment variables or use default
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse")
    
    try:
        # Test basic HTTP connection
        async with httpx.AsyncClient() as client:
            # Try to connect to the server
            response = await client.get(server_url, timeout=10.0)
            
            logger.info(f"✅ Successfully connected to Coral server: {server_url}")
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to Coral server: {str(e)}")
        return False

async def test_sse_connection():
    """Test Server-Sent Events connection to the Coral Protocol server."""
    logger.info("Testing SSE connection to Coral Protocol server...")
    
    server_url = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse")
    
    try:
        # Test SSE connection with proper headers
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", server_url, headers=headers, timeout=10.0) as response:
                logger.info(f"✅ SSE connection established: {response.status_code}")
                logger.info(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
                
                # Read a few lines to test the stream
                line_count = 0
                async for line in response.aiter_lines():
                    if line.strip():
                        logger.info(f"Received: {line}")
                        line_count += 1
                        if line_count >= 3:  # Just read a few lines
                            break
                
                logger.info("✅ SSE stream is working")
                return True
                
    except Exception as e:
        logger.error(f"❌ SSE connection failed: {str(e)}")
        return False

async def main():
    """Main function to run all tests."""
    logger.info("Starting Coral Protocol connectivity tests...")
    
    # Test 1: Basic HTTP connection
    http_success = await test_coral_connection()
    
    # Test 2: SSE connection
    sse_success = await test_sse_connection()
    
    if http_success and sse_success:
        logger.info("✅ All Coral Protocol connectivity tests passed!")
        logger.info("🎉 Agent Angus can communicate with Team Yona!")
        return True
    else:
        logger.error("❌ Some connectivity tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
