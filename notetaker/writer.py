from typing import Literal

from pydantic import BaseModel

from notetaker import notedb
from notetaker.tui import UserInterface
from semiotique.agent import Agent
from semiotique.semiotique import S


class DeleteNote(BaseModel):
    kind: Literal["DELETE_NOTE"]
    note_id: str


class DeleteLink(BaseModel):
    kind: Literal["DELETE_LINK"]
    note_id_1: str
    note_id_2: str


class DeleteLinks(BaseModel):
    kind: Literal["DELETE_LINKS"]
    note_id: str


class DeleteCategory(BaseModel):
    kind: Literal["DELETE_CATEGORY"]
    note_id: str
    category: str


class DeleteCategories(BaseModel):
    kind: Literal["DELETE_CATEGORIES"]
    note_id: str


class InsertNote(BaseModel):
    kind: Literal["INSERT_NOTE"]
    content: str


class InsertCategories(BaseModel):
    kind: Literal["INSERT_CATEGORIES"]
    note_id: str
    categories: list[str]


class InsertLinks(BaseModel):
    kind: Literal["INSERT_LINKS"]
    links: list[tuple[str, str]]


class RefactorNotes(BaseModel):
    kind: Literal["REFACTOR_NOTES"]
    instructions: str


class NoteTakerWriter(Agent[None]):
    """Handle all tasks related to inserting, managing, and deleting personal notes.

    Create new notes, update existing content, merge or delete notes, organize categories, and manage
    links between related notes to maintain the user's personal knowledge base.
    """

    def __init__(self, ui: UserInterface) -> None:
        self.ui = ui

    def __call__(self, prompt: str, **kwargs) -> None:
        operations = self._extract_operations(prompt)
        for token in operations:
            match token:
                case DeleteNote():
                    self.delete_note(token)
                case DeleteLink():
                    self.delete_link(token)
                case DeleteLinks():
                    self.delete_links(token)
                case DeleteCategory():
                    self.delete_category(token)
                case DeleteCategories():
                    self.delete_categories(token)
                case InsertNote():
                    self.insert_note(token)
                case InsertCategories():
                    self.insert_categories(token)
                case InsertLinks():
                    self.insert_links(token)
                case RefactorNotes():
                    self.refactor_notes(token)

    def _extract_operations(
        self, prompt: str
    ) -> list[
        DeleteNote
        | DeleteLink
        | DeleteLinks
        | DeleteCategory
        | DeleteCategories
        | InsertNote
        | InsertCategories
        | InsertLinks
        | RefactorNotes
    ]:
        return S(
            "Extract the knowledge base write operations requested by the user "
            "as action tokens with their arguments. Use these operations:\n"
            "- DELETE_NOTE(note_id): delete a note.\n"
            "- DELETE_LINK(note_id_1, note_id_2): delete the link between two "
            "notes, preserving both notes.\n"
            "- DELETE_LINKS(note_id): delete all direct links of a note, "
            "preserving the notes.\n"
            "- DELETE_CATEGORY(note_id, category): remove one category "
            "assignment from a note, using the exact category name.\n"
            "- DELETE_CATEGORIES(note_id): remove all category assignments "
            "from a note, preserving the note.\n"
            "- INSERT_NOTE(content): create a new note with the supplied text.\n"
            "- INSERT_CATEGORIES(note_id, categories): assign the supplied list "
            "of category names to an existing note, preserving its current "
            "categories.\n"
            "- INSERT_LINKS(links): create bidirectional links between existing "
            "notes. Supply a list of pairs of known note IDs; each pair "
            "represents one link.\n"
            "- REFACTOR_NOTES(instructions): handle complex note management "
            "requests that the other operations cannot cover. Preserve the "
            "user's instructions; known note IDs are not required.\n"
            "Include only explicitly requested operations, in the requested "
            "order. Produce one token per distinct operation; do not produce "
            "duplicates, alternative strategies, or implicit cleanup steps. "
            "Prefer a specific operation when it fully handles a requested "
            "item with arguments available from the prompt. Otherwise use one "
            "REFACTOR_NOTES token covering the whole item, without additional "
            "tokens for intermediate steps of that same item. "
            "Only include operations whose arguments are available from the "
            "prompt. Do not invent note IDs, category names, note content, "
            "or results of other operations. Preserve partial editing requests "
            "as instructions for REFACTOR_NOTES. Return an empty list "
            "if no operation can be extracted. Extract only; do not execute "
            "operations or answer the prompt.\n\n"
            f"User prompt:\n{prompt}",
            output_type=list[
                DeleteNote
                | DeleteLink
                | DeleteLinks
                | DeleteCategory
                | DeleteCategories
                | InsertNote
                | InsertCategories
                | InsertLinks
                | RefactorNotes
            ],
        )

    def delete_note(self, token: DeleteNote) -> None:
        self.ui.display(f"Deleting note with ID: {token.note_id}")
        notedb.delete_note(token.note_id)

    def delete_link(self, token: DeleteLink) -> None:
        self.ui.display(
            f"Deleting link between note IDs: {token.note_id_1} and {token.note_id_2}"
        )
        notedb.delete_link(token.note_id_1, token.note_id_2)

    def delete_links(self, token: DeleteLinks) -> None:
        self.ui.display(f"Deleting all links for note ID: {token.note_id}")
        notedb.delete_links(token.note_id)

    def delete_category(self, token: DeleteCategory) -> None:
        self.ui.display(
            f"Deleting category '{token.category}' from note ID: {token.note_id}"
        )
        notedb.delete_category(token.note_id, token.category)

    def delete_categories(self, token: DeleteCategories) -> None:
        self.ui.display(f"Deleting all categories for note ID: {token.note_id}")
        notedb.delete_categories(token.note_id)

    def insert_categories(self, token: InsertCategories) -> None:
        if not notedb.get_note_by_ids([token.note_id]):
            self.ui.display(
                f"Cannot insert categories. Missing note IDs: {token.note_id}"
            )
            return

        self.ui.display(
            f"Inserting categories {token.categories} for note ID: {token.note_id}"
        )
        notedb.insert_categories(token.note_id, token.categories)

    def insert_links(self, token: InsertLinks) -> None:
        note_ids = sorted({note_id for link in token.links for note_id in link})
        existing_ids = {note.id for note in notedb.get_note_by_ids(note_ids)}
        missing_ids = [note_id for note_id in note_ids if note_id not in existing_ids]
        if missing_ids:
            self.ui.display(
                f"Cannot insert links. Missing note IDs: {', '.join(missing_ids)}"
            )
            return

        self.ui.display(f"Inserting links between note IDs: {token.links}")
        notedb.insert_links(token.links)

    def insert_note(self, token: InsertNote) -> None:
        self.ui.display(f"Inserting note with content: {token.content}")

    def refactor_notes(self, token: RefactorNotes) -> None:
        self.ui.display(f"Refactoring notes with instructions: {token.instructions}")
