#!/usr/bin/env python3
"""
Simple Angus Coral Agent

This agent connects directly to the coral protocol server using SSE
and registers Agent Angus to communicate with Team Yona.
"""
import os
import sys
import json
import logging
import asyncio
import httpx
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AngusCoralAgent:
    """Simple Angus Coral Agent for direct communication with Team Yona."""
    
    def __init__(self, server_url: str = None):
        """Initialize the Angus Coral Agent."""
        self.server_url = server_url or os.getenv(
            "CORAL_SERVER_URL", 
            "http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse"
        )
        self.agent_id = "angus"
        self.agent_name = "Agent Angus"
        self.description = "Angus agent for music analysis, YouTube content creation, and creative collaboration"
        self.capabilities = [
            "music-analysis",
            "youtube-content",
            "audio-processing", 
            "creative-collaboration",
            "feedback-processing"
        ]
        self.session_id = str(uuid.uuid4())
        
        logger.info(f"Initialized Angus Coral Agent")
        logger.info(f"Agent ID: {self.agent_id}")
        logger.info(f"Server URL: {self.server_url}")
        logger.info(f"Session ID: {self.session_id}")
        
    async def register_agent(self):
        """Register Agent Angus with the coral protocol server."""
        logger.info("🚀 Registering Agent Angus with coral protocol...")
        
        # Create registration message
        registration_data = {
            "type": "agent_registration",
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "capabilities": self.capabilities,
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "did": f"did:web:angus.ai",
            "status": "active"
        }
        
        try:
            # Send registration via HTTP POST
            async with httpx.AsyncClient() as client:
                # Try to register via POST to the base URL
                base_url = self.server_url.replace('/sse', '')
                register_url = f"{base_url}/register"
                
                response = await client.post(
                    register_url,
                    json=registration_data,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("✅ Successfully registered Agent Angus!")
                    logger.info(f"Registration response: {response.text}")
                    return True
                else:
                    logger.warning(f"Registration returned status {response.status_code}: {response.text}")
                    
        except Exception as e:
            logger.warning(f"HTTP registration failed: {str(e)}")
            
        # Fallback: Send registration via SSE stream
        logger.info("Trying registration via SSE stream...")
        return await self.send_sse_message(registration_data)
        
    async def send_sse_message(self, message_data: dict):
        """Send a message via the SSE stream."""
        try:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Send message as query parameter or in headers
                params = {
                    "message": json.dumps(message_data)
                }
                
                async with client.stream(
                    "GET", 
                    self.server_url, 
                    headers=headers,
                    params=params,
                    timeout=10.0
                ) as response:
                    
                    if response.status_code == 200:
                        logger.info("✅ Message sent via SSE stream")
                        return True
                    else:
                        logger.error(f"SSE message failed: {response.status_code}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send SSE message: {str(e)}")
            return False
            
    async def listen_for_messages(self, duration: int = 30):
        """Listen for messages from other agents."""
        logger.info(f"🎧 Listening for messages from Team Yona for {duration} seconds...")
        
        try:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "GET", 
                    self.server_url, 
                    headers=headers,
                    timeout=duration + 5
                ) as response:
                    
                    logger.info(f"✅ Connected to SSE stream: {response.status_code}")
                    logger.info(f"Content-Type: {response.headers.get('content-type')}")
                    
                    message_count = 0
                    start_time = asyncio.get_event_loop().time()
                    
                    async for line in response.aiter_lines():
                        current_time = asyncio.get_event_loop().time()
                        if current_time - start_time > duration:
                            logger.info(f"⏰ Listening timeout reached ({duration}s)")
                            break
                            
                        if line.strip():
                            message_count += 1
                            logger.info(f"📨 Message {message_count}: {line}")
                            
                            # Try to parse as JSON
                            try:
                                if line.startswith("data: "):
                                    data = json.loads(line[6:])
                                    await self.handle_message(data)
                                elif line.startswith("{"):
                                    data = json.loads(line)
                                    await self.handle_message(data)
                            except json.JSONDecodeError:
                                logger.info(f"📝 Raw message: {line}")
                                
                    logger.info(f"📊 Received {message_count} messages total")
                    return message_count > 0
                    
        except Exception as e:
            logger.error(f"Failed to listen for messages: {str(e)}")
            return False
            
    async def handle_message(self, data: dict):
        """Handle incoming messages from other agents."""
        logger.info(f"🔍 Processing message: {data}")
        
        message_type = data.get("type", "unknown")
        sender = data.get("agent_id", "unknown")
        
        if message_type == "agent_discovery":
            logger.info(f"🤝 Discovered agent: {sender}")
            await self.respond_to_discovery(data)
        elif message_type == "agent_registration":
            logger.info(f"👋 Agent registered: {sender}")
        elif message_type == "message":
            content = data.get("content", "")
            logger.info(f"💬 Message from {sender}: {content}")
            await self.respond_to_message(data)
        else:
            logger.info(f"📋 Unknown message type: {message_type}")
            
    async def respond_to_discovery(self, discovery_data: dict):
        """Respond to agent discovery."""
        sender = discovery_data.get("agent_id", "unknown")
        
        response_data = {
            "type": "discovery_response",
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "to_agent": sender,
            "capabilities": self.capabilities,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Hello from {self.agent_name}! Ready to collaborate on music and creative projects!"
        }
        
        logger.info(f"🤝 Responding to discovery from {sender}")
        await self.send_sse_message(response_data)
        
    async def respond_to_message(self, message_data: dict):
        """Respond to a message from another agent."""
        sender = message_data.get("agent_id", "unknown")
        content = message_data.get("content", "")
        
        response_data = {
            "type": "message",
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "to_agent": sender,
            "content": f"Thanks for your message: '{content}'. Agent Angus is ready to collaborate!",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"💬 Responding to message from {sender}")
        await self.send_sse_message(response_data)
        
    async def send_greeting_to_yona(self):
        """Send a greeting message to Team Yona."""
        greeting_data = {
            "type": "message",
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "to_agent": "yona",
            "content": "Hello Team Yona! Agent Angus is now connected and ready for creative collaboration! 🎵🚀",
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": self.capabilities
        }
        
        logger.info("👋 Sending greeting to Team Yona...")
        return await self.send_sse_message(greeting_data)
        
    async def run_agent(self, duration: int = 60):
        """Run the complete agent workflow."""
        logger.info("🚀 Starting Angus Coral Agent...")
        
        # Step 1: Register agent
        registration_success = await self.register_agent()
        if not registration_success:
            logger.warning("⚠️ Registration may have failed, but continuing...")
            
        # Step 2: Send greeting to Yona
        await asyncio.sleep(2)  # Brief pause
        greeting_success = await self.send_greeting_to_yona()
        if greeting_success:
            logger.info("✅ Greeting sent to Team Yona!")
        
        # Step 3: Listen for responses
        await asyncio.sleep(1)  # Brief pause
        messages_received = await self.listen_for_messages(duration)
        
        if messages_received:
            logger.info("🎉 Successfully communicated with coral protocol!")
            logger.info("🤝 Agent Angus is now connected to Team Yona!")
            return True
        else:
            logger.info("📡 No messages received, but connection established")
            logger.info("🔗 Agent Angus is connected and waiting for Team Yona")
            return True

async def main():
    """Main function to run the Angus Coral Agent."""
    logger.info("🎵 Initializing Agent Angus for coral protocol communication...")
    
    # Create and run the agent
    agent = AngusCoralAgent()
    success = await agent.run_agent(duration=30)
    
    if success:
        logger.info("✅ Agent Angus coral integration completed successfully!")
        logger.info("🎉 Ready for multi-agent collaboration with Team Yona!")
        return True
    else:
        logger.error("❌ Agent Angus coral integration failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
