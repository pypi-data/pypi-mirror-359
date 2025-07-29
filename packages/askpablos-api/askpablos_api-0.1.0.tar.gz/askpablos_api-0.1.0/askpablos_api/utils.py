"""
askpablos_api.utils

Utility functions and helpers for the AskPablos API client.

This module provides utility functions that support the main API client
functionality, including logging configuration and option building.
"""

import logging
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger("askpablos_api")


def configure_logging(level: int = logging.INFO,
                      format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s") -> None:
    """
    Configure the logger for the AskPablos API package.

    Sets up logging for the AskPablos API client with customizable log level
    and format. This is useful for debugging API requests and understanding
    what's happening during client operations.

    Args:
        level (int, optional): The logging level to use. Defaults to logging.INFO.
        format_string (str, optional): The format string for log messages.

    Example:
        >>> from askpablos_api import configure_logging
        >>> import logging
        >>> configure_logging(level=logging.DEBUG)
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False


def build_proxy_options(browser: bool = False,
                        rotate_proxy: bool = True,
                        user_agent: Optional[str] = None,
                        cookies: Optional[Dict[str, str]] = None,
                        **kwargs) -> Dict[str, Any]:
    """
    Build a dictionary of options for the proxy request.

    Creates a standardized options dictionary for proxy requests with common
    parameters and defaults.

    Args:
        browser (bool, optional): Whether to use browser automation. Defaults to False.
        rotate_proxy (bool, optional): Whether to use proxy rotation. Defaults to True.
        user_agent (str, optional): Custom User-Agent string.
        cookies (Dict[str, str], optional): Dictionary of cookies.
        **kwargs: Additional options to include in the proxy request.

    Returns:
        Dict[str, Any]: Dictionary of proxy options.
    """
    options = {
        "browser": browser,
        "rotate_proxy": rotate_proxy
    }

    if user_agent:
        options["user_agent"] = user_agent

    if cookies:
        options["cookies"] = cookies

    # Add any additional options
    options.update(kwargs)

    return options
