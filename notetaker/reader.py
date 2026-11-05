from typing import Annotated, Literal

from pydantic import BaseModel, Field

from notetaker import notedb
from notetaker.models import Note
from notetaker.tui import UserInterface
from semiotique.agent import Agent
from semiotique.semiotique import S


class GetNoteByIds(BaseModel):
    kind: Literal["GET_NOTE_BY_IDS"]
    note_ids: list[str]


class GetCategories(BaseModel):
    kind: Literal["GET_CATEGORIES"]


class GetNoteIdsByCategory(BaseModel):
    kind: Literal["GET_NOTE_IDS_BY_CATEGORY"]
    category: str


class GetNoteIdsByKeyword(BaseModel):
    kind: Literal["GET_NOTE_IDS_BY_KEYWORD"]
    keyword: str


class GetLinkedNoteIds(BaseModel):
    kind: Literal["GET_LINKED_NOTE_IDS"]
    note_id: str


class GetSimilarNoteIds(BaseModel):
    kind: Literal["GET_SIMILAR_NOTE_IDS"]
    content: str


class SearchNotes(BaseModel):
    kind: Literal["SEARCH_NOTES"]
    theme: list[str] | None = None


ReadOperation = Annotated[
    GetNoteByIds
    | GetCategories
    | GetNoteIdsByCategory
    | GetNoteIdsByKeyword
    | GetLinkedNoteIds
    | GetSimilarNoteIds
    | SearchNotes,
    Field(discriminator="kind"),
]


class ReadRequest(BaseModel):
    operations: list[ReadOperation]


class NoteTakerReader(Agent[None]):
    """Handle all tasks related to querying the user's note knowledge base.

    Find relevant notes by content, categories, or semantic similarity, follow
    links between related notes, and answer questions using the stored knowledge.
    """

    def __init__(self, ui: UserInterface) -> None:
        self.ui = ui

    def __call__(self, prompt: str, **kwargs) -> None:
        request = S(
            "Extract the knowledge base read operations requested by the user "
            "as function tokens with their arguments. Use these operations:\n"
            "- GET_NOTE_BY_IDS(note_ids): retrieve notes by known IDs.\n"
            "- GET_CATEGORIES(): list all category names.\n"
            "- GET_NOTE_IDS_BY_CATEGORY(category): find IDs by exact category, "
            "including case.\n"
            "- GET_NOTE_IDS_BY_KEYWORD(keyword): find IDs by a literal, "
            "case-sensitive substring in note content. Call only when it is "
            "obvious that the user wants to search for a specific keyword.\n"
            "- GET_LINKED_NOTE_IDS(note_id): find all IDs connected to a known "
            "note, including indirect links.\n"
            "- GET_SIMILAR_NOTE_IDS(content): find IDs and similarity "
            "scores by semantic similarity to supplied text.\n"
            "- SEARCH_NOTES(theme=None): handle complex requests requiring "
            "exploration, synthesis, missing arguments, or operations that "
            "depend on earlier results. Set theme to a list of topics from the "
            "request when available; otherwise leave it null.\n"
            "Include multiple operations when requested. Only include operations "
            "whose arguments are available from the prompt; do not invent IDs, "
            "category names, or results of other operations. Return an empty "
            "operations list if no operation can be extracted. Extract only; "
            "do not execute operations or answer the prompt.\n\n"
            f"User prompt:\n{prompt}",
            output_type=ReadRequest,
        )
        notes: list[Note] = []
        for token in request.operations:
            match token:
                case GetNoteByIds():
                    notes.extend(self.get_note_by_ids(token))
                case GetCategories():
                    notes.extend(self.get_categories(token))
                case GetNoteIdsByCategory():
                    notes.extend(self.get_note_ids_by_category(token))
                case GetNoteIdsByKeyword():
                    notes.extend(self.get_note_ids_by_keyword(token))
                case GetLinkedNoteIds():
                    notes.extend(self.get_linked_note_ids(token))
                case GetSimilarNoteIds():
                    notes.extend(self.get_similar_note_ids(token))
                case SearchNotes():
                    notes.extend(self.search_notes(token))

    def get_note_by_ids(self, token: GetNoteByIds) -> list[Note]:
        self.ui.display(f"Getting notes by IDs for IDs: {token.note_ids}")
        return []

    def get_categories(self, token: GetCategories) -> list[Note]:
        self.ui.display("Getting all categories")
        return []

    def get_note_ids_by_category(self, token: GetNoteIdsByCategory) -> list[Note]:
        self.ui.display(f"Getting note IDs for category: {token.category}")
        return []

    def get_note_ids_by_keyword(self, token: GetNoteIdsByKeyword) -> list[Note]:
        self.ui.display(f"Getting note IDs for keyword: {token.keyword}")
        return []

    def get_linked_note_ids(self, token: GetLinkedNoteIds) -> list[Note]:
        self.ui.display(f"Getting linked note IDs for note ID: {token.note_id}")
        return []

    def get_similar_note_ids(self, token: GetSimilarNoteIds) -> list[Note]:
        self.ui.display(
            f"Getting similar note IDs for content: {token.content}"
        )
        return []

    def search_notes(self, token: SearchNotes) -> list[Note]:
        self.ui.display(
            f"Searching notes for themes: {token.theme}"
            if token.theme is not None
            else "Searching notes without a specific theme"
        )
        return []