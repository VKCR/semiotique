from notetaker.notetakeragent import NoteTaker
from notetaker.reader import NoteTakerReader
from notetaker.tui import UserInterface
from notetaker.writer import NoteTakerWriter


def app() -> None:
    # To load the dummy DB - will take a bit of time due to embedding computation
    # from notetaker.note_examples import load_into_db()
    # load_into_db()

    with UserInterface() as ui:
        writer = NoteTakerWriter(ui)
        reader = NoteTakerReader(ui)
        notetaker = NoteTaker(ui, writer=writer, reader=reader)
        while True:
            notetaker()

