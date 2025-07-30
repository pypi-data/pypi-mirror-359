import inspect
from typing import Callable, Dict, Tuple

from rich import get_console
from rich import print as rich_print
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cotyper.dagtyping.dag.rerun import run_flow_from_file
from cotyper.dagtyping.render.stylize_text import Stylize

print = rich_print

RENDER_GRAPH_CMD = "--display-graph"
HELP_CMD = "--help"
H_CMD = "-h"
LOAD_CMD = "load"

ARGUMENTS = (RENDER_GRAPH_CMD, HELP_CMD, H_CMD, LOAD_CMD)


def get_obj_doc(obj: object) -> Text:
    """
    get the documentation without args and returns
    Args:
        obj:

    Returns:

    """

    doc = inspect.getdoc(obj)
    if doc is None:
        return Text("MISSING DOCUMENTATION", style="red")

    return Text(doc)


def task_row(task_name: str, task_func: Callable) -> Tuple[Text, Text, Text]:
    """
    generates all columns for the task table based on given task name and its function
    Args:
        task_name: CLI name of the function
        task_func: function which will be called in the task

    Returns:
        column for the task table
    """
    sig = inspect.signature(task_func)

    parameter_str = (
        "("
        + ", ".join(
            (
                f"{param.name}: {param.annotation.__name__}"
                for param in sig.parameters.values()
            )
        )
        + ")"
    )

    return_str = str(sig.return_annotation.__name__)

    desc_col = Text(parameter_str + " -> " + return_str + "\n")
    styled_desc = Stylize.description(desc_col) + get_obj_doc(task_func) + Text("\n")

    return Stylize.argument(task_name), Stylize.type(str(task_func)), styled_desc


def argument_row(
    arg: str, t: str | None = None, description: str | None = None
) -> Tuple[Text, Text, Text]:
    """

    Args:
        arg:
        t: type
        description:

    Returns:

    """
    return (
        Stylize.argument(arg),
        Stylize.type(t or ""),
        Stylize.description(description or ""),
    )


def create_pygisnet_cover() -> Panel:
    """

    Returns:

    """
    lib_name = "DAGTyping"
    logo = """
   ┌─────┐
   │ DAG │
   └──┬──┘
      │
      ▼
   ┌─────────┐    ┌─────┐
   │ CoTyper ├───►│ NET │
   └─────────┘    └─────┘
"""
    logo_width = len(max(logo.split("\n"), key=len))

    console = get_console()
    pad = (console.width - 2 - logo_width) // 2

    return Panel(logo, title=lib_name, style="bold", padding=(1, 2, 1, pad))


def create_general_arg_help() -> Panel:
    """

    Returns:

    """
    general_argument_table = Table(
        show_header=False,
        show_lines=False,
        show_edge=False,
        show_footer=False,
        expand=True,
    )

    general_argument_table.add_row(
        *argument_row(f"{HELP_CMD} | {H_CMD}", None, "for help")
    )
    general_argument_table.add_row(
        *argument_row(RENDER_GRAPH_CMD, None, "to render the DAG in the terminal")
    )

    general_argument_table.add_row(
        *argument_row(
            LOAD_CMD,
            str(inspect.signature(run_flow_from_file)),
            "to load a task flow graph from a file",
        )
    )

    return Panel(general_argument_table, title="Arguments", title_align="left")


def create_task_help(tasks: Dict[str, Callable]) -> Panel:
    """

    Returns:

    """
    task_table = Table(
        show_header=False,
        show_lines=False,
        show_edge=False,
        show_footer=False,
        expand=True,
    )

    for task_name, task_func in tasks.items():
        task_table.add_row(*task_row(task_name, task_func))

    return Panel(task_table, title="Tasks", title_align="left")


def print_help(tasks: Dict[str, Callable]):
    """

    Returns:

    """
    print(
        Group(
            create_pygisnet_cover(), create_general_arg_help(), create_task_help(tasks)
        )
    )
