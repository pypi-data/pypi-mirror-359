from rich.style import Style
from rich.text import Text

ARGUMENT = Style(color="blue")
TYPE = Style(color="yellow", bold=True)
DEFAULT = Style(color="gray19")
DESCRIPTION = Style(color="gray42")


class Stylize:
    @staticmethod
    def _stylize(s: str | Text, style: Style) -> Text:
        if isinstance(s, str):
            return Text(s, style=style)
        elif isinstance(s, Text):
            s.stylize(style)
            return s
        else:
            raise NotImplementedError(type(s))

    @staticmethod
    def type(s: str | Text) -> Text:
        return Stylize._stylize(s, TYPE)

    @staticmethod
    def default(s: str | Text) -> Text:
        return Stylize._stylize(s, DEFAULT)

    @staticmethod
    def description(s: str | Text) -> Text:
        return Stylize._stylize(s, DESCRIPTION)

    @staticmethod
    def argument(s: str | Text) -> Text:
        return Stylize._stylize(s, ARGUMENT)
