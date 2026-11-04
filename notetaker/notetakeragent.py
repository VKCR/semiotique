from enum import Enum

from notetaker.reader import NoteTakerReader
from notetaker.tui import UserInterface
from notetaker.writer import NoteTakerWriter
from semiotique.agent import Agent
from semiotique.semiotique import S


class InstructionType(str, Enum):
    WRITER = "Writer"
    READER = "Reader"
    OTHER = "Other"


class NoteTaker(Agent[None]):
    """Help the user manage their personal notes.

    Notes contain written content, an identifier, and a timestamp. Categories
    organize notes by topic, embeddings help find notes with similar meaning,
    and (bidirectional) links connect related notes into a personal knowledge base.
    """

    def __init__(
        self, ui: UserInterface, writer: NoteTakerWriter, reader: NoteTakerReader
    ) -> None:
        self.ui = ui
        self.writer = writer
        self.reader = reader

    def __call__(
        self, prompt: str = "What would you like to do with your notes?", **kwargs
    ) -> None:
        instruction = self.ui.ask(prompt)
        instruction_type = S(
            "Classify the user's instruction. Choose Writer for note management "
            "such as creating, updating, merging, deleting, categorizing, or linking "
            "notes. Choose Reader for querying the note knowledge base, such as "
            "finding or retrieving notes, exploring related notes, or answering "
            "questions using stored notes. Choose Other if the instruction does "
            "not fit either responsibility or its intent is unclear.\n\n"
            f"User instruction:\n{instruction}",
            output_type=InstructionType,
        )
        if instruction_type == InstructionType.WRITER:
            self.writer(instruction)
        elif instruction_type == InstructionType.READER:
            self.reader(instruction)
        else:
            self.ui.display("I didn't understand the instruction.")
