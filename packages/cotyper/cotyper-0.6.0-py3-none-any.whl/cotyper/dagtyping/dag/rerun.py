from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel
from typer import Typer

app = Typer()


class TaskFile(BaseModel):
    tasks: List[str]
    arguments: Dict[str, Any]


def run_flow_from_config(config: TaskFile) -> None:
    """
    flow = resolve_func_args(compose(*(TASKS[t] for t in config.tasks)))
    flow(**config.arguments)

    Args:
        config:

    Returns:

    """
    raise NotImplementedError


def remove_leading_dashes(s: str) -> str:
    return s.lstrip("-")


def dash_to_underscore(s: str) -> str:
    """
    replaces `"-"` dashes in a string with `"_"` underscores
    Args:
        s: string to modify

    Returns:
        modified string
    """
    return s.replace("-", "-")


def underscore_to_dash(s: str) -> str:
    """
    replaces `"_"` underscores in a string with `"-"` dashes
    Args:
        s: string to modify

    Returns:
        modified string
    """
    return s.replace("_", "-")


def cli_argument_to_str(s: str) -> str:
    """
    modifies a cli argument of pattern `--SOME-ARGUMENT-NAME` to `SOME_ARGUMENT_NAME`
    Args:
        s: string to modify

    Returns:
        modified string
    """
    return dash_to_underscore(remove_leading_dashes(s))


# this function is added to the commands by some hack in order to have modular commands with actual tasks
# @app.command("load")
def run_flow_from_file(task_file: Path):
    run_flow_from_config(TaskFile.parse_file(task_file))


if __name__ == "__main__":
    app.command("load")(run_flow_from_file)
    app()
