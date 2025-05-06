"""
Coral Protocol LangChain Integration

This package provides integration between LangChain and the Coral Protocol.
"""

from src.coral_protocol.langchain.runnable import CoralRunnable
from src.coral_protocol.langchain.config import CoralRunnableConfig

__all__ = ["CoralRunnable", "CoralRunnableConfig"]
