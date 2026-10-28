"""Tests for test_loader module."""
import pytest
from pathlib import Path
from src.test_loader import load_test_graph, get_test_dependencies


TEST_DATA_DIR = Path(__file__).parent / "test_data"


def test_load_simple_graph():
    """Test loading simple acyclic graph."""
    file_path = str(TEST_DATA_DIR / "simple_graph.txt")
    graph = load_test_graph(file_path)
    assert "A" in graph
    assert graph["A"] == ["B", "C"]
    assert graph["B"] == ["D"]
    assert graph["C"] == ["D", "E"]
    assert graph["D"] == []
    assert graph["E"] == []
    assert len(graph) == 5


def test_load_cyclic_graph():
    """Test loading graph with cycles."""
    file_path = str(TEST_DATA_DIR / "cyclic_graph.txt")
    graph = load_test_graph(file_path)
    assert "A" in graph
    assert "B" in graph
    assert "C" in graph
    assert "D" in graph
    assert graph["A"] == ["B"]
    assert graph["B"] == ["C"]
    assert graph["C"] == ["A"]
    assert graph["D"] == ["B"]


def test_load_complex_graph():
    """Test loading complex graph with multiple dependencies."""
    file_path = str(TEST_DATA_DIR / "complex_graph.txt")
    graph = load_test_graph(file_path)
    assert len(graph) == 8
    assert graph["A"] == ["B", "C", "D"]
    assert graph["B"] == ["E", "F"]
    assert graph["C"] == ["F", "G"]
    assert graph["D"] == ["G"]
    assert graph["E"] == ["H"]
    assert graph["F"] == ["H"]
    assert graph["G"] == []
    assert graph["H"] == []


def test_load_nonexistent_file():
    """Test error handling for missing file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        load_test_graph("/fake/path/to/graph.txt")
    assert "not found" in str(exc_info.value)


def test_load_empty_graph_file(tmp_path):
    """Test loading empty graph file."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    graph = load_test_graph(str(empty_file))
    assert graph == {}


def test_load_graph_with_comments(tmp_path):
    """Test loading graph file with comments."""
    file_with_comments = tmp_path / "comments.txt"
    file_with_comments.write_text(
        "# This is a comment\n"
        "A: B C\n"
        "# Another comment\n"
        "B:\n"
    )
    graph = load_test_graph(str(file_with_comments))
    assert "A" in graph
    assert "B" in graph
    assert graph["A"] == ["B", "C"]
    assert graph["B"] == []


def test_load_graph_invalid_format_no_colon(tmp_path):
    """Test error handling for invalid format (missing colon)."""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("A B C\n")
    with pytest.raises(ValueError) as exc_info:
        load_test_graph(str(invalid_file))
    assert "Invalid format" in str(exc_info.value)


def test_load_graph_with_whitespace(tmp_path):
    """Test loading graph with various whitespace."""
    whitespace_file = tmp_path / "whitespace.txt"
    whitespace_file.write_text(
        "  A  :  B   C  \n"
        "B:\n"
        "  C  :  D  \n"
    )
    graph = load_test_graph(str(whitespace_file))
    assert graph["A"] == ["B", "C"]
    assert graph["B"] == []
    assert graph["C"] == ["D"]


def test_get_test_dependencies():
    """Test creating dependency function from graph."""
    file_path = str(TEST_DATA_DIR / "simple_graph.txt")
    graph = load_test_graph(file_path)
    get_deps = get_test_dependencies(graph)
    assert get_deps("A") == ["B", "C"]
    assert get_deps("B") == ["D"]
    assert get_deps("C") == ["D", "E"]
    assert get_deps("D") == []
    assert get_deps("E") == []


def test_get_test_dependencies_nonexistent_package():
    """Test dependency function with nonexistent package."""
    graph = {"A": ["B"], "B": []}
    get_deps = get_test_dependencies(graph)
    assert get_deps("Z") == []
    assert get_deps("X") == []


def test_get_test_dependencies_empty_graph():
    """Test dependency function with empty graph."""
    graph = {}
    get_deps = get_test_dependencies(graph)
    assert get_deps("A") == []