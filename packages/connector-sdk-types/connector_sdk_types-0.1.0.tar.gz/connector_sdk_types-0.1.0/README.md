# Connector SDK Types

A Python package providing type definitions and utilities for connector SDKs.

## Installation

You can install the package from PyPI:

```bash
pip install connector-sdk-types
```

Or install from source:

```bash
git clone https://github.com/yourusername/connector-sdk-types.git
cd connector-sdk-types
pip install -e .
```

## Development Installation

For development, install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from connector_sdk_types import __version__

print(f"Connector SDK Types version: {__version__}")
```

## Features

- Type definitions for connector SDKs
- Utility functions for common connector operations
- Comprehensive type hints for better IDE support

## Development

### Setup Development Environment

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Install pre-commit hooks: `pre-commit install`

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

### Linting

```bash
flake8 .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### 0.1.0 (2024-01-01)

- Initial release
- Basic package structure
- Type definitions foundation 