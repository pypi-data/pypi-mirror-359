"""
    Adds wire length computation
"""

import queue
import pandas as pd
import lc_reconstruction_analysis.utils as utils


def add_all_wire_lengths(dataDF, graphs):
    """
    compute wire length for all cells
    """
    for name in dataDF["Graph"]:
        graphs[name] = add_wire_length(graphs[name])
    return graphs


def add_wire_length(graph):
    """
    Add wire length calculation to each node
    graph = axon.add_wire_length(graph)
    """
    graph.nodes[1]["wire_length"] = 0
    node_queue = queue.Queue()
    node_queue.put(1)
    while not node_queue.empty():
        node = node_queue.get()
        edges = dict(graph[node])
        for k in edges.keys():
            graph.nodes[k]["wire_length"] = (
                graph.nodes[node]["wire_length"] + edges[k]["weight"]
            )
            node_queue.put(k)
    return graph


def build_branch_table(graph):
    """
    Builds a dataframe of nodes with columns:
        node #
        branch segment
        parent for that node
        wire length
    Builds a dataframe of branch segments with columns:
        parent
        min_length
        max_length
    """
    if "wire_length" not in graph.nodes[1]:
        raise Exception("Need to compute wire length first")

    branch_num = 1
    axon_tree = utils.get_subgraph(graph, "structure_id", [1, 2])
    results, successors = build_branch_table_inner(axon_tree, 1, branch_num, 1)
    branch_num = 2
    while len(successors) != 0:
        this_result, this_successors = build_branch_table_inner(
            axon_tree, successors[0][1], branch_num, successors[0][0]
        )
        results = results + this_result
        successors = successors[1:] + this_successors
        branch_num += 1
    node_df = pd.DataFrame(
        results, columns=["node", "branch", "parent", "wire_length"]
    )
    branch_df = pd.DataFrame()
    branch_df["parent"] = node_df.groupby("branch")["parent"].first()
    branch_df["min_length"] = [
        graph.nodes[x["parent"]]["wire_length"]
        for _, x in branch_df.iterrows()
    ]
    branch_df["max_length"] = node_df.groupby("branch")["wire_length"].max()
    return node_df, branch_df


def build_branch_table_inner(graph, node, branch_number, parent):
    """
    Recursive function to build table of branch segments
    node, the current node
    branch_number, the current branch segment
    parent, the connection point for this branch segment

    returns
        results, a list of tuples
            Each tuple is (node, branch number, parent, wire length)
        successors, a list of tuples
            Each tuple is (parent, node)
    """
    if graph.out_degree(node) == 0:
        return [
            (node, branch_number, parent, graph.nodes[node]["wire_length"])
        ], []
    elif graph.out_degree(node) > 1:
        successors = [(node, x) for x in list(graph.successors(node))]
        return [
            (node, branch_number, parent, graph.nodes[node]["wire_length"])
        ], successors
    else:
        next_node = list(graph.successors(node))[0]
        results, successors = build_branch_table_inner(
            graph, next_node, branch_number, parent
        )
        return [
            (node, branch_number, parent, graph.nodes[node]["wire_length"])
        ] + results, successors
