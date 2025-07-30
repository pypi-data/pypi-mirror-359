import sys
from typing import Callable, Dict, List

from cotyper.dagtyping.dag.compose import dag_from_functions
from cotyper.dagtyping.dag.help import RENDER_GRAPH_CMD
from cotyper.dagtyping.render.graph import render_graph


def modify_sys_args(tasks: List[Callable]) -> None:
    sys.argv = [sys.argv[0]] + sys.argv[len(tasks) + 1 :]


def parse_task_funcs(task_dict: Dict[str, Callable]) -> List[Callable]:
    tasks: List[Callable] = []

    for arg in sys.argv[1:]:
        if arg in task_dict.keys():
            tasks.append(task_dict[arg])

    modify_sys_args(tasks)
    return tasks


def render_graph_if_needed(tasks: List[Callable]) -> None:
    if RENDER_GRAPH_CMD in sys.argv:
        graph, _ = dag_from_functions(*tasks)
        render_graph(graph)
        sys.argv.remove(RENDER_GRAPH_CMD)
        if len(sys.argv) < 2:
            sys.exit()
