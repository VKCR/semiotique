# Note taker agent demo

## Running the app

To run the app, simply run main.py at the root of this repo.

You need to have an OpenRouter API key defined in your .env with the key "OPENROUTER_API_KEY".

The database used in the app is sqlite - it persists the DB in a local file called `notes.sqlite3`

If you wish to generate an example Note DB, uncomment the instructions at the top of app() function in app.py ; it will take a while to create the DB, due to embedding computation.

## Presentation

This is a demo of a "note-taking app". The app itself is very rudimentary, but the purpose of this demo is to showcase how one can build a "complex" app using the Semiotique paradigm. The value is in **reading the code**, moreso than using the app!

The app provides a TUI for reading / searching, and inserting / modifying a database of personal notes.

The underlying idea is that the app is _opinionated_, in the sense that certain workflows for querying the Note DB or modifying the Note DB follow "deterministic tactics", which combine both deterministic code and LLM-expression evaluation to search / refactor notes within deterministic guardrails (see Analysis section for more info).

## Code structure

The utils/ directory contain files related to the TUI, various helpers, model definitions, and db management.

In particular, the utils/models.py defines the Note class. Notes are characterized by their unique ID, possess a text content, can optionally belong to a list of categories, and can optionally be linked (bidirectionally) to other Notes.

The agents/ directory contains the various agent classes (in the Semiotique sense) which compose the note taker app
- notetakeragent.py => the high-level agent whose "agentic loop" is called in app.py to run the app. It dispatches user inputs to relevant sub-agents, and can show a help screen.
- reader.py => the sub-agent responsible for all tasks related to querying the Notes DB for information
- writer.py => the sub-agent responsible for all tasks related to insert / modifying / deleting Notes
- interpretation.py => a sub-agent which is re-used in various other agents, and which provides useful primitives for "interpretation" tasks

## Analysis

The interesting bits of code are to be found in the sub-agents reader.py, writer.py, and interpretation.py

The agents reader.py and writer.py translate a user prompts into a list of "operations" and executes them. Most of these operations are straightforward, and for these the paradigm of agentic loop + tools would have been perfectly fine. But certain operations implement "deterministic tactics" mixing deterministic code and LLM-expression evaluations, which would be harder to replicate with a simple agentic loop + tools.

These operations - which are of particular interest - are reader.search_notes, writer.insert_note, and writer.refactor_notes
- reader.search_notes : this method is called for vague queries, and tries to search the Note DB with the following tactics
  - First, it attempts to extract themes from the user prompt ; if it doesn't, it prompts the user to explicitly give themes
  - From the above themes, it first tries to match them to existing categories ; if any such categories are matched, it prompts the user if he wants to fetch the notes associated with that category
  - If the user refuses or no categories were deduced, then we combine a keyword search + an embedding search.
  - Finally, we ask the user if he wants the list of Notes, or a summary of them (unless the user already specified he wants a summary in his original prompt)
- writer.insert_note:
  - First, we determine the content of the Note, prompting the user if it's not clear
  - Then, we check whether a similar Note already exists. If one does, we prompt the user to choose between inserting the new note, abandoning the insertion, or refactoring the new note with the old (which calls in turn writer.refactor_notes)
  - If we do choose to insert, then we determine if there could be any relevant categories, or any relevant links to other Notes, and prompt the user to ask if he wants to add them.
- writer.refactor_note:
  - (If not skipped) We first build the refactoring prompt, by attempting to extract note_ids specified in the user prompt, or by attempting to search for relevant notes based on any themes extracted from the user prompt (leveraging reader.search_notes). Then, we use an LLM-expression evaluation to craft the refactoring prompt
  - We then enter a loop with message memory, where we use evaluate the refactoring prompt to determine the suggested changes to make ; we then prompt the user for feedback, and he can either ask for other changes, approve the changes, or cancel the refactoring.
  - Once changes are approved, we apply them. If any new notes are to be added which do not specify categories or links, we leverage writer.insert_note in order to benefit from its category and link suggestions.

All of the above operations show how the Semiotique framework can be leveraged to enmesh LLM-expression evaluations within deterministic code to do the following tasks:
- Routing / Classifying / Extraction tasks (which depends on understanding natural language)
- Using LLM-expression evaluations to craft prompts
- Branching based on LLM-expression evaluations
- Structured output based on LLM-expression evalution (refactored Notes)

All of the above operations also showcase how easy it is to keep a human-in-the-loop when using Semiotique framework.

Finally, the agent interpretation.py shows how "generic" operations can be re-used within other agents, and how they will be "steered" by the automatically curated agent context call stack (refer to the repo README to learn about this concept).

## Examples

With the example DB loaded:

> List all categories.

> Summarize the notes in category psychology.

> Show notes reading-002 and reading-003.

> Find notes containing the literal keyword reputation.

> Summarize what my notes say about conformity and social pressure.

> Find notes similar to people agreeing with a group despite private doubts.

> Add category sociology to note reading-002.

> Remove category sociology from note reading-002.

> Link notes reading-006 and reading-056.

> Show all notes connected to reading-008.

> Add a note: People may publicly agree with a group to avoid exclusion while privately disagreeing.

> Merge notes reading-006 and reading-008 into one note about reputation and trust in trade.
