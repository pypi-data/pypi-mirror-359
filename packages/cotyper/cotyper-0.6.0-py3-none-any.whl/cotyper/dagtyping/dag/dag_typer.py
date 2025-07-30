import sys
from typing import Callable, Dict, Iterable, Optional

from cotyper.dagtyping.dag.compose import compose
from cotyper.dagtyping.dag.help import H_CMD, HELP_CMD, print_help
from cotyper.dagtyping.dag.parse import parse_task_funcs, render_graph_if_needed
from cotyper.parser.app import App


class DAGApp:
    def __init__(self, name: Optional[str] = None):
        self._typer = App(name=name)
        self.commands: Dict[str, Callable] = {}

    def command(self, name: Optional[str] = None):
        def decorator(fn: Callable):
            self.register_command(name=name, callback=fn)
            return fn

        return decorator

    def add_commands(self, *fn: Callable) -> Iterable[Callable]:
        for f in fn:
            self.command()(f)
        return fn

    def register_command(self, name: Optional[str] = None, *, callback: Callable):
        self.commands[name or callback.__name__.replace("_", "-")] = callback

    def display_help_if_needed(self):
        if len(sys.argv) <= 2 and any(arg in (HELP_CMD, H_CMD) for arg in sys.argv):
            print_help(self.commands)
            sys.exit()

    def __call__(self, *args, **kwargs):
        tasks = parse_task_funcs(self.commands)

        # eventually run help
        self.display_help_if_needed()

        # display graph if required
        render_graph_if_needed(tasks)

        # actually add composed tasks to the typer app
        self._typer.struct_command("composed")(compose(*tasks))

        self._typer()
