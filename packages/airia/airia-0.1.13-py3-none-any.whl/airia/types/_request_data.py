"""
Internal data structures for HTTP request preparation.

This module defines the data models used internally by the SDK clients
to organize and pass request information between methods.
"""
from typing import Any, Dict, Optional

from pydantic import BaseModel


class RequestData(BaseModel):
    """
    Structured container for HTTP request components.
    
    This internal data structure organizes all the components needed to make
    an HTTP request, including the URL, headers, payload, query parameters,
    and correlation ID for tracing.
    
    Attributes:
        url: The complete URL for the HTTP request
        payload: Optional JSON payload for the request body
        params: Optional query parameters to append to the URL
        headers: HTTP headers including authentication and content-type
        correlation_id: Unique identifier for request tracing and logging
    """
    url: str
    payload: Optional[Dict[str, Any]]
    params: Optional[Dict[str, Any]]
    headers: Dict[str, Any]
    correlation_id: str
