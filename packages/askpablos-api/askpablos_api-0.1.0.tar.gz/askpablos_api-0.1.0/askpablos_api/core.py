"""
askpablos_api.core

Core functionality for the AskPablos proxy API client.

This module provides the main AskPablos class, which serves as a simple interface
for making GET requests through the AskPablos proxy service. The client handles
authentication, error management, and request formatting automatically.
"""

from typing import Dict, Optional
import logging

from .client import ProxyClient, ResponseData
from .utils import build_proxy_options
from .exceptions import AskPablosError
from .config import DEFAULT_API_URL

logger = logging.getLogger("askpablos_api")


class AskPablos:
    """
    Simple interface for making GET requests through the AskPablos proxy API.

    This class provides a clean interface for sending GET requests through the
    AskPablos proxy service. It handles authentication, request formatting,
    and error management automatically.

    The AskPablos class is designed to be simple and focused - it only supports
    GET requests to keep the interface clean and easy to use.

    Attributes:
        client (ProxyClient): The underlying client for making API requests.

    """

    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize the AskPablos API client.

        Creates a new instance of the AskPablos client with the provided
        authentication credentials. The client will use these credentials
        for all subsequent API requests.

        Args:
            api_key (str): Your unique API key from the AskPablos dashboard.
            secret_key (str): Your private secret key used for HMAC signing.

        Raises:
            AuthenticationError: If any of the required credentials are missing
                                or invalid.
        """
        self.client = ProxyClient(api_key, secret_key, DEFAULT_API_URL)

    def get(
            self,
            url: str,
            params: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, str]] = None,
            browser: bool = False,
            rotate_proxy: bool = False,
            timeout: int = 30,
            **options
    ) -> ResponseData:
        """
        Send a GET request through the AskPablos proxy.

        This is the main method for fetching web pages and API endpoints through
        the AskPablos proxy service. It supports various options for customizing
        the request behavior.

        Args:
            url (str): The target URL to fetch. Must be a valid HTTP/HTTPS URL.
            params (Dict[str, str], optional): URL query parameters to append.
                                             Example: {"page": "1", "limit": "10"}
            headers (Dict[str, str], optional): Custom headers for the request.
            browser (bool, optional): Whether to use browser automation for
                                    JavaScript rendering. Useful for SPAs and
                                    dynamic content. Defaults to False.
            rotate_proxy (bool, optional): Whether to use proxy rotation for this
                                         request. Helps avoid rate limiting.
                                         Defaults to True.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            **options: Additional proxy options like user_agent, cookies, etc.

        Returns:
            ResponseData: The response object from the API containing:
                - status_code (int): HTTP status code from the target server
                - headers (Dict[str, str]): Response headers from target server
                - content (str): Response body/content
                - url (str): Final URL after any redirects
                - elapsed (float): Time taken to complete the request in seconds
                - encoding (Optional[str]): Response text encoding
                - json (Optional[Dict[str, Any]]): Parsed JSON data if available

        Raises:
            APIConnectionError: If the client cannot connect to the AskPablos API.
            ResponseError: If the API returns an error status code.
            AuthenticationError: If authentication fails.
        """
        # Build proxy options
        proxy_options = build_proxy_options(
            browser=browser,
            rotate_proxy=rotate_proxy,
            **options
        )

        try:
            return self.client.request(url=url, headers=headers, params=params, options=proxy_options, timeout=timeout)
        except AskPablosError as e:
            logger.error(f"GET request failed: {str(e)}")
            raise
