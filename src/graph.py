"""Module for building dependency graph using recursive BFS."""

from typing import Optional


def build_dependency_graph(
    start_package: str,
    get_dependencies_func,
) -> dict[str, list[str]]:
    """Build dependency graph using recursive BFS.

    Args:
        start_package: Starting package name.
        get_dependencies_func: Function that returns dependencies.

    Returns:
        Dictionary mapping package names to their dependencies.
    """
    graph = {}
    visited = set()

    def _bfs_recursive(current_level: list[str]) -> None:
        """Recursively process BFS level by level."""
        if not current_level:
            return

        next_level = []
        for package in current_level:
            if package in visited:
                continue
            visited.add(package)
            dependencies = get_dependencies_func(package)
            graph[package] = dependencies
            for dep in dependencies:
                if dep not in visited:
                    next_level.append(dep)

        _bfs_recursive(next_level)

    _bfs_recursive([start_package])
    return graph


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect cycles in dependency graph using DFS.

    Args:
        graph: Dependency graph as adjacency list.

    Returns:
        List of cycles found (each cycle is a list of package names).
    """
    cycles = []
    visited = set()
    rec_stack = set()

    def _dfs(node: str, path: list[str]) -> None:
        """Recursive DFS to find cycles."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                _dfs(neighbor, path)
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            _dfs(node, [])

    return cycles


def get_transitive_dependencies(
    start_package: str,
    get_dependencies_func,
) -> set[str]:
    """Get all transitive dependencies using recursive BFS.

    Args:
        start_package: Starting package name.
        get_dependencies_func: Function that returns dependencies.

    Returns:
        Set of all transitive dependency names.
    """
    visited = set()

    def _bfs_recursive(current_level: list[str]) -> None:
        """Recursively collect dependencies level by level."""
        if not current_level:
            return

        next_level = []
        for package in current_level:
            if package in visited:
                continue
            visited.add(package)
            for dep in get_dependencies_func(package):
                if dep not in visited:
                    next_level.append(dep)

        _bfs_recursive(next_level)

    _bfs_recursive([start_package])
    visited.discard(start_package)
    return visited


def _build_reverse_graph(
    graph: dict[str, list[str]],
) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Build reverse graph and compute in-degrees.

    Args:
        graph: Dependency graph as adjacency list.

    Returns:
        Tuple of (reverse_graph, in_degree).
    """
    reverse_graph: dict[str, list[str]] = {node: [] for node in graph}
    in_degree: dict[str, int] = {node: 0 for node in graph}

    for node in graph:
        for dep in graph[node]:
            if dep in reverse_graph:
                reverse_graph[dep].append(node)
                in_degree[node] += 1

    return reverse_graph, in_degree


def _find_initial_nodes(in_degree: dict[str, int]) -> list[str]:
    """Find nodes with zero in-degree.

    Args:
        in_degree: Mapping of node to its in-degree.

    Returns:
        List of nodes with in-degree equal to zero.
    """
    return [node for node in in_degree if in_degree[node] == 0]


def _process_queue(
    queue: list[str],
    reverse_graph: dict[str, list[str]],
    in_degree: dict[str, int],
) -> list[str]:
    """Process BFS queue for topological sort.

    Args:
        queue: Initial queue of zero in-degree nodes.
        reverse_graph: Reverse adjacency list.
        in_degree: Current in-degree of each node.

    Returns:
        List of nodes in topological order.
    """
    order: list[str] = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        for dependent in reverse_graph.get(node, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    return order


def get_load_order(graph: dict[str, list[str]]) -> list[str]:
    """Get package load order using topological sort (Kahn's algorithm).

    Args:
        graph: Dependency graph as adjacency list.
               graph[A] = [B, C] means A depends on B and C.

    Returns:
        List of packages in load order. Empty list if cycle is detected.
    """
    reverse_graph, in_degree = _build_reverse_graph(graph)
    queue = _find_initial_nodes(in_degree)
    order = _process_queue(queue, reverse_graph, in_degree)

    if len(order) != len(graph):
        return []
    return order