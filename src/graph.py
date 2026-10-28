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