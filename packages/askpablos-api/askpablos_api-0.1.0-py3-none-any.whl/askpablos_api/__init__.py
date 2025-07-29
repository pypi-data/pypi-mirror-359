"""
askpablos_api

A Python client library for interacting with the AskPablos proxy API service.
"""

from .core import AskPablos
from .client import ProxyClient
from .exceptions import (
    AskPablosError,
    AuthenticationError,
    APIConnectionError,
    ResponseError
)
from .utils import configure_logging

__version__ = "0.1.0"

# Set up default exports
__all__ = [
    "AskPablos",
    "ProxyClient",
    "AskPablosError",
    "AuthenticationError",
    "APIConnectionError",
    "ResponseError",
    "configure_logging",
]
