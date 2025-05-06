"""
CrewAI Tool for Coral Protocol

This module provides a CrewAI tool for interacting with the Coral Protocol.
"""
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class CoralProtocolInput(BaseModel):
    """Input schema for the Coral Protocol tool."""
    agent_did: str = Field(..., description="DID of the agent to call")
    function_name: str = Field(..., description="Name of the function to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the function")

class CoralProtocolTool(BaseTool):
    """Tool for interacting with the Coral Protocol."""
    
    name: str = "coral_protocol"
    description: str = "Call functions on other agents through the Coral Protocol"
    args_schema: type[BaseModel] = CoralProtocolInput
    
    def __init__(self, coral_adapter):
        """
        Initialize the Coral Protocol Tool.
        
        Args:
            coral_adapter: An instance of AngusCoralLangChainAdapter
        """
        super().__init__()
        self.coral_adapter = coral_adapter
    
    def _run(self, agent_did: str, function_name: str, arguments: Dict[str, Any] = None) -> Any:
        """
        Call a function on another agent through the Coral Protocol.
        
        Args:
            agent_did: DID of the agent to call
            function_name: Name of the function to call
            arguments: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        if arguments is None:
            arguments = {}
        
        return self.coral_adapter.call_agent(agent_did, function_name, **arguments)
