from notetaker.tui import UserInterface
from semiotique.agent import Agent


class NoteTakerWriter(Agent[None]):
    """Handle all tasks related to inserting, managing, and deleting personal notes.

    Create new notes, update existing content, merge or delete notes, organize categories, and manage
    links between related notes to maintain the user's personal knowledge base.
    """

    def __init__(self, ui: UserInterface) -> None:
        self.ui = ui

    def __call__(self, prompt: str, **kwargs) -> None:
        self.ui.display("writer not implemented yet")
