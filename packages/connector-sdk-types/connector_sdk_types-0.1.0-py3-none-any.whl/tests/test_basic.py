"""
Basic tests for connector-sdk-types package.
"""

import pytest
from connector_sdk_types import __version__, __author__, __email__


def test_package_import():
    """Test that the package can be imported successfully."""
    assert __version__ == "0.1.0"
    assert __author__ == "Your Name"
    assert __email__ == "your.email@example.com"


def test_package_structure():
    """Test that the package has the expected structure."""
    import connector_sdk_types
    
    # Check that the package has the expected attributes
    assert hasattr(connector_sdk_types, "__version__")
    assert hasattr(connector_sdk_types, "__author__")
    assert hasattr(connector_sdk_types, "__email__")
    assert hasattr(connector_sdk_types, "__all__")


if __name__ == "__main__":
    pytest.main([__file__]) 