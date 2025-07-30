"""
models/response.py

Defines a standard structure for all API responses to ensure consistency across endpoints.
"""

from typing import Optional
from pydantic import BaseModel

class ResponseWrapper(BaseModel):
    """
    A standardized response wrapper model for API responses.

    Attributes:
        status (int): The HTTP status code of the response (e.g., 200, 404, 500).
        success (bool): Indicates whether the request was processed successfully.
        message (str): A human-readable message describing the result.
        data (Optional[dict]): The payload returned by the API. Can be None if no data is available or on failure.
    """
    status: int
    success: bool
    message: str
    data: Optional[dict]
