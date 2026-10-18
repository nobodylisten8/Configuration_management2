"""Tests for CLI argument parsing and validation."""
import pytest
import sys
from unittest.mock import patch
from src.main import parse_arguments, validate_arguments


def test_parse_arguments_defaults():
    """Test parsing with default values."""
    test_args = [
        "main.py",
        "--package", "test_pkg",
        "--repo-url", "http://example.com"
    ]
    with patch.object(sys, 'argv', test_args):
        args = parse_arguments()
        assert args.package == "test_pkg"
        assert args.repo_url == "http://example.com"
        assert args.version == "latest"
        assert args.output_file == "graph.png"
        assert args.test_mode is False
        assert args.ascii_tree is False


def test_validate_arguments_success():
    """Test successful validation of arguments."""

    class MockArgs:
        package = "pkg"
        repo_url = "http://test.com"
        version = "1.0"
        output_file = "graph.png"

    validate_arguments(MockArgs())


def test_validate_empty_package(capsys):
    """Test validation failure on empty package."""

    class MockArgs:
        package = ""
        repo_url = "http://test.com"
        version = "1.0"
        output_file = "graph.png"

    with pytest.raises(SystemExit) as exc_info:
        validate_arguments(MockArgs())

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Package name cannot be empty" in captured.out