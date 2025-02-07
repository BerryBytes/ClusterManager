import logging
import os

from pyparsing import Union
from models.common_response import ResponseModel
from typing import Any, List, Optional, Dict

from fastapi.responses import JSONResponse

def generate_response(success: bool, code: int, message: str, data: Union[List[Any], Any] = []) -> JSONResponse:
    response_content = {
        "success": success,
        "code": code,
        "message": message,
        "data": data
    }
    return JSONResponse(content=response_content, status_code=code)
def debug_response(data: any, message: Optional[str] = None, type: Optional[str] = None):
    if os.getenv("DEBUG", "false").lower() == "true":
        if type == "error":
            logging.error("Error occurs: %s, Message: %s", str(data), message)
        elif type == "info":
            logging.info("Debug data: %s, Message: %s", data, message)
        else:
            logging.debug("Debug data: %s", data)