from enum import Enum

from notetaker import notedb
from notetaker.tui import UserInterface
from semiotique.agent import Agent
from semiotique.semiotique import S


class QueryType(str, Enum):
    SPECIFIC = "Specific"
    VAGUE = "Vague"


class NoteTakerReader(Agent[None]):
    """Handle all tasks related to querying the user's note knowledge base.

    Find relevant notes by content, categories, or semantic similarity, follow
    links between related notes, and answer questions using the stored knowledge.
    """

    def __init__(self, ui: UserInterface) -> None:
        self.ui = ui

    def __call__(self, prompt: str, **kwargs) -> None:
        query_type = S(
            "Classify the user's prompt. Choose Specific if it can be directly "
            "translated into exactly one of these knowledge base read functions "
            "with arguments available from the prompt:\n"
            "- get_all_note_ids(): list all note IDs.\n"
            "- get_note_by_ids(note_ids): retrieve notes by known IDs.\n"
            "- get_categories(): list all category names.\n"
            "- get_note_ids_by_category(category): find IDs by exact category.\n"
            "- get_note_ids_by_keyword(keyword): find IDs by a literal, "
            "case-sensitive substring in note content.\n"
            "- get_linked_note_ids(note_id): find all IDs connected to a known "
            "note, including indirect links.\n"
            "- get_similar_note_ids(note_id, n=10): find notes semantically "
            "similar to a known note.\n\n"
            "Choose Vague if the prompt requires interpretation, exploration, "
            "synthesis, multiple read operations, or missing arguments. "
            "Classify only; do not answer the prompt.\n\n"
            f"User prompt:\n{prompt}",
            output_type=QueryType,
        )
        if query_type == QueryType.SPECIFIC:
            self.fallback(prompt)
        else:
            self.query(prompt)

    def query(self, prompt: str) -> None:
        self.ui.display("query not implemented yet")

    def fallback(self, prompt: str) -> None:
        self.ui.display("Falling back to reader.fallback")
        with S.with_context(
            "Query the user's note knowledge base using the available read tools "
            "to answer the user's prompt. Retrieve relevant notes and base your "
            "answer on their content. If the knowledge base does not contain "
            "enough information, explain what is missing."
        ):
            response = S(
                prompt,
                tools=[
                    notedb.get_note_by_ids,
                    notedb.get_categories,
                    notedb.get_note_ids_by_category,
                    notedb.get_note_ids_by_keyword,
                    notedb.get_linked_note_ids,
                    notedb.get_similar_note_ids,
                ],
            )
        self.ui.display(response)
