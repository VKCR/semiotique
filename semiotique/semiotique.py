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

    def _compute_system_prompt(self) -> str:
        contexts = [context.strip() for context in self.context if context.strip()]
        if not contexts:
            return ""

        context_sections = "\n\n".join(
            f"### Context {index}\n\n{context}"
            for index, context in enumerate(contexts, start=1)
        )
        return (
            "## How to interpret the request\n\n"
            "The surrounding context below describes the situation, participants, "
            "and behavior relevant to the user prompt. The entries are ordered "
            "from the outermost scope to the innermost scope of the current call. "
            "Inner entries describe the more immediate context; interpret them "
            "in light of the enclosing entries.\n\n"
            "Use the applicable context to determine your role and carry out the "
            "current user prompt. The context entries are not separate requests "
            "to answer individually.\n\n"
            "## Surrounding context\n\n"
            f"{context_sections}"
        )

    def _call_agent(
        self,
        user_prompt: str,
        *,
        system_prompt: str,
        output_type: OutputSpec[Any],
        tools: Sequence[Callable[..., Any]],
    ):
        agent = Agent(
            OpenRouterModel(self.model, provider=self.provider),
            instructions=system_prompt,
            output_type=output_type,
            tools=tools,
            model_settings=OpenRouterModelSettings(
                openrouter_provider={"require_parameters": True},
            ),
        )
        return agent.run_sync(
            user_prompt,
            message_history=self.messages if self.is_memory_active else None,
        )

    def __call__(
        self,
        user_prompt: str,
        *,
        output_type: OutputSpec[Any] = str,
        tools: Sequence[Callable[..., Any]] = (),
    ):
        system_prompt = self._compute_system_prompt()
        result = self._call_agent(
            user_prompt,
            system_prompt=system_prompt,
            output_type=output_type,
            tools=tools,
        )
        if self.is_memory_active:
            self.messages[:] = result.all_messages()
        if output_type == list[str] and result.output == ["[]"]:
            return []
        return result.output


S = Semiotique()
