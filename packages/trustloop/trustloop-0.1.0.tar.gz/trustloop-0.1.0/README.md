# file: /trustloop-python/README.md

# TrustLoop Python Client

A Python client library for interacting with TrustLoop servers. This package provides easy access to TrustLoop APIs for data loading, domain management, and more.

## Prerequisites

**Important**: This package requires a running TrustLoop server. It's a client library that connects to your TrustLoop server instance (default: http://localhost:4000).

## Installation

```bash
pip install trustloop
```

## Quick Start

```python
import trustloop as tl

# Ensure your TrustLoop server is running on localhost:4000
# or configure a custom server URL:
# from trustloop import TrustLoop
# tl = TrustLoop(base_url="http://your-server:port")

# List available data sources
tl.data.list()

# Load data from TrustLoop server
data = tl.data.load("domain-directory")

# List domains
domains = tl.domains.list()

# Make direct API calls
result = tl.api.get("/api/testing/ping")

# Get help
tl.help()
```

## Usage

### Data Module

```python
# Load data from different sources
data = tl.data.load("domain-directory")
testing_data = tl.data.load("testing")
status = tl.data.load("global-status")

# List available data sources
tl.data.list()

# Check cached data
tl.data.cached()

# Reload data (bypass cache)
fresh_data = tl.data.reload("domain-directory")
```

### Domains Module

```python
# List all domains
domains = tl.domains.list()

# Get specific domain
domain = tl.domains.get("example", "namespace", "database")

# Check if domain exists
exists = tl.domains.check_exists("example", "namespace", "database")
```

### API Module

```python
# Make direct GET requests
result = tl.api.get("/api/testing/ping")

# Make direct POST requests
result = tl.api.post("/api/endpoint", {"key": "value"})
```

### EventBus Module

```python
# Emit events (placeholder implementation)
tl.eventbus.emit("test-event", {"key": "value"})
```

## Configuration

By default, the client connects to `http://localhost:4000`. You can customize this:

```python
from trustloop import TrustLoop

# Connect to different server
tl = TrustLoop(base_url="http://your-server:port")
```

## Development

### Local Development

```bash
# Clone and install in development mode
git clone https://github.com/trustloop/trustloop-python
cd trustloop-python
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black trustloop/
isort trustloop/
```

### Building and Publishing

```bash
# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Requirements

- Python 3.8+
- Access to a TrustLoop server

## License

MIT License

## Support

For support and questions, please visit our [GitHub repository](https://github.com/trustloop/trustloop-python) or contact us at hello@trustloop.com.