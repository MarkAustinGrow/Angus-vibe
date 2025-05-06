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
        self.agent_name = agent_name or "Agent Angus"
        self.agent_description = agent_description or "AI agent for YouTube publishing and audience engagement"
