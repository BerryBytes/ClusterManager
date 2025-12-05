"""Utility functions to generate API responses and debug logs."""

import logging
import os
from typing import Any, Dict, List, Optional

from fastapi.responses import JSONResponse
from models.common_response import ResponseModel
from pyparsing import Union


def generate_response(
    success: bool, code: int, message: str, data: Union[List[Any], Any] = []
) -> JSONResponse:
    """Generate a standardized JSON response for API endpoints.

    Args:
        success (bool): Whether the request was successful.
        code (int): HTTP status code.
        message (str): Response message.
        data (list|any): Response data payload.

    Returns:
        JSONResponse: FastAPI JSON response.
    """
    response_content = {
        "success": success,
        "code": code,
        "message": message,
        "data": data,
    }
    return JSONResponse(content=response_content, status_code=code)


def debug_response(
    data: any, message: Optional[str] = None, type: Optional[str] = None
):
    """Log debug information if DEBUG environment variable is enabled.

    Args:
        data (Any): Data to log.
        message (str, optional): Optional message to include.
        type (str, optional): Type of log ('error', 'info', or default 'debug').
    """
    if os.getenv("DEBUG", "false").lower() == "true":
        if type == "error":
            logging.error("Error occurs: %s, Message: %s", str(data), message)
        elif type == "info":
            logging.info("Debug data: %s, Message: %s", data, message)
        else:
            logging.debug("Debug data: %s", data)
