from abc import ABC, abstractmethod
from functools import wraps
from inspect import isfunction

from semiotique.semiotique import S


def _with_agent_context(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        S.push_context(self.__doc__ or "")
        try:
            return method(self, *args, **kwargs)
        finally:
            S.pop_context()

    return wrapper


class Agent(ABC):
    """Base class for building agents.

    Subclasses should override this docstring with a description of the agent's behavior.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, method in list(cls.__dict__.items()):
            if isfunction(method):
                setattr(cls, name, _with_agent_context(method))

    @abstractmethod
    def __call__(self, prompt: str, **kwargs) -> None:
        """Interpret the prompt, optionally using the supplied keyword arguments."""
        pass
