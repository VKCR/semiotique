# Note taker agent demo
## Presentation
This is a demo of a "note-taking app". The app itself is very rudimentary, but the purpose of this demo is to showcase how one can build a "complex" app using the Semiotique paradigm.

This app is a TUI for reading / searching, and inserting / modifying Notes. 

Notes are characterized by their unique ID, possess a text content, can optionally belong to a list of categories, and can optionally be linked (bidirectionally) to other Notes. 

The 


Sections: 
- Presentation, and how to run it
- Explanation of how it works (and the code organization, and especially where the important code resides)
- Analysis
  - Especially compare it to agentic loop
  - Structured flow for integrating new notes, and for searching vagues notes

Notes:
- README : emphasize the SMART and TANGLED (human in the loop) nature of the app, and how it makes it differ from the standard agent loop + tools
  - Emphasize the "action token" paradigm I have introduced, which inverts the agentic loop, giving you the ability to run deterministic code between different "tool calls" (or rather decision by the agent of what methods to run)
    - Give some usage examples
    - Complex querying
    - Adding a new note, with the category / link flow
    - Merge all notes relevant to language
