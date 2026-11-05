import os
from contextlib import contextmanager
from collections.abc import Callable, Iterator, Sequence
from typing import Any

import pydantic_ai
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings
from pydantic_ai.output import OutputSpec
from pydantic_ai.providers.openrouter import OpenRouterProvider


class Semiotique:
    def __init__(self):
        load_dotenv()
        pydantic_ai.BANNER_ENABLED = False
        self.provider = OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"))
        self.model = "openai/gpt-6-luna"
        self.context: list[str] = []
        self.messages: list[ModelMessage] = []
        self.is_memory_active: bool = False

    def _push_context(self, context: str) -> None:
        self.context.append(context)

    def _pop_context(self) -> None:
        if not self.context:
            raise IndexError("Cannot pop context from an empty context stack")
        self.context.pop()

    @contextmanager
    def with_context(self, context: str) -> Iterator[None]:
        # Prevent duplicate context when an Agent's method calls another method of the same Agent.
        if self.context and self.context[-1] == context:
            yield
            return

        self._push_context(context)
        try:
            yield
        finally:
            self._pop_context()

    @contextmanager
    def with_memory(self) -> Iterator[None]:
        if self.is_memory_active:
            raise RuntimeError("Cannot nest with_memory contexts")
        self.is_memory_active = True
        try:
            yield
        finally:
            self.is_memory_active = False
            self.messages.clear()

    def __call__(
        self,
        value: str,
        *,
        output_type: OutputSpec[Any] = str,
        tools: Sequence[Callable[..., Any]] = (),
    ):
        system_prompt = "\n\n".join(self.context)

        agent = Agent(
            OpenRouterModel(self.model, provider=self.provider),
            instructions=system_prompt,
            output_type=output_type,
            tools=tools,
            model_settings=OpenRouterModelSettings(
                openrouter_provider={"require_parameters": True},
            ),
        )
        result = agent.run_sync(
            value,
            message_history=self.messages if self.is_memory_active else None,
        )
        if self.is_memory_active:
            self.messages[:] = result.all_messages()
        return result.output


S = Semiotique()
