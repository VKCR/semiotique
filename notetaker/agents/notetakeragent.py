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
        self,
        prompt: str = "\nWhat would you like to do with your notes? (Type help for a manual.)",
        **kwargs,
    ) -> None:
        """Ask for an instruction and route it to writing, reading, or help.

        Report unrecognized or unclear instructions to the user.
        """
        instruction = self.ui.ask(prompt)
        instruction_type = self.interpretation.classify_choice(
            instruction,
            choices={
                "help": (
                    "Help using the note-taking app: show the user manual, "
                    "explain available features, or explain how to perform "
                    "an action. Examples: 'help', 'what can I do?', or "
                    "'how do I create a note?'."
                ),
                "Writer": (
                    "Requests to perform note management: creating, updating, "
                    "merging, deleting, categorizing, or linking notes. "
                    "Requests for instructions on using the app belong to help."
                ),
                "Reader": (
                    "Querying the note knowledge base: finding or retrieving "
                    "notes, exploring related notes, or answering questions "
                    "using stored notes. Requests for instructions on using "
                    "the app belong to help."
                ),
                "Other": (
                    "Instructions outside reader, writer, and help responsibilities "
                    "or with unclear intent."
                ),
            },
            default="Other",
        )
        if instruction_type == "help":
            self.help()
        elif instruction_type == "Writer":
            self.writer(instruction)
        elif instruction_type == "Reader":
            self.reader(instruction)
        else:
            self.ui.display("I didn't understand the instruction.")

    def help(self) -> None:
        """Display the user manual in short pages within the TUI."""
        pages = (
            "USER MANUAL (1/4) - Getting started\n"
            "Type requests in plain language and press Enter to submit.\n"
            "Use Backspace to correct your input.\n"
            "Each note has an ID, text, optional categories, and links.\n"
            "Use the IDs shown in results when referring to specific notes.\n"
            "Create: 'Add a note: Sleep helps memory.'\n"
            "Or say 'Add a new note' and enter its content when asked.\n"
            "For similar notes, choose abandon, integrate, or insert separately.\n"
            "Suggested categories and links are added only if you approve.",
            "USER MANUAL (2/4) - Finding and reading notes\n"
            "Retrieve by ID: 'Show note <note_id>.'\n"
            "Search by topic: 'Find my notes about sleep.'\n"
            "Search by meaning: 'Find notes similar to getting enough rest.'\n"
            "Search by keyword: 'Find notes containing the keyword Sleep.'\n"
            "Keyword matching is literal and case-sensitive.\n"
            "By category: 'Show notes in category Health.'\n"
            "Explore links: 'Show notes connected to <note_id>.'\n"
            "Ask for a summary in your request, or choose full content when asked.",
            "USER MANUAL (3/4) - Organizing notes\n"
            "Replace <note_id>, <first_id>, and <second_id> with actual IDs.\n"
            "List categories: 'List all categories.'\n"
            "Assign: 'Add category Health to note <note_id>.'\n"
            "Remove one: 'Remove category Health from note <note_id>.'\n"
            "Remove all: 'Remove all categories from note <note_id>.'\n"
            "Link: 'Link notes <first_id> and <second_id>.'\n"
            "Unlink: 'Remove the link between <first_id> and <second_id>.'\n"
            "Remove all links: 'Remove all links from note <note_id>.'\n"
            "Links work in both directions; unlinking preserves the notes.",
            "USER MANUAL (4/4) - Editing and deleting\n"
            "Edit: 'Update note <note_id> to say: Sleep supports learning.'\n"
            "Merge: 'Merge my notes about sleep into one coherent note.'\n"
            "Review proposed revisions, then approve, request changes, or cancel.\n"
            "Delete: 'Delete note <note_id>.'\n"
            "Direct deletion also removes its categories and links,\n"
            "and takes effect without a confirmation prompt.\n"
            "Answer follow-up questions to supply missing details.\n"
            "Type 'help' at the main prompt to open this manual again.\n"
            "Press Ctrl-D with an empty input to exit the app.",
        )
        for index, page in enumerate(pages):
            self.ui.display(page)
            if index < len(pages) - 1:
                response = self.ui.ask(
                    "Press Enter for the next page, or type q to close help."
                )
                if response.strip().lower() == "q":
                    return
