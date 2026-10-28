import os
from contextlib import contextmanager
from collections.abc import Iterator

from dotenv import load_dotenv
from openrouter import OpenRouter
from pydantic import create_model


class Semiotique:
    def __init__(self):
        load_dotenv()
        self.client = OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY"))
        self.model = "openai/gpt-6-luna"
        self.context: list[str] = []

    def _push_context(self, context: str) -> None:
        self.context.append(context)

    def _pop_context(self) -> None:
        if not self.context:
            raise IndexError("Cannot pop context from an empty context stack")
        self.context.pop()

    @contextmanager
    def with_context(self, context: str) -> Iterator[None]:
        self._push_context(context)
        try:
            yield
        finally:
            self._pop_context()

    def __call__(self, value: str, *, output_type: type = str):
        if not isinstance(output_type, type):
            raise TypeError("output_type must be a type")

        system_prompt = "\n\n".join(self.context)

        # An object envelope supports scalar, collection, and custom output types.
        output_model = create_model("Output", value=(output_type, ...))
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "output",
                "schema": output_model.model_json_schema(),
            },
        }

        response = self.client.chat.send(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": value},
            ],
            response_format=response_format,
            provider={"require_parameters": True},
        )
        if not response.choices or response.choices[0].message.content is None:
            raise ValueError("OpenRouter returned no text output")

        content = response.choices[0].message.content
        return output_model.model_validate_json(content).value


S = Semiotique()
