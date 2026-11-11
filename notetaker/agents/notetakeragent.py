from notetaker.agents.interpretation import InterpretationAgent
from notetaker.agents.reader import NoteTakerReader
from notetaker.tui import UserInterface
from notetaker.agents.writer import NoteTakerWriter
from semiotique.agent import Agent


class NoteTaker(Agent[None]):
    """Help the user manage their personal notes.

    Notes contain written content, an identifier, and a timestamp. Categories
    organize notes by topic, embeddings help find notes with similar meaning,
    and (bidirectional) links connect related notes into a personal knowledge base.
    """

    def __init__(
        self,
        ui: UserInterface,
        writer: NoteTakerWriter,
        reader: NoteTakerReader,
        interpretation: InterpretationAgent,
    ) -> None:
        """Initialize the interface and agents used to manage and retrieve notes."""
        self.ui = ui
        self.writer = writer
        self.reader = reader
        self.interpretation = interpretation

    def __call__(
        self, prompt: str = "\nWhat would you like to do with your notes?", **kwargs
    ) -> None:
        """Ask for an instruction and route it to the writer or reader agent.

        Report unrecognized or unclear instructions to the user.
        """
        instruction = self.ui.ask(prompt)
        instruction_type = self.interpretation.classify_choice(
            instruction,
            choices={
                "Writer": (
                    "Note management: creating, updating, merging, deleting, "
                    "categorizing, or linking notes."
                ),
                "Reader": (
                    "Querying the note knowledge base: finding or retrieving "
                    "notes, exploring related notes, or answering questions "
                    "using stored notes."
                ),
                "Other": (
                    "Instructions outside reader and writer responsibilities "
                    "or with unclear intent."
                ),
            },
            default="Other",
        )
        if instruction_type == "Writer":
            self.writer(instruction)
        elif instruction_type == "Reader":
            self.reader(instruction)
        else:
            self.ui.display("I didn't understand the instruction.")
