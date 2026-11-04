from notetaker.tui import UserInterface
from semiotique.agent import Agent


class NoteTakerReader(Agent[None]):
    """Handle all tasks related to querying the user's note knowledge base.

    Find relevant notes by content, categories, or semantic similarity, follow
    links between related notes, and answer questions using the stored knowledge.
    """

    def __init__(self, ui: UserInterface) -> None:
        self.ui = ui

    def __call__(self, prompt: str, **kwargs) -> None:
        self.ui.display("reader not implemented yet")
