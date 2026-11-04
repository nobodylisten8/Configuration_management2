"""Tests for visualizer module."""
from src.visualizer import (
    generate_plantuml,
    encode_plantuml,
    generate_ascii_tree,
)


SAMPLE_GRAPH = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": [],
}


def test_generate_plantuml_header():
    """Test PlantUML diagram starts with @startuml."""
    result = generate_plantuml(SAMPLE_GRAPH)
    assert result.startswith("@startuml")
    assert "@enduml" in result


def test_generate_plantuml_contains_packages():
    """Test PlantUML diagram contains all packages."""
    result = generate_plantuml(SAMPLE_GRAPH)
    assert '"A"' in result
    assert '"B"' in result
    assert '"C"' in result
    assert '"D"' in result


def test_generate_plantuml_contains_arrows():
    """Test PlantUML diagram contains dependency arrows."""
    result = generate_plantuml(SAMPLE_GRAPH)
    assert '"A" --> "B"' in result
    assert '"A" --> "C"' in result
    assert '"B" --> "D"' in result
    assert '"C" --> "D"' in result


def test_generate_plantuml_empty_graph():
    """Test PlantUML diagram for empty graph."""
    result = generate_plantuml({})
    assert "@startuml" in result
    assert "@enduml" in result


def test_encode_plantuml_returns_string():
    """Test encode_plantuml returns non-empty string."""
    result = encode_plantuml("@startuml\n@enduml")
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_ascii_tree_root():
    """Test ASCII tree starts with root package."""
    result = generate_ascii_tree(SAMPLE_GRAPH, "A")
    assert result.startswith("A")


def test_generate_ascii_tree_contains_children():
    """Test ASCII tree contains child packages."""
    result = generate_ascii_tree(SAMPLE_GRAPH, "A")
    assert "B" in result
    assert "C" in result
    assert "D" in result


def test_generate_ascii_tree_single_package():
    """Test ASCII tree for package without dependencies."""
    result = generate_ascii_tree({"X": []}, "X")
    assert result == "X"


def test_generate_ascii_tree_cycle_detection():
    """Test ASCII tree handles cyclic dependencies."""
    cyclic_graph = {"A": ["B"], "B": ["A"]}
    result = generate_ascii_tree(cyclic_graph, "A")
    assert "A" in result
    assert "B" in result
    assert "(...)" in result