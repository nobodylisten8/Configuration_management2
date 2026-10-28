"""Tests for APKINDEX parser module."""
from src.apk_index import parse_apk_index, _parse_package_block

EXPECTED_PACKAGES_COUNT = 3

SAMPLE_INDEX = (
    "P:alpine-baselayout\n"
    "V:3.4.3-r1\n"
    "D:musl /bin/sh so:libc.musl-x86_64.so.1\n"
    "\n"
    "P:busybox\n"
    "V:1.36.1-r15\n"
    "D:musl musl-utils\n"
    "\n"
    "P:empty-pkg\n"
    "V:1.0.0-r0\n"
    "\n"
)


def test_parse_apk_index_counts_packages():
    """Test that parser finds all packages."""
    packages = parse_apk_index(SAMPLE_INDEX)
    assert len(packages) == EXPECTED_PACKAGES_COUNT


def test_parse_apk_index_extracts_name():
    """Test that parser extracts package name."""
    packages = parse_apk_index(SAMPLE_INDEX)
    assert packages[0]["name"] == "alpine-baselayout"


def test_parse_apk_index_extracts_version():
    """Test that parser extracts package version."""
    packages = parse_apk_index(SAMPLE_INDEX)
    assert packages[0]["version"] == "3.4.3-r1"


def test_parse_apk_index_extracts_dependencies():
    """Test that parser extracts dependencies."""
    packages = parse_apk_index(SAMPLE_INDEX)
    assert packages[0]["dependencies"] == [
        "musl", "/bin/sh", "so:libc.musl-x86_64.so.1"
    ]


def test_parse_apk_index_handles_no_dependencies():
    """Test that parser handles packages without dependencies."""
    packages = parse_apk_index(SAMPLE_INDEX)
    assert packages[2]["dependencies"] == []


def test_parse_package_block_missing_name():
    """Test that block without name returns empty dict."""
    block = "V:1.0.0\nD:dep1"
    result = _parse_package_block(block)
    assert result == {}


def test_parse_package_block_missing_version():
    """Test that block without version returns empty dict."""
    block = "P:pkg\nD:dep1"
    result = _parse_package_block(block)
    assert result == {}


def test_parse_apk_index_empty_content():
    """Test that empty content returns empty list."""
    assert parse_apk_index("") == []