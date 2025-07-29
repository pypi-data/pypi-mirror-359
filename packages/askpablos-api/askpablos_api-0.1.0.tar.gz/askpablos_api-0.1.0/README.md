# AskPablos API Client
[![PyPI Version](https://img.shields.io/pypi/v/askpablos-api.svg)](https://pypi.python.org/pypi/askpablos-api)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/askpablos-api.svg)](https://pypi.python.org/pypi/askpablos-api)

A simple Python client for making GET requests through the AskPablos proxy API service. This library provides a clean and easy-to-use interface for fetching web pages and APIs through the AskPablos proxy infrastructure.

## Features

- 🔐 **Secure Authentication**: HMAC-SHA256 signature-based authentication
- 🌐 **Proxy Support**: Route requests through rotating proxies
- 🤖 **Browser Integration**: Support for JavaScript-heavy websites
- 🛡️ **Error Handling**: Comprehensive exception handling
- 📊 **Logging**: Built-in logging support for debugging
- 🎯 **Simple Interface**: GET-only requests for clean API

## Installation

```bash
pip install askpablos-api
```

## Quick Start

```python
from askpablos_api import AskPablos

# Initialize the client
client = AskPablos(
    api_key="your_api_key",
    secret_key="your_secret_key"
)

# Make a simple GET request
response = client.get("https://httpbin.org/ip")
print(response)
```

## Authentication

The AskPablos API uses HMAC-SHA256 signature-based authentication. You only need:

1. **API Key**: Your unique API identifier
2. **Secret Key**: Your private key for signing requests

```python
from askpablos_api import AskPablos

client = AskPablos(
    api_key="your_api_key",
    secret_key="your_secret_key"
)
```

## Usage Examples

### Basic GET Requests

```python
# Simple GET request
response = client.get("https://example.com")

# GET with query parameters
response = client.get(
    "https://api.example.com/users",
    params={"page": 1, "limit": 10}
)

# GET with custom headers
response = client.get(
    "https://api.example.com/data",
    headers={"Authorization": "Bearer token123"}
)
```

### Advanced Options

```python
# Use browser automation for JavaScript-heavy sites
response = client.get(
    "https://spa-website.com",
    browser=True
)

# Disable proxy rotation
response = client.get(
    "https://example.com",
    rotate_proxy=False
)

# Custom user agent and cookies
response = client.get(
    "https://example.com",
    user_agent="Mozilla/5.0 (Custom Bot)",
    cookies={"session": "abc123"}
)

# Custom timeout
response = client.get(
    "https://slow-website.com",
    timeout=60
)
```

### Error Handling

```python
from askpablos_api import (
    AskPablos, 
    AuthenticationError, 
    APIConnectionError, 
    ResponseError
)

try:
    client = AskPablos(api_key="", secret_key="")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")

try:
    response = client.get("https://example.com")
except APIConnectionError as e:
    print(f"Connection failed: {e}")
except ResponseError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### Logging

```python
from askpablos_api import configure_logging
import logging

# Enable debug logging
configure_logging(level=logging.DEBUG)

client = AskPablos(api_key="...", secret_key="...")
response = client.get("https://example.com")  # This will be logged
```

## API Reference

### AskPablos Class

The main interface for the API client.

#### Constructor

```python
AskPablos(api_key: str, secret_key: str)
```

**Parameters:**
- `api_key` (str): Your API key from the AskPablos dashboard
- `secret_key` (str): Your secret key for HMAC signing

#### Methods

##### get()

```python
get(url, params=None, headers=None, browser=False, rotate_proxy=True, timeout=30, **options)
```

Send a GET request through the AskPablos proxy.

**Parameters:**
- `url` (str): Target URL to fetch
- `params` (dict, optional): URL query parameters
- `headers` (dict, optional): Custom headers
- `browser` (bool, optional): Use browser automation (default: False)
- `rotate_proxy` (bool, optional): Enable proxy rotation (default: True)
- `timeout` (int, optional): Request timeout in seconds (default: 30)
- `**options`: Additional options like user_agent, cookies, etc.

**Returns:** Dictionary containing the API response

### Exception Classes

- `AskPablosError` - Base exception class
- `AuthenticationError` - Authentication-related errors
- `APIConnectionError` - Connection and network errors
- `ResponseError` - API response errors

## Response Format

All successful requests return a dictionary with:

```python
{
    "status_code": 200,
    "headers": {"content-type": "text/html", ...},
    "content": "Response body content",
    "url": "Final URL after redirects",
    "proxy_used": "proxy.example.com:8080",
    "time_taken": 1.23
}
```

## Requirements

- Python 3.9+
- requests >= 2.25.0

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Email: fawadstar6@gmail.com
