import os

from dotenv import load_dotenv
from openrouter import OpenRouter
from pydantic import create_model


class Semiotique:
    def __init__(self):
        load_dotenv()
        self.client = OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY"))
        self.model = "openai/gpt-5.6-luna"

    def __call__(self, value: str, *, output_type: type = str):
        if not isinstance(output_type, type):
            raise TypeError("output_type must be a type")

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
            messages=[{"role": "user", "content": value}],
            response_format=response_format,
            provider={"require_parameters": True},
        )
        if not response.choices or response.choices[0].message.content is None:
            raise ValueError("OpenRouter returned no text output")

        content = response.choices[0].message.content
        return output_model.model_validate_json(content).value


S = Semiotique()
