"""Tests for graph module."""
from src.graph import (
    build_dependency_graph,
    detect_cycles,
    get_transitive_dependencies,
)


def _mock_get_deps(package: str) -> list[str]:
    """Mock dependency function for testing."""
    deps_map = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": [],
        "E": [],
    }
    return deps_map.get(package, [])


def _mock_cyclic_deps(package: str) -> list[str]:
    """Mock cyclic dependency function."""
    deps_map = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],
    }
    return deps_map.get(package, [])


def test_build_dependency_graph_simple():
    """Test building simple acyclic graph with recursive BFS."""
    graph = build_dependency_graph("A", _mock_get_deps)
    assert "A" in graph
    assert "B" in graph
    assert "C" in graph
    assert "D" in graph
    assert "E" in graph
    assert graph["A"] == ["B", "C"]
    assert graph["D"] == []


def test_detect_cycles_no_cycles():
    """Test cycle detection on acyclic graph."""
    graph = build_dependency_graph("A", _mock_get_deps)
    cycles = detect_cycles(graph)
    assert len(cycles) == 0


def test_detect_cycles_with_cycle():
    """Test cycle detection on cyclic graph."""
    graph = build_dependency_graph("A", _mock_cyclic_deps)
    cycles = detect_cycles(graph)
    assert len(cycles) > 0


def test_get_transitive_dependencies():
    """Test getting all transitive dependencies with recursive BFS."""
    deps = get_transitive_dependencies("A", _mock_get_deps)
    assert "B" in deps
    assert "C" in deps
    assert "D" in deps
    assert "E" in deps
    assert "A" not in deps