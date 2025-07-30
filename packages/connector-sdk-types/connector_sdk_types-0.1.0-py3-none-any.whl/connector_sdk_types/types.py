"""
Type definitions for connector SDKs.
"""

from typing import Any, Dict, List, Optional, Union
from typing_extensions import TypedDict


class ConnectorConfig(TypedDict, total=False):
    """Configuration for a connector."""
    
    name: str
    version: str
    description: Optional[str]
    settings: Dict[str, Any]
    credentials: Dict[str, Any]


class ConnectorMetadata(TypedDict):
    """Metadata for a connector."""
    
    id: str
    name: str
    version: str
    description: str
    author: str
    tags: List[str]


class ConnectorResponse(TypedDict, total=False):
    """Response from a connector operation."""
    
    success: bool
    data: Optional[Any]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]


# Type aliases for common patterns
ConnectorData = Union[Dict[str, Any], List[Dict[str, Any]]]
ConnectorSettings = Dict[str, Union[str, int, float, bool, List[str]]] 