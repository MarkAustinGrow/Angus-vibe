#!/usr/bin/env python3
"""
Coral MCP Server for Agent Angus

This module implements the Model Context Protocol (MCP) server for Coral Protocol integration.
It provides tools for agent communication, registration, and discovery.
"""
import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import LangChain components for MCP
try:
    from langchain_core.tools import Tool
    from langchain_core.callbacks import CallbackManagerForToolRun
    from langchain_mcp_adapters.client import MultiServerMCPClient
    logger.info("Successfully imported LangChain MCP components")
except ImportError as e:
    logger.error(f"Failed to import LangChain MCP components: {str(e)}")
    logger.error("Please install the required dependencies: pip install langchain langchain-core langchain-mcp-adapters")
    raise

# Import CrewAI components
try:
    from crewai import Agent, Task, Crew
    logger.info("Successfully imported CrewAI components")
except ImportError as e:
    logger.error(f"Failed to import CrewAI components: {str(e)}")
    logger.error("Please install the required dependencies: pip install crewai")
    raise

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Default Coral server URL
DEFAULT_CORAL_SERVER_URL = os.getenv("CORAL_SERVER_URL", "http://coral.pushcollective.club:5555/devmode/app/priv/session1/sse")

class CoralMCPServer:
    """
    Model Context Protocol (MCP) server for Coral Protocol integration.
    
    This class provides tools for agent communication, registration, and discovery
    using the Coral Protocol through the LangChain MCP interface.
    """
    
    def __init__(self, server_url: str = DEFAULT_CORAL_SERVER_URL):
        """
        Initialize the Coral MCP Server.
        
        Args:
            server_url: URL of the Coral Protocol server
        """
        self.server_url = server_url
        self.client = None
        self.agent_name = os.getenv("AGENT_NAME", "angus_agent")
        self.tools = []
        
        logger.info(f"Initialized Coral MCP Server with URL: {self.server_url}")
        
    async def connect(self) -> None:
        """
        Connect to the Coral Protocol server.
        
        Returns:
            None
        """
        try:
            # Configure the MCP client with Coral server connection
            self.client = MultiServerMCPClient(
                connections={
                    "coral": {
                        "transport": "sse",
                        "url": self.server_url,
                        "timeout": 5,
                        "sse_read_timeout": 60,  # Reduced timeout
                        "headers": {
                            "Accept": "text/event-stream"
                        }
                    }
                }
            )
            
            logger.info(f"Connected to MCP server at {self.server_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Coral server: {str(e)}")
            raise
            
    def get_register_agent_tool(self) -> Tool:
        """
        Get a tool for registering an agent with the Coral Protocol.
        
        Returns:
            Tool: A LangChain tool for agent registration
        """
        async def _register_agent(
            agent_name: str,
            capabilities: List[str] = None,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
            """Register an agent with the Coral Protocol."""
            if self.client is None:
                await self.connect()
                
            capabilities = capabilities or []
            
            try:
                # Register the agent with the Coral server
                response = await self.client.register_agent(
                    agent_name=agent_name,
                    capabilities=capabilities
                )
                
                return f"Successfully registered agent '{agent_name}' with capabilities: {capabilities}"
                
            except Exception as e:
                logger.error(f"Failed to register agent: {str(e)}")
                return f"Failed to register agent: {str(e)}"
                
        return Tool(
            name="register_agent",
            description="Register an agent with the Coral Protocol",
            func=_register_agent,
            coroutine=_register_agent
        )
        
    def get_send_message_tool(self) -> Tool:
        """
        Get a tool for sending messages to other agents.
        
        Returns:
            Tool: A LangChain tool for sending messages
        """
        async def _send_message(
            recipient: str,
            content: str,
            thread_id: Optional[str] = None,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
            """Send a message to another agent."""
            if self.client is None:
                await self.connect()
                
            try:
                # Send a message to another agent
                response = await self.client.send_message(
                    recipient=recipient,
                    content=content,
                    thread_id=thread_id
                )
                
                return f"Successfully sent message to '{recipient}': {content}"
                
            except Exception as e:
                logger.error(f"Failed to send message: {str(e)}")
                return f"Failed to send message: {str(e)}"
                
        return Tool(
            name="send_message",
            description="Send a message to another agent",
            func=_send_message,
            coroutine=_send_message
        )
        
    def get_list_agents_tool(self) -> Tool:
        """
        Get a tool for listing available agents.
        
        Returns:
            Tool: A LangChain tool for listing agents
        """
        async def _list_agents(
            include_details: bool = True,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
            """List available agents."""
            if self.client is None:
                await self.connect()
                
            try:
                # List available agents
                agents = await self.client.list_agents(include_details=include_details)
                
                return json.dumps(agents, indent=2)
                
            except Exception as e:
                logger.error(f"Failed to list agents: {str(e)}")
                return f"Failed to list agents: {str(e)}"
                
        return Tool(
            name="list_agents",
            description="List available agents registered with the Coral Protocol",
            func=_list_agents,
            coroutine=_list_agents
        )
        
    def get_create_thread_tool(self) -> Tool:
        """
        Get a tool for creating a new thread.
        
        Returns:
            Tool: A LangChain tool for creating threads
        """
        async def _create_thread(
            participants: List[str],
            initial_message: Optional[str] = None,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
            """Create a new thread with participants."""
            if self.client is None:
                await self.connect()
                
            try:
                # Create a new thread
                thread_id = await self.client.create_thread(
                    participants=participants,
                    initial_message=initial_message
                )
                
                return f"Successfully created thread {thread_id} with participants: {participants}"
                
            except Exception as e:
                logger.error(f"Failed to create thread: {str(e)}")
                return f"Failed to create thread: {str(e)}"
                
        return Tool(
            name="create_thread",
            description="Create a new thread with participants",
            func=_create_thread,
            coroutine=_create_thread
        )
        
    def get_all_tools(self) -> List[Tool]:
        """
        Get all available tools for Coral Protocol integration.
        
        Returns:
            List[Tool]: A list of all available tools
        """
        self.tools = [
            self.get_register_agent_tool(),
            self.get_send_message_tool(),
            self.get_list_agents_tool(),
            self.get_create_thread_tool()
        ]
        
        return self.tools
        
    async def initialize(self) -> None:
        """
        Initialize the Coral MCP Server.
        
        This method connects to the Coral server and registers the agent.
        
        Returns:
            None
        """
        # Connect to the Coral server
        await self.connect()
        
        # Register the agent
        register_tool = self.get_register_agent_tool()
        result = await register_tool.arun(self.agent_name, ["messaging", "coordination"])
        
        logger.info(result)
        
        # Get all tools
        self.tools = self.get_all_tools()
        
        logger.info(f"Initialized Coral MCP Server with {len(self.tools)} tools")
        
    def create_langchain_agent(self, name: str, system_prompt: str) -> Any:
        """
        Create a LangChain agent that can use the Coral Protocol tools.
        
        Args:
            name: Name of the agent
            system_prompt: System prompt for the agent
            
        Returns:
            Any: A LangChain agent
        """
        from langchain.agents import create_tool_calling_agent
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
        
        # Create the LLM
        llm = ChatOpenAI(model="gpt-4o")
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        # Create the agent
        agent = create_tool_calling_agent(llm, self.tools, prompt)
        
        return agent
        
    def create_crewai_agent(self, role: str, goal: str, backstory: str) -> Agent:
        """
        Create a CrewAI agent that can use the Coral Protocol tools.
        
        Args:
            role: Role of the agent
            goal: Goal of the agent
            backstory: Backstory of the agent
            
        Returns:
            Agent: A CrewAI agent
        """
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=self.tools,
            verbose=True
        )

# Example usage
async def main():
    """Example usage of the Coral MCP Server."""
    # Initialize the Coral MCP Server
    coral_server = CoralMCPServer()
    await coral_server.initialize()
    
    # Create a CrewAI agent
    agent = coral_server.create_crewai_agent(
        role="Coordinator",
        goal="Coordinate tasks between agents",
        backstory="You are a coordinator agent that helps manage communication between agents."
    )
    
    # Use the agent in a crew
    crew = Crew(
        agents=[agent],
        tasks=[],
        verbose=True
    )
    
    logger.info("Coral MCP Server initialized successfully")

if __name__ == "__main__":
    asyncio.run(main())
