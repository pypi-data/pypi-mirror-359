"""
askpablos_api.client

This module provides the main client class for interacting with the AskPablos proxy API.

The ProxyClient class handles low-level communication with the AskPablos API service,
including authentication, request signing, and HTTP communication. It serves as the
foundation for higher-level interfaces like the AskPablos class.

This module is designed for users who need direct control over API requests and
authentication handling, or for building custom interfaces on top of the base client.
"""

import json
import base64
import hmac
import hashlib
import requests
from typing import Optional, Dict, Any

from .exceptions import APIConnectionError, ResponseError, AuthenticationError


class ResponseData:
    """Response object that provides dot notation access to response data."""

    def __init__(self, status_code: int, headers: Dict[str, str], content: str,
                 url: str, elapsed: float, encoding: Optional[str],
                 json_data: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.url = url
        self.elapsed = elapsed
        self.encoding = encoding
        self.json = json_data


class ProxyClient:
    """
    ProxyClient securely sends requests through the AskPablos proxy service.

    This is the low-level client that handles direct communication with the AskPablos
    API. It manages authentication via HMAC-SHA256 signatures, constructs proper
    request headers, and handles HTTP communication with the proxy service.

    The ProxyClient is typically used internally by higher-level classes like AskPablos,
    but can be used directly for fine-grained control over API interactions.

    Attributes:
        api_key (str): The API key for authentication.
        secret_key (str): The secret key for HMAC signing.
        api_url (str): The base URL of the proxy API service.

    Security Note:
        This client uses HMAC-SHA256 signatures to ensure request integrity and
        authenticity. The secret_key is never transmitted and is only used locally
        to generate signatures.
    """

    def __init__(self, api_key: str, secret_key: str, api_url: str):
        """
        Initialize the API client.

        Sets up the client with authentication credentials and validates that
        all required parameters are provided.

        Args:
            api_key (str): Your API key from the AskPablos dashboard. This identifies
                          your account and is included in the X-API-Key header.
            secret_key (str): Your shared secret for HMAC signing. This is used to
                             generate request signatures and must be kept secure.
            api_url (str): The proxy API base URL. This should be the full URL to
                          the proxy endpoint.

        Raises:
            AuthenticationError: If any required credential is missing or empty.
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_url = api_url

        if not all([api_key, secret_key, api_url]):
            raise AuthenticationError("API key, secret key, and API URL must all be provided")

    def _generate_signature(self, payload: str) -> str:
        """
        Generate a base64-encoded HMAC SHA256 signature.

        Creates a cryptographic signature of the request payload using the client's
        secret key. This signature is used by the API server to verify that the
        request came from an authorized client and hasn't been tampered with.

        Args:
            payload (str): JSON string of the request body that will be signed.
                          This should be the exact JSON that will be sent in the
                          HTTP request body.

        Returns:
            str: Base64 encoded HMAC-SHA256 signature of the payload.

        Note:
            The signature is generated using HMAC-SHA256 with the client's secret key.
            The resulting binary signature is then base64-encoded for transmission
            in HTTP headers.
        """
        signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _build_headers(self, payload: str) -> dict:
        """
        Construct request headers with API key and signature.

        Builds the complete set of HTTP headers needed for API authentication,
        including the content type, API key, and request signature.

        Args:
            payload (str): JSON string of the request body. Used to generate
                          the authentication signature.

        Returns:
            dict: HTTP headers dictionary containing:
                - Content-Type: Set to "application/json"
                - X-API-Key: Your API key for identification
                - X-Signature: HMAC-SHA256 signature of the payload
        """
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Signature': self._generate_signature(payload)
        }

    def request(
            self,
            url: str,
            method: str = "GET",
            data: dict = None,
            headers: dict = None,
            params: dict = None,
            options: dict = None,
            timeout: int = 30
    ) -> ResponseData:
        """
        Send a request through the AskPablos proxy.

        This is the core method that handles communication with the AskPablos API.
        It constructs the request payload, generates authentication headers,
        and sends the HTTP request to the proxy service.

        Args:
            url (str): The target URL to fetch through the proxy. Must be a valid
                      HTTP or HTTPS URL.
            method (str, optional): HTTP method for the request. Supported methods
                                  include GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS.
                                  Defaults to "GET".
            data (dict, optional): Request payload for POST/PUT requests. Will be
                                 included in the request body sent to the target URL.
            headers (dict, optional): Custom headers to send to the target URL.
                                    These are forwarded to the target server, not
                                    used for API authentication.
            params (dict, optional): Query parameters to append to the target URL.
            options (dict, optional): Proxy-specific options controlling how the
                                    request is processed. See options below.
            timeout (int, optional): Request timeout in seconds. If the proxy
                                   doesn't respond within this time, the request
                                   will be cancelled. Defaults to 30.

        Proxy Options:
            The options dictionary can contain:
            - browser (bool): Use browser automation for JavaScript rendering
            - rotate_proxy (bool): Use proxy rotation for this request
            - user_agent (str): Custom user agent string
            - cookies (dict): Cookies to include with the request
            - Any other proxy-specific options supported by the API

        Returns:
            dict: The JSON response from the AskPablos API containing the results
                 of the proxied request. The exact structure depends on the API
                 version, but typically includes status_code, headers, content, etc.

        Raises:
            APIConnectionError: If the client cannot connect to the AskPablos API
                              due to network issues, DNS problems, or timeouts.
            ResponseError: If the API returns an HTTP error status code (4xx or 5xx).
                         The exception will include the status code and error message.
        """
        # Initialize options dictionary if not provided
        if options is None:
            options = {}

        # Create the request data - matching your exact format
        request_data = {
            "url": url,
            "method": method.upper(),
            "browser": options.get("browser", False),
            "rotateProxy": options.get("rotate_proxy", False)
        }

        if data:
            request_data["data"] = data

        if headers:
            request_data["headers"] = headers

        if params:
            request_data["params"] = params

        # Add any additional options
        for key, value in options.items():
            if key not in ["browser", "rotate_proxy"]:
                request_data[key] = value

        # Convert to JSON with same separators as your example
        payload = json.dumps(request_data, separators=(',', ':'))
        headers = self._build_headers(payload)

        try:
            response = requests.post(self.api_url, data=payload, headers=headers, timeout=timeout)

            if response.status_code >= 400:
                error_msg = response.json().get('error', 'Unknown error') if response.text else 'No error details provided'
                raise ResponseError(response.status_code, error_msg)

            # Return complete response information
            response_data = ResponseData(
                url=response.url,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=json.loads(response.text).get('data'),
                elapsed=response.elapsed.total_seconds(),
                encoding=response.encoding
            )

            try:
                response_data.json = response.json()
            except (ValueError, json.JSONDecodeError):
                response_data.json = None

            return response_data
        except requests.RequestException as e:
            raise APIConnectionError(f"Failed to connect to API: {str(e)}")
