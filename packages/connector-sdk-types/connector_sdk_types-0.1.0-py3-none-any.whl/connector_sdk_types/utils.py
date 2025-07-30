"""
Utility functions for connector SDKs.
"""

import json
from typing import Any, Dict, Optional
from .types import ConnectorConfig, ConnectorResponse


def validate_config(config: ConnectorConfig) -> bool:
    """
    Validate a connector configuration.
    
    Args:
        config: The configuration to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["name", "version"]
    
    for field in required_fields:
        if field not in config:
            return False
    
    return True


def create_response(
    success: bool,
    data: Optional[Any] = None,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> ConnectorResponse:
    """
    Create a standardized connector response.
    
    Args:
        success: Whether the operation was successful
        data: The response data
        error: Error message if operation failed
        metadata: Additional metadata
        
    Returns:
        A ConnectorResponse object
    """
    response: ConnectorResponse = {"success": success}
    
    if data is not None:
        response["data"] = data
    
    if error is not None:
        response["error"] = error
    
    if metadata is not None:
        response["metadata"] = metadata
    
    return response


def serialize_config(config: ConnectorConfig) -> str:
    """
    Serialize a connector configuration to JSON.
    
    Args:
        config: The configuration to serialize
        
    Returns:
        JSON string representation
    """
    return json.dumps(config, indent=2)


def deserialize_config(config_str: str) -> ConnectorConfig:
    """
    Deserialize a JSON string to a connector configuration.
    
    Args:
        config_str: JSON string representation
        
    Returns:
        ConnectorConfig object
    """
    return json.loads(config_str) 