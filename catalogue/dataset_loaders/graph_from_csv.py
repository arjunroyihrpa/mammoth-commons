import os.path

from mammoth.datasets import Graph_CSH
from mammoth.integration import loader


@loader(namespace="mauritzniklas", version="v001", python="3.11")
def data_graph_csv(
    path_nodes: str = "", path_edges: str = "", attributes: list[str] = []
) -> Graph_CSH:
    """This loads the nodes and edges of a graph."""
    import pandas as pd

    nodes = pd.read_csv(path_nodes)
    edges = pd.read_csv(path_edges)
    return Graph_CSH(nodes, edges, attributes)
