from typing import Any

from pydantic import BaseModel


__all__ = (
    "SuccessResponse",
    "FailedResponse",
)


class ResponseBase(BaseModel):
    success: bool


class SuccessResponse(ResponseBase):
    success: bool = True
    data: Any


class FailedResponse(ResponseBase):
    success: bool = False
    message: str
