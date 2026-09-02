from __future__ import annotations

from typing import Any

from models import ResponseModel, TextResponse
from openai_tools import create_client, parse_response


class LLM:
    """A configured LLM, ready to be evaluated on any input."""

    def __init__(
            self,
            *,
            api_key: str,
            model: str,
            reasoning_effort: str,
            instructions: str,
    ) -> None:
        self.client = create_client(api_key)
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.instructions = instructions

    def E(self, input: Any, text_format: type[ResponseModel] = TextResponse) -> ResponseModel:
        """Evaluate the model on `input`, returning the parsed output."""

        response = parse_response(
            self.client,
            model=self.model,
            instructions=self.instructions,
            input=input,
            reasoning={"effort": self.reasoning_effort},
            text_format=text_format,
        )

        return response.output_parsed.response
