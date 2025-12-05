"""Response model for API outputs."""
from typing import Any, List, Optional, Union

from pydantic import BaseModel  # type: ignore


class ResponseModel(BaseModel):
    """Standard API response structure."""

    code: int
    error_code: int
    message: str
    data: Union[List[Any], Any] = []
