import inspect
from collections import Counter, OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, TypeVar

import networkx as nx
from rich import get_console
from rich import print as rprint
from typer import Typer

from cotyper.dagtyping.render.graph import render_graph
from cotyper.log.progress import progress_task

print = rprint
console = get_console()


@dataclass
class DAGNode:
    function: Callable
    name: Optional[str] = None

    def __post_init__(self):
        self.name = self.name or self.function.__name__
        signature = inspect.signature(self.function)
        annotation = {
            param.name: param.annotation for param in signature.parameters.values()
        }

        def new_call(self, *args, **kwargs):
            return self.function(*args, **kwargs)

        new_call.__signature__ = signature
        new_call.__annotations__ = annotation
        new_call.__doc__ = self.function.__doc__
        new_call.__name__ = self.name

        setattr(self, "__call__", new_call)

    def __call__(self, *args, **kwargs):
        return progress_task(self.function)(*args, **kwargs)

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"<DAGNode {self.name} - {self.function.__name__} {inspect.signature(self.function)}>"

    def __str__(self):
        return f"{self.name}"


def dag_node_wrapper(name=None):
    def decorator(fn):
        return DAGNode(fn, name)

    return decorator


def dag_from_functions(
    *functions: Callable,
) -> Tuple[nx.DiGraph, Dict[DAGNode, List[inspect.Parameter]]]:
    graph = nx.DiGraph()
    outs = {}
    inputs = defaultdict(list)

    func_counter = Counter()

    for k, f in enumerate(functions):
        last = k == len(functions) - 1
        signature = inspect.signature(f)

        func_counter[f] += 1
        func_name = f.__name__
        func_name += str(func_counter[f] - 1) if func_counter[f] > 1 else ""
        node = DAGNode(f, func_name)

        for parameter in signature.parameters.values():
            t = parameter.annotation

            if t in outs:
                graph.add_edge(outs[t], node, parameter=parameter)

            else:
                inputs[node].append(parameter)
                # graph.add_edge(parameter.name, node, parameter=parameter)

        if not last:
            outs[signature.return_annotation] = node

    return graph, inputs


T = TypeVar("T")


def required_dag_nodes_to_signature(
    inputs: Dict[DAGNode, List[inspect.Parameter]], return_annotation: T
) -> inspect.Signature:
    input_parameters = OrderedDict()
    for node, parameters in inputs.items():
        for parameter in parameters:
            p = inspect.Parameter(
                name=f"{node.name}_{parameter.name}",
                kind=inspect._ParameterKind.KEYWORD_ONLY,
                default=parameter.default,
                annotation=parameter.annotation,
            )
            input_parameters[p.name] = p

    return inspect.Signature(
        list(input_parameters.values()), return_annotation=return_annotation
    )


def compose_function_from_dag(
    dag: nx.DiGraph, input_kwargs: Dict[DAGNode, List[inspect.Parameter]]
) -> Callable:
    longest_path = nx.dag_longest_path(dag)
    topological_generations = list(nx.topological_generations(dag))

    last_node = longest_path[-1]
    signature = required_dag_nodes_to_signature(
        input_kwargs, inspect.signature(last_node.function).return_annotation
    )

    def composed(**kwargs):
        arrow = "->"
        console.log(
            f"starting dag: {arrow.join([f'({arrow.join([n.name for n in nodes])})' for nodes in topological_generations])}"
        )
        console.log(kwargs)
        computed_kwargs = defaultdict(dict)

        result = None

        for gen in topological_generations:
            for node in gen:
                # fetch kwargs
                input_kwarg = {
                    p.name: kwargs[f"{node.name}_{p.name}"]
                    for p in input_kwargs.get(node, [])
                }
                computed_kwarg = computed_kwargs.get(node, {})
                node_kwargs = {**input_kwarg, **computed_kwarg}

                # call node
                result = node(**node_kwargs)

                # save output to every node in children with their parameter name
                for child_node, edge in dag._adj[node].items():
                    computed_kwargs[child_node][edge["parameter"].name] = result

        return result

    composed.__signature__ = signature
    composed.__annotations__ = {
        param.name: param.annotation for param in signature.parameters.values()
    }

    return composed


def compose(*functions: Callable) -> Callable:
    return compose_function_from_dag(*dag_from_functions(*functions))


def plot_digraph(graph: nx.DiGraph, required_arguments=None) -> None:
    if required_arguments is not None:
        # add required arguments to plotted graph
        @dag_node_wrapper("input_kwargs")
        def input_kwarg_func(*args, **kwargs):
            pass

        for node, params in required_arguments.items():
            for param in params:
                graph.add_edge(input_kwarg_func, node, parameter=param)

    print(render_graph(graph, True))


if __name__ == "__main__":

    def pow(x: int) -> int:
        return x**2

    def add(x: int, y: int) -> int:
        return x + y

    def div2(num: int) -> float:
        return num / 2

    def mul(lhs: float, rhs: int) -> float:
        return lhs * rhs

    functions = [pow, add, div2, mul]
    app = Typer()
    graph, args = dag_from_functions(*functions)
    plot_digraph(graph, args)
