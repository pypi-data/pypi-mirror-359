"""
askpablos_api.config

Configuration settings for the AskPablos API client.

This module contains default configuration values and settings that can be
customized if needed. The primary API URL is defined here so users don't
need to specify it when creating client instances.
"""

# Default API configuration
DEFAULT_API_URL = "http://10.10.10.178:7500/api/proxy/"

# Default request settings - matching your example
DEFAULT_TIMEOUT = 30
DEFAULT_ROTATE_PROXY = True
DEFAULT_BROWSER = False

# User agent for requests
DEFAULT_USER_AGENT = "AskPablos-Python-Client/0.1.0"
