# Step-by-Step Guide: Integrating Coral Protocol with LangChain for Agent Angus

I'm glad you're pleased with the work! Here's a comprehensive guide for integrating the Coral Protocol with LangChain for your Angus agent, which you can share with the other AI coding tool.

## Prerequisites

- Python 3.11 or higher
- LangChain (0.1.0 or higher)
- LangChain OpenAI (if using OpenAI models)
- A running Coral Protocol server (e.g., [](http://coral.pushcollective.club/sse)<http://coral.pushcollective.club/sse>)

## Step 1: Create the Directory Structure

Create the following directory structure for the Coral Protocol LangChain integration:

```javascript
src/
└── coral_protocol/
    └── langchain/
        ├── __init__.py
        ├── config.py
        └── runnable.py
```

## Step 2: Implement the Configuration Class

Create `src/coral_protocol/langchain/config.py`:

```python
"""
Configuration for the CoralRunnable class.
"""
from typing import Dict, Any, Optional


class CoralRunnableConfig:
    """
    Configuration for the CoralRunnable class.
    
    This class holds the configuration for connecting to a Coral Protocol server
    and registering an agent with it.
    """
    
    def __init__(
        self,
        server_url: str,
        did: str,
        private_key: bytes,
        capability_document: Dict[str, Any],
        agent_name: Optional[str] = None,
        agent_description: Optional[str] = None,
    ):
        """
        Initialize the CoralRunnableConfig.
        
        Args:
            server_url: URL of the Coral server
            did: DID of the agent
            private_key: Private key as bytes
            capability_document: Capability document for the agent
            agent_name: Name of the agent (optional)
            agent_description: Description of the agent (optional)
        """
        self.server_url = server_url
        self.did = did
        self.private_key = private_key
        self.capability_document = capability_document
        self.agent_name = agent_name or "Unnamed Agent"
        self.agent_description = agent_description or "No description provided"
```

## Step 3: Implement the Package Initialization

Create `src/coral_protocol/langchain/__init__.py`:

```python
"""
Coral Protocol LangChain Integration

This package provides integration between LangChain and the Coral Protocol.
"""

from src.coral_protocol.langchain.runnable import CoralRunnable
from src.coral_protocol.langchain.config import CoralRunnableConfig

__all__ = ["CoralRunnable", "CoralRunnableConfig"]
```

## Step 4: Implement the CoralRunnable Class

Create `src/coral_protocol/langchain/runnable.py`:

```python
"""
CoralRunnable class for integrating with the Coral Protocol.
"""
import json
import logging
import threading
import time
from typing import Dict, Any, List, Callable, Optional, Union, Tuple

import requests
from langchain.schema.runnable import Runnable

from src.coral_protocol.langchain.config import CoralRunnableConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoralRunnable:
    """
    A LangChain Runnable that integrates with the Coral Protocol.
    
    This class allows exposing functions through the Coral Protocol and
    calling functions on other agents.
    """
    
    def __init__(
        self,
        functions: Dict[str, Callable],
        config: CoralRunnableConfig
    ):
        """
        Initialize the CoralRunnable.
        
        Args:
            functions: Dictionary mapping function names to callables
            config: Configuration for the Coral Protocol integration
        """
        self.functions = functions
        self.config = config
        
        # Register with the Coral server
        self._register_with_server()
        
        # Server for handling incoming requests
        self.server_thread = None
        self.server_running = False
    
    def _register_with_server(self) -> None:
        """Register with the Coral server."""
        try:
            # Create registration payload
            payload = {
                "did": self.config.did,
                "capability_document": self.config.capability_document,
                "name": self.config.agent_name,
                "description": self.config.agent_description
            }
            
            # Sign the payload
            signature = self._sign_payload(payload)
            
            # Send registration request
            headers = {
                "Content-Type": "application/json",
                "X-Signature": signature
            }
            
            response = requests.post(
                f"{self.config.server_url}/register",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully registered with Coral server at {self.config.server_url}")
            else:
                logger.error(f"Failed to register with Coral server: {response.text}")
        except Exception as e:
            logger.error(f"Error registering with Coral server: {str(e)}")
    
    def _sign_payload(self, payload: Dict[str, Any]) -> str:
        """
        Sign a payload with the private key.
        
        Args:
            payload: Payload to sign
            
        Returns:
            Signature as a string
        """
        # In a real implementation, this would use cryptography to sign the payload
        # For now, we'll just return a placeholder
        return "signature_placeholder"
    
    def call_agent(self, agent_did: str, function_name: str, **kwargs) -> Any:
        """
        Call a function on another agent.
        
        Args:
            agent_did: DID of the agent to call
            function_name: Name of the function to call
            **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        try:
            # Create function call payload
            payload = {
                "did": self.config.did,
                "target_did": agent_did,
                "function": function_name,
                "arguments": kwargs
            }
            
            # Sign the payload
            signature = self._sign_payload(payload)
            
            # Send function call request
            headers = {
                "Content-Type": "application/json",
                "X-Signature": signature
            }
            
            response = requests.post(
                f"{self.config.server_url}/call",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully called {function_name} on agent {agent_did}")
                return response.json().get("result")
            else:
                logger.error(f"Failed to call function: {response.text}")
                return {"status": "failed", "error": response.text}
        except Exception as e:
            logger.error(f"Error calling function: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """
        Discover agents registered with the Coral server.
        
        Returns:
            List of dictionaries containing agent information
        """
        try:
            # Create discovery payload
            payload = {
                "did": self.config.did
            }
            
            # Sign the payload
            signature = self._sign_payload(payload)
            
            # Send discovery request
            headers = {
                "Content-Type": "application/json",
                "X-Signature": signature
            }
            
            response = requests.get(
                f"{self.config.server_url}/discover",
                headers=headers,
                params=payload
            )
            
            if response.status_code == 200:
                logger.info("Successfully discovered agents")
                return response.json().get("agents", [])
            else:
                logger.error(f"Failed to discover agents: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error discovering agents: {str(e)}")
            return []
    
    def get_agent_capabilities(self, agent_did: str) -> Dict[str, Any]:
        """
        Get the capabilities of an agent.
        
        Args:
            agent_did: DID of the agent
            
        Returns:
            Dictionary containing the agent's capabilities
        """
        try:
            # Create capabilities payload
            payload = {
                "did": self.config.did,
                "target_did": agent_did
            }
            
            # Sign the payload
            signature = self._sign_payload(payload)
            
            # Send capabilities request
            headers = {
                "Content-Type": "application/json",
                "X-Signature": signature
            }
            
            response = requests.get(
                f"{self.config.server_url}/capabilities",
                headers=headers,
                params=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully retrieved capabilities for agent {agent_did}")
                return response.json().get("capabilities", {})
            else:
                logger.error(f"Failed to get agent capabilities: {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error getting agent capabilities: {str(e)}")
            return {}
    
    def start_server(self, host: str = '0.0.0.0', port: int = 5001) -> None:
        """
        Start a server to listen for requests from the Coral Protocol.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        if self.server_running:
            logger.warning("Server is already running")
            return
        
        self.server_running = True
        self.server_thread = threading.Thread(
            target=self._run_server,
            args=(host, port),
            daemon=True
        )
        self.server_thread.start()
        
        logger.info(f"Started server on {host}:{port}")
    
    def _run_server(self, host: str, port: int) -> None:
        """
        Run the server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        # In a real implementation, this would start a web server
        # For now, we'll just simulate it with a loop
        try:
            while self.server_running:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error in server thread: {str(e)}")
            self.server_running = False
    
    def stop_server(self) -> None:
        """Stop the server."""
        if not self.server_running:
            logger.warning("Server is not running")
            return
        
        self.server_running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)
            
        logger.info("Stopped server")
```

## Step 5: Create the Adapter for Angus

Create a new file `src/angus_coral_adapter.py`:

```python
"""
Coral Protocol LangChain Integration for Angus

This module provides integration between Angus and the Coral Protocol
using LangChain.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

from src.coral_protocol.langchain import CoralRunnable, CoralRunnableConfig
from langchain.schema.runnable import Runnable
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AngusCoralAdapter:
    """
    Adapter for integrating Angus with the Coral Protocol using LangChain.
    
    This class provides functionality for:
    - Registering Angus's capabilities with a Coral server
    - Handling requests from other agents through the Coral Protocol
    - Sending requests to other agents through the Coral Protocol
    """
    
    def __init__(self, 
                 angus_agent,
                 coral_server_url: str,
                 openai_api_key: Optional[str] = None,
                 did_domain: str = "angus.ai",
                 private_key_path: Optional[str] = None):
        """
        Initialize the Angus Coral Adapter.
        
        Args:
            angus_agent: Instance of AngusAgent
            coral_server_url: URL of the Coral server
            openai_api_key: API key for OpenAI (optional, will use AngusAgent's key if not provided)
            did_domain: Domain for the did:web identifier
            private_key_path: Path to a file containing a private key for DID
        """
        self.angus_agent = angus_agent
        self.coral_server_url = coral_server_url
        self.openai_api_key = openai_api_key or angus_agent.openai_api_key
        
        # Use the DID manager from the Angus agent
        self.did_manager = angus_agent.did_manager
        self.capability_generator = angus_agent.capability_generator
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(api_key=self.openai_api_key)
        
        # Create Coral runnable configuration
        self.coral_config = CoralRunnableConfig(
            server_url=coral_server_url,
            did=self.did_manager.did,
            private_key=self._get_private_key_bytes(),
            capability_document=self.capability_generator.generate(),
            agent_name="Angus",
            agent_description="Angus AI Agent"
        )
        
        # Create Coral runnable
        self.coral_runnable = self._create_coral_runnable()
        
        logger.info(f"AngusCoralAdapter initialized with DID: {self.did_manager.did}")
        logger.info(f"Connected to Coral server at: {coral_server_url}")
    
    def _get_private_key_bytes(self) -> bytes:
        """
        Get the private key as bytes.
        
        Returns:
            Private key as bytes
        """
        from cryptography.hazmat.primitives import serialization
        
        private_key_bytes = self.did_manager.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return private_key_bytes
    
    def _create_coral_runnable(self) -> CoralRunnable:
        """
        Create a Coral runnable with Angus's capabilities.
        
        Returns:
            CoralRunnable instance
        """
        # Define the functions to expose through Coral
        # Customize these based on Angus's capabilities
        functions = {
            "process_query": self.angus_agent.process_query,
            # Add more functions as needed
        }
        
        # Create the Coral runnable
        coral_runnable = CoralRunnable(
            functions=functions,
            config=self.coral_config
        )
        
        return coral_runnable
    
    def register_with_coral_server(self) -> bool:
        """
        Register Angus's capabilities with the Coral server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # The registration happens automatically when the CoralRunnable is created
            # We just need to make sure it's initialized
            if self.coral_runnable:
                logger.info(f"Successfully registered with Coral server at {self.coral_server_url}")
                return True
            else:
                logger.error("Coral runnable not initialized")
                return False
        except Exception as e:
            logger.error(f"Error registering with Coral server: {str(e)}")
            return False
    
    def call_agent(self, agent_did: str, function_name: str, **kwargs) -> Any:
        """
        Call a function on another agent through the Coral Protocol.
        
        Args:
            agent_did: DID of the agent to call
            function_name: Name of the function to call
            **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        try:
            logger.info(f"Calling {function_name} on agent {agent_did}")
            
            # Create the function call
            result = self.coral_runnable.call_agent(
                agent_did=agent_did,
                function_name=function_name,
                **kwargs
            )
            
            logger.info(f"Successfully called {function_name} on agent {agent_did}")
            return result
        except Exception as e:
            logger.error(f"Error calling agent {agent_did}: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """
        Discover agents registered with the Coral server.
        
        Returns:
            List of dictionaries containing agent information
        """
        try:
            logger.info(f"Discovering agents on Coral server {self.coral_server_url}")
            
            # Get the list of agents
            agents = self.coral_runnable.discover_agents()
            
            logger.info(f"Discovered {len(agents)} agents")
            return agents
        except Exception as e:
            logger.error(f"Error discovering agents: {str(e)}")
            return []
    
    def get_agent_capabilities(self, agent_did: str) -> Dict[str, Any]:
        """
        Get the capabilities of an agent.
        
        Args:
            agent_did: DID of the agent
            
        Returns:
            Dictionary containing the agent's capabilities
        """
        try:
            logger.info(f"Getting capabilities for agent {agent_did}")
            
            # Get the agent's capabilities
            capabilities = self.coral_runnable.get_agent_capabilities(agent_did)
            
            logger.info(f"Successfully retrieved capabilities for agent {agent_did}")
            return capabilities
        except Exception as e:
            logger.error(f"Error getting capabilities for agent {agent_did}: {str(e)}")
            return {}
    
    def start_server(self, host: str = '0.0.0.0', port: int = 5001) -> None:
        """
        Start a server to listen for requests from the Coral Protocol.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        try:
            logger.info(f"Starting Coral server on {host}:{port}")
            
            # Start the server
            self.coral_runnable.start_server(host=host, port=port)
            
            logger.info(f"Coral server started on {host}:{port}")
        except Exception as e:
            logger.error(f"Error starting Coral server: {str(e)}")
            raise
```

## Step 6: Create a Test Script

Create a test script `test_angus_coral.py`:

```python
#!/usr/bin/env python
"""
Test script for the Coral Protocol LangChain integration with Angus.

This script demonstrates how to use the AngusCoralAdapter to connect
Angus to a Coral Protocol server using LangChain.
"""
import os
import json
import logging
import argparse
from pprint import pprint

from src.angus_agent import AngusAgent  # Import your Angus agent class
from src.angus_coral_adapter import AngusCoralAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_coral_connection(coral_server_url):
    """
    Test the connection to a Coral Protocol server.
    
    Args:
        coral_server_url: URL of the Coral server
    """
    print(f"\n=== Testing Coral Protocol Connection to {coral_server_url} ===\n")
    
    try:
        # Initialize Angus agent
        angus_agent = AngusAgent()
        
        # Initialize Coral adapter
        coral_adapter = AngusCoralAdapter(
            angus_agent=angus_agent,
            coral_server_url=coral_server_url
        )
        
        # Register with Coral server
        success = coral_adapter.register_with_coral_server()
        
        if success:
            print("Successfully registered with Coral server")
        else:
            print("Failed to register with Coral server")
            return False
        
        # Discover agents
        print("\nDiscovering agents on Coral server...")
        agents = coral_adapter.discover_agents()
        
        if agents:
            print(f"Discovered {len(agents)} agents:")
            for agent in agents:
                print(f"  - {agent.get('name', 'Unknown')} ({agent.get('did', 'Unknown DID')})")
        else:
            print("No agents discovered")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Coral connection: {str(e)}")
        return False

def test_agent_capabilities(coral_server_url, agent_did):
    """
    Test getting the capabilities of an agent.
    
    Args:
        coral_server_url: URL of the Coral server
        agent_did: DID of the agent to get capabilities for
    """
    print(f"\n=== Testing Agent Capabilities for {agent_did} ===\n")
    
    try:
        # Initialize Angus agent
        angus_agent = AngusAgent()
        
        # Initialize Coral adapter
        coral_adapter = AngusCoralAdapter(
            angus_agent=angus_agent,
            coral_server_url=coral_server_url
        )
        
        # Get agent capabilities
        print(f"Getting capabilities for agent {agent_did}...")
        capabilities = coral_adapter.get_agent_capabilities(agent_did)
        
        if capabilities:
            print("Agent capabilities:")
            pprint(capabilities)
        else:
            print("Failed to get agent capabilities")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error testing agent capabilities: {str(e)}")
        return False

def test_agent_call(coral_server_url, agent_did, function_name, **kwargs):
    """
    Test calling a function on another agent.
    
    Args:
        coral_server_url: URL of the Coral server
        agent_did: DID of the agent to call
        function_name: Name of the function to call
        **kwargs: Arguments to pass to the function
    """
    print(f"\n=== Testing Agent Call to {agent_did}.{function_name} ===\n")
    
    try:
        # Initialize Angus agent
        angus_agent = AngusAgent()
        
        # Initialize Coral adapter
        coral_adapter = AngusCoralAdapter(
            angus_agent=angus_agent,
            coral_server_url=coral_server_url
        )
        
        # Call the function
        print(f"Calling {function_name} on agent {agent_did}...")
        result = coral_adapter.call_agent(
            agent_did=agent_did,
            function_name=function_name,
            **kwargs
        )
        
        if result:
            print("Function call result:")
            pprint(result)
        else:
            print("Failed to call function")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error calling agent function: {str(e)}")
        return False

def start_coral_server(coral_server_url, host='0.0.0.0', port=5001):
    """
    Start a Coral server to listen for requests.
    
    Args:
        coral_server_url: URL of the Coral server
        host: Host to bind to
        port: Port to bind to
    """
    print(f"\n=== Starting Coral Server on {host}:{port} ===\n")
    
    try:
        # Initialize Angus agent
        angus_agent = AngusAgent()
        
        # Initialize Coral adapter
        coral_adapter = AngusCoralAdapter(
            angus_agent=angus_agent,
            coral_server_url=coral_server_url
        )
        
        # Start the server
        print(f"Starting Coral server on {host}:{port}...")
        coral_adapter.start_server(host=host, port=port)
        
        return True
    except Exception as e:
        logger.error(f"Error starting Coral server: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test Coral Protocol LangChain integration with Angus')
    
    # Add arguments
    parser.add_argument('--server-url', type=str, required=True,
                        help='URL of the Coral server')
    parser.add_argument('--test', type=str, choices=['connection', 'capabilities', 'call', 'server'],
                        default='connection', help='Test to run')
    parser.add_argument('--agent-did', type=str, help='DID of the agent to interact with')
    parser.add_argument('--function', type=str, help='Function to call on the agent')
    parser.add_argument('--args', type=str, help='JSON string of arguments to pass to the function')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind server to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind server to')
    
    args = parser.parse_args()
    
    # Run the specified test
    if args.test == 'connection':
        success = test_coral_connection(args.server_url)
    elif args.test == 'capabilities':
        if not args.agent_did:
            parser.error("--agent-did is required for capabilities test")
        success = test_agent_capabilities(args.server_url, args.agent_did)
    elif args.test == 'call':
        if not args.agent_did or not args.function:
            parser.error("--agent-did and --function are required for call test")
        
        # Parse function arguments
        kwargs = {}
        if args.args:
            try:
                kwargs = json.loads(args.args)
            except json.JSONDecodeError:
                parser.error("--args must be a valid JSON string")
        
        success = test_agent_call(args.server_url, args.agent_did, args.function, **kwargs)
    elif args.test == 'server':
        success = start_coral_server(args.server_url, args.host, args.port)
    else:
        parser.error(f"Unknown test: {args.test}")
    
    # Print result
    if success:
        print("\nTest completed successfully")
        return 0
    else:
        print("\nTest failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

## Step 7: Integrate with CrewAI

If you want to integrate the Coral Protocol with CrewAI, you can create a CrewAI tool that uses the AngusCoralAdapter:

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from typing import Dict, Any, List, Optional

class CoralProtocolTool(BaseTool):
    """Tool for interacting with the Coral Protocol."""
    
    name: str = "Coral Protocol Tool"
    description: str = "A tool for interacting with other agents through the Coral Protocol."
    
    def __init__(self, coral_adapter):
        """
        Initialize the Coral Protocol Tool.
        
        Args:
            coral_adapter: An instance of AngusCoralAdapter
        """
        super().__init__()
        self.coral_adapter = coral_adapter
    
    def _run(self, agent_did: str, function_name: str, **kwargs) -> Any:
        """
        Call a function on another agent through the Coral Protocol.
        
        Args:
            agent_did: DID of the agent to call
            function_name: Name of the function to call
            **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        return self.coral_adapter.call_agent(agent_did, function_name, **kwargs)

# Example usage in a CrewAI setup
def create_crew_with_coral():
    # Initialize Angus agent
    angus_agent = AngusAgent()
    
    # Initialize Coral adapter
    coral_adapter = AngusCoralAdapter(
        angus_agent=angus_agent,
        coral_server_url="http://coral.pushcollective.club/sse"
    )
    
    # Start the Coral server
    coral_adapter.start_server(host='0.0.0.0', port=5001)
    
    # Create the Coral Protocol tool
    coral_tool = CoralProtocolTool(coral_adapter)
    
    # Create a CrewAI agent with the Coral Protocol tool
    agent = Agent(
        role="Coral Protocol Agent",
        goal="Interact with other agents through the Coral Protocol",
        backstory="I am an agent that can interact with other agents through the Coral Protocol.",
        tools=[coral_tool],
        verbose=True
    )
    
    # Create a task for the agent
    task = Task(
        description="Discover agents on the Coral Protocol server and interact with them.",
        agent=agent
    )
    
    # Create a crew with the agent and task
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result
```

## Step 8: Testing with Yona

To test the integration with Yona, you can use the following command:

```bash
python test_angus_coral.py --server-url http://coral.pushcollective.club/sse --test connection
```

To test calling a function on Yona:

```bash
python test_angus_coral.py --server-url http://coral.pushcollective.club/sse --test call --agent-did did:web:yona.ai --function create_song --args '{"prompt": "Create a happy K-pop song about summer adventures"}'
```

## Conclusion

This guide provides a step-by-step approach to integrating the Coral Protocol with LangChain for your Angus agent. The implementation allows Angus to:

1. Register with a Coral Protocol server
2. Discover other agents on the server
3. Get the capabilities of other agents
4. Call functions on other agents
5. Start a server to listen for requests from other agents

The integration also includes a CrewAI tool that allows you to use the Coral Protocol in your CrewAI workflows.

Remember to adapt the code to your specific Angus agent implementation, particularly the functions you want to expose through the Coral Protocol.
