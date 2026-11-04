import curses
import textwrap


class UserInterface:
    """A scrolling output area and a bottom input bar.

    Usage:
        with UserInterface() as ui:
            ui.display("Welcome!")
            instruction = ui.ask("What would you like to do?")
    """

    def __init__(self) -> None:
        self._screen = None
        self._messages: list[str] = []

    def __enter__(self) -> "UserInterface":
        self._screen = curses.initscr()
        try:
            curses.noecho()
            curses.cbreak()
            self._screen.keypad(True)
            self._draw()
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            self._screen.keypad(False)
            curses.nocbreak()
            curses.echo()
        finally:
            curses.endwin()
            self._screen = None

    def display(self, message: str) -> None:
        """Append a message to the main screen."""
        self._messages.append(message)
        self._draw()

    def ask(self, message: str) -> str:
        """Display a prompt and wait for the user to submit a line."""
        self.display(message)
        value = ""
        while True:
            self._draw(value)
            key = self._screen.get_wch()
            if key in ("\n", "\r", curses.KEY_ENTER):
                self.display(f"> {value}")
                return value
            if key == "\x04" and not value:
                raise EOFError
            if key in (curses.KEY_BACKSPACE, "\b", "\x7f"):
                value = value[:-1]
            elif isinstance(key, str) and key.isprintable():
                value += key

    def _draw(self, value: str | None = None) -> None:
        if self._screen is None:
            raise RuntimeError("Use UserInterface inside a 'with' block.")

        height, width = self._screen.getmaxyx()
        self._screen.erase()
        # Leave the last column unused to avoid curses' bottom-right error.
        usable_width = max(1, width - 1)
        lines = []
        for message in self._messages:
            for line in message.split("\n"):
                lines.extend(textwrap.wrap(line, usable_width) or [""])

        output_height = max(0, height - 2)
        if output_height:
            for row, line in enumerate(lines[-output_height:]):
                self._screen.addnstr(row, 0, line, usable_width)

        if height >= 2 and width >= 2:
            self._screen.addnstr(height - 2, 0, "─" * usable_width, usable_width)
            if value is not None:
                input_width = max(0, usable_width - 2)
                visible_value = value[-input_width:] if input_width else ""
                bar = ("> " + visible_value)[:usable_width]
                self._screen.addnstr(height - 1, 0, bar, usable_width)
                self._screen.move(height - 1, min(len(bar), width - 1))

        self._screen.refresh()
