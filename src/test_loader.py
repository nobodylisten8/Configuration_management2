"""Module for loading test graph from file."""

from pathlib import Path


def load_test_graph(file_path: str) -> dict[str, list[str]]:
    """Load dependency graph from test file.

    File format: each line is 'PACKAGE: DEP1 DEP2 DEP3'

    Args:
        file_path: Path to test graph file.

    Returns:
        Dictionary mapping package names to their dependencies.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file format is invalid.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Test file '{file_path}' not found")

    graph = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                raise ValueError(
                    f"Invalid format at line {line_num}: '{line}'"
                )

            package, _, deps_str = line.partition(":")
            package = package.strip()
            deps = deps_str.split() if deps_str.strip() else []
            graph[package] = deps

    return graph


def get_test_dependencies(
    graph: dict[str, list[str]],
) -> callable:
    """Create dependency function from test graph.

    Args:
        graph: Test graph as adjacency list.

    Returns:
        Function that returns dependencies for a package.
    """
    def _get_deps(package: str) -> list[str]:
        """Get dependencies for package from test graph."""
        return graph.get(package, [])

    return _get_deps