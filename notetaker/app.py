from notetaker.agents.interpretation import InterpretationAgent
from notetaker.agents.notetakeragent import NoteTaker
from notetaker.agents.reader import NoteTakerReader
from notetaker.tui import UserInterface
from notetaker.agents.writer import NoteTakerWriter


def app() -> None:
    # To load the dummy DB - will take a bit of time due to embedding computation
    # from notetaker.note_examples import load_into_db()
    # load_into_db()

    with UserInterface() as ui:
        interpretation = InterpretationAgent()
        reader = NoteTakerReader(ui, interpretation=interpretation)
        writer = NoteTakerWriter(ui, reader=reader, interpretation=interpretation)
        notetaker = NoteTaker(
            ui, writer=writer, reader=reader, interpretation=interpretation
        )
        while True:
            notetaker()

