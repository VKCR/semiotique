from __future__ import annotations

from pydantic import BaseModel, Field


class TextResponse(BaseModel):
    """A plain-text answer, with no additional structure."""

    response: str = Field(description="Plain-text response")


class BoolResponse(BaseModel):
    """A yes/no answer."""

    response: bool = Field(description="True or false response")


class IntResponse(BaseModel):
    """A whole-number answer."""

    response: int = Field(description="Integer response")


class FloatResponse(BaseModel):
    """A numeric answer."""

    response: float = Field(description="Number response")


class TextListResponse(BaseModel):
    """A list of plain-text answers."""

    response: list[str] = Field(description="List of plain-text responses")
