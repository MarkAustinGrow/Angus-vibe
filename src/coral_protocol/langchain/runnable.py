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
