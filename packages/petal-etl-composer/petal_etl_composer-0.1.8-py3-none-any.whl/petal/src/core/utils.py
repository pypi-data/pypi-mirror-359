from collections import defaultdict, deque


def topological_sort(edges: set[tuple[str, str]]) -> list[str]:
    """
    Perform topological sort on a list of edges.
    Returns a list of node ids in topological order.
    Raises ValueError if a cycle is detected.
    """
    graph = defaultdict(set)
    in_degree = defaultdict(int)

    # Build the graph
    nodes = set()
    for src, dst in edges:
        graph[src].add(dst)
        in_degree[dst] += 1
        nodes.update([src, dst])

    for node in nodes:
        in_degree.setdefault(node, 0)

    # Start with nodes that have zero in-degree
    queue = deque([n for n in nodes if in_degree[n] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(nodes):
        raise ValueError("Graph contains a cycle")

    return result


def is_dag(edges: set[tuple[str, str]]) -> bool:
    """
    Returns True if the graph is a DAG (no cycles), else False.
    """
    try:
        topological_sort(edges)
        return True
    except ValueError:
        return False
