"""
Connector SDK Types

A Python package providing type definitions and utilities for connector SDKs.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main types and utilities here
from .types import (
    ConnectorConfig,
    ConnectorMetadata,
    ConnectorResponse,
    ConnectorData,
    ConnectorSettings,
)
from .utils import (
    validate_config,
    create_response,
    serialize_config,
    deserialize_config,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    # Types
    "ConnectorConfig",
    "ConnectorMetadata", 
    "ConnectorResponse",
    "ConnectorData",
    "ConnectorSettings",
    # Utilities
    "validate_config",
    "create_response",
    "serialize_config",
    "deserialize_config",
] 