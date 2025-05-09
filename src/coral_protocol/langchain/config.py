"""
Configuration for Coral Protocol LangChain Integration

This module provides configuration classes for the Coral Protocol LangChain integration.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CoralRunnableConfig:
    """
    Configuration for Coral Protocol LangChain runnable.
    """
    
    def __init__(
        self,
        server_url: str,
        did: str,
        private_key: bytes,
        capability_document: Dict[str, Any],
        timeout: int = 30,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the Coral Runnable configuration.
        
        Args:
            server_url: URL of the Coral Protocol server
            did: Decentralized identifier for the agent
            private_key: Private key as bytes
            capability_document: Capability document for the agent
            timeout: Timeout for requests in seconds
            verify_ssl: Whether to verify SSL certificates
            headers: Additional headers for requests
        """
        self.server_url = server_url
        self.did = did
        self.private_key = private_key
        self.capability_document = capability_document
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.headers = headers or {}
        
        logger.info(f"Initialized Coral Runnable configuration for {did}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            Configuration as a dictionary
        """
        return {
            "server_url": self.server_url,
            "did": self.did,
            "private_key": self.private_key,
            "capability_document": self.capability_document,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
            "headers": self.headers
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CoralRunnableConfig":
        """
        Create a configuration from a dictionary.
        
        Args:
            config_dict: Configuration as a dictionary
            
        Returns:
            CoralRunnableConfig instance
        """
        return cls(
            server_url=config_dict["server_url"],
            did=config_dict["did"],
            private_key=config_dict["private_key"],
            capability_document=config_dict["capability_document"],
            timeout=config_dict.get("timeout", 30),
            verify_ssl=config_dict.get("verify_ssl", True),
            headers=config_dict.get("headers", {})
        )
