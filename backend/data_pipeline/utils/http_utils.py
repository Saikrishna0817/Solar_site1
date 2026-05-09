"""
HTTP utilities with retries and basic backoff for robust data fetching.
"""
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional

from .logging_helpers import get_logger

logger = get_logger(__name__)

# ─── Retry strategy ───────────────────────────────────────────────
def get_retrying_session(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: tuple = (500, 502, 503, 504, 429),
) -> requests.Session:
    """
    Create a requests session with automatic retries.
    
    Args:
        retries: Total number of retries to attempt.
        backoff_factor: Backoff factor for urllib3 retry sleeps.
        status_forcelist: HTTP status codes that trigger a retry.
    
    Returns:
        A configured requests.Session instance.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def robust_get(url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
    """
    Perform a GET request with automatic retry and exponential backoff.
    
    Args:
        url: The URL to fetch.
        params: Query parameters.
        **kwargs: Additional arguments passed to requests.get.
    
    Returns:
        A requests.Response object.
    """
    session = get_retrying_session()
    logger.debug("GET %s (params=%s)", url, params)
    resp = session.get(url, params=params, timeout=60, **kwargs)
    resp.raise_for_status()
    return resp


def robust_post(url: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
    """
    Perform a POST request with automatic retry and exponential backoff.
    
    Args:
        url: The URL to post to.
        json_data: JSON payload.
        **kwargs: Additional arguments passed to requests.post.
    
    Returns:
        A requests.Response object.
    """
    session = get_retrying_session()
    logger.debug("POST %s (json=%s)", url, json_data)
    resp = session.post(url, json=json_data, timeout=60, **kwargs)
    resp.raise_for_status()
    return resp
