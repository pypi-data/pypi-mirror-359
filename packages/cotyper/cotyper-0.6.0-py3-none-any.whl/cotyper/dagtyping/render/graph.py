import networkx as nx
from netext import ConsoleGraph
from netext.edge_rendering.arrow_tips import ArrowTip
from netext.edge_rendering.modes import EdgeSegmentDrawingMode
from netext.edge_routing.modes import EdgeRoutingMode
from rich import get_console, print
from rich.panel import Panel

console = get_console()


def render_graph(graph: nx.DiGraph, render_edge_labels: bool = True) -> None:
    """

    Args:
        graph:
        render_edge_labels:

    Returns:

    """
    if render_edge_labels:
        edge_attributes = {}

        for u, v in graph.edges:
            parameter = graph.edges[u, v]["parameter"]
            edge_attributes[u, v] = {"$label": parameter.annotation.__name__}

        nx.set_edge_attributes(graph, edge_attributes)

    nx.set_edge_attributes(graph, ArrowTip.ARROW, "$end-arrow-tip")
    nx.set_edge_attributes(graph, EdgeRoutingMode.ORTHOGONAL, "$edge-routing-mode")
    nx.set_edge_attributes(
        graph, EdgeSegmentDrawingMode.BOX, "$edge-segment-drawing-mode"
    )

    term_graph = ConsoleGraph(graph, max_width=console.width)

    pad = (console.width - 2 - term_graph.max_width) // 2
    print(
        Panel(
            term_graph, title_align="center", title="Task DAG", padding=(1, 2, 1, pad)
        )
    )
