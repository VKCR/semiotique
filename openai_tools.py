from __future__ import annotations

from typing import Any

from openai import OpenAI

def create_client(api_key: str) -> OpenAI:
    """Create an OpenAI client for backend API calls."""
    return OpenAI(api_key=api_key)


def parse_response(
        client: OpenAI,
        *,
        model: str,
        instructions: str,
        input: Any,
        reasoning: dict[str, Any] | None = None,
        text_format: Any | None = None,
) -> Any:
    """Call the OpenAI Responses API parse helper."""

    response = client.responses.parse(
        model=model,
        instructions=instructions,
        input=input,
        reasoning=reasoning,
        text_format=text_format,
    )

    return response


