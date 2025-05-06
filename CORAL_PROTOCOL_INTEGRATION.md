# Coral Protocol Integration for Agent Angus

This document provides instructions for setting up and using the Coral Protocol integration with Agent Angus.

## Overview

The Coral Protocol integration allows Agent Angus to communicate with other agents using the Coral Protocol. This enables structured agent-to-agent communication, memory management, and tool composition across diverse environments.

## Prerequisites

- Python 3.8 or later
- Node.js v18 or later
- npm
- git

## Installation

1. Clone the Agent Angus repository:
   ```bash
   git clone https://github.com/MarkAustinGrow/Angus-vibe.git
   cd Angus-vibe
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the local Coral Protocol server:
   ```bash
   # On Windows
   run_local_coral_server.bat
   
   # On Unix-based systems
   ./run_local_coral_server.sh
   ```

   This will clone the Coral Protocol server repository, install its dependencies, build it, and start it on port 3001.

## Testing the Integration

To verify that the Coral Protocol integration is working correctly, you can run the test script:

```bash
# On Windows
run_coral_test.bat

# On Unix-based systems
./run_coral_test.sh
```

This will run a simple test that connects to the Coral Protocol server, registers an agent, and lists available agents.

## Configuration

The Coral Protocol integration can be configured using environment variables:

- `CORAL_SERVER_URL`: The URL of the Coral Protocol server. Default: `http://localhost:3001/sse`
- `CORAL_SERVER_DIR`: The directory where the Coral Protocol server is cloned. Default: `./coral-server`
- `CORAL_SERVER_PORT`: The port on which the Coral Protocol server runs. Default: `3001`
- `AGENT_NAME`: The name of the agent to register with the Coral Protocol. Default: `angus_agent`

You can set these variables in a `.env` file in the root directory of the project:

```
CORAL_SERVER_URL=http://localhost:3001/sse
CORAL_SERVER_DIR=./coral-server
CORAL_SERVER_PORT=3001
AGENT_NAME=angus_agent
```

## Usage

### Using the Coral MCP Server

The `CoralMCPServer` class provides tools for agent communication, registration, and discovery using the Coral Protocol through the LangChain MCP interface.

```python
from coral_mcp_server import CoralMCPServer

# Create the Coral MCP Server
coral_server = CoralMCPServer()

# Initialize the server
await coral_server.initialize()

# Get all available tools
tools = coral_server.get_all_tools()

# Create a CrewAI agent that can use the Coral Protocol tools
agent = coral_server.create_crewai_agent(
    role="Coordinator",
    goal="Coordinate tasks between agents",
    backstory="You are a coordinator agent that helps manage communication between agents."
)

# Use the agent in a crew
from crewai import Crew, Task
crew = Crew(
    agents=[agent],
    tasks=[
        Task(
            description="List all available agents",
            agent=agent,
            expected_output="A list of all available agents"
        )
    ],
    verbose=True
)

# Run the crew
result = crew.kickoff()
```

### Available Tools

The Coral MCP Server provides the following tools:

1. **Register Agent Tool**: Register an agent with the Coral Protocol
   ```python
   register_tool = coral_server.get_register_agent_tool()
   result = await register_tool.acoroutine("agent_name", ["capability1", "capability2"])
   ```

2. **Send Message Tool**: Send a message to another agent
   ```python
   message_tool = coral_server.get_send_message_tool()
   result = await message_tool.acoroutine("recipient_agent", "Hello from agent_name", "thread_id")
   ```

3. **List Agents Tool**: List available agents registered with the Coral Protocol
   ```python
   list_tool = coral_server.get_list_agents_tool()
   result = await list_tool.acoroutine(True)  # True to include details
   ```

4. **Create Thread Tool**: Create a new thread with participants
   ```python
   thread_tool = coral_server.get_create_thread_tool()
   result = await thread_tool.acoroutine(["agent1", "agent2"], "Initial message")
   ```

## Integration with CrewAI

The Coral Protocol integration works seamlessly with CrewAI. You can create CrewAI agents that use the Coral Protocol tools:

```python
from coral_mcp_server import CoralMCPServer
from crewai import Agent, Task, Crew

# Create the Coral MCP Server
coral_server = CoralMCPServer()
await coral_server.initialize()

# Create a CrewAI agent
agent = coral_server.create_crewai_agent(
    role="Coordinator",
    goal="Coordinate tasks between agents",
    backstory="You are a coordinator agent that helps manage communication between agents."
)

# Create a task
task = Task(
    description="List all available agents",
    agent=agent,
    expected_output="A list of all available agents"
)

# Create a crew
crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

# Run the crew
result = crew.kickoff()
```

## Integration with LangChain

The Coral Protocol integration also works with LangChain. You can create LangChain agents that use the Coral Protocol tools:

```python
from coral_mcp_server import CoralMCPServer

# Create the Coral MCP Server
coral_server = CoralMCPServer()
await coral_server.initialize()

# Create a LangChain agent
agent = coral_server.create_langchain_agent(
    name="langchain_agent",
    system_prompt="You are a helpful assistant that uses tools to communicate with other agents."
)

# Run the agent
result = await agent.ainvoke({"input": "List all available agents"})
```

## Troubleshooting

### Coral Protocol Server Not Starting

If the Coral Protocol server fails to start, check the following:

1. Make sure Node.js v18 or later is installed:
   ```bash
   node --version
   ```

2. Make sure npm is installed:
   ```bash
   npm --version
   ```

3. Make sure git is installed:
   ```bash
   git --version
   ```

4. Check the logs for any errors:
   ```bash
   # On Windows
   run_local_coral_server.bat > coral_server.log 2>&1
   
   # On Unix-based systems
   ./run_local_coral_server.sh > coral_server.log 2>&1
   ```

### Connection Issues

If you're having trouble connecting to the Coral Protocol server, check the following:

1. Make sure the server is running:
   ```bash
   curl http://localhost:3001/health
   ```

2. Check the `CORAL_SERVER_URL` environment variable:
   ```bash
   echo $CORAL_SERVER_URL
   ```

3. Try restarting the server:
   ```bash
   # On Windows
   run_local_coral_server.bat
   
   # On Unix-based systems
   ./run_local_coral_server.sh
   ```

### Import Errors

If you're seeing import errors, make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Resources

- [Coral Protocol Documentation](https://docs.coralprotocol.org/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
