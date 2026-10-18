"""Tests for collector module."""
import pytest
from unittest.mock import patch
from src.collector import (
    fetch_apk_index,
    find_package,
    get_direct_dependencies,
    _build_archive_url,
)


SAMPLE_PACKAGES = [
    {"name": "pkg1", "version": "1.0", "dependencies": ["dep1", "dep2"]},
    {"name": "pkg2", "version": "2.0", "dependencies": ["dep3"]},
]


def test_build_archive_url_with_trailing_slash():
    """Test URL building with trailing slash."""
    url = _build_archive_url("http://example.com/repo/")
    assert url == "http://example.com/repo/APKINDEX.tar.gz"


def test_build_archive_url_without_trailing_slash():
    """Test URL building without trailing slash."""
    url = _build_archive_url("http://example.com/repo")
    assert url == "http://example.com/repo/APKINDEX.tar.gz"


def test_find_package_success():
    """Test finding an existing package."""
    result = find_package(SAMPLE_PACKAGES, "pkg1", "1.0")
    assert result["name"] == "pkg1"
    assert result["dependencies"] == ["dep1", "dep2"]


def test_find_package_not_found():
    """Test that missing package raises ValueError."""
    with pytest.raises(ValueError):
        find_package(SAMPLE_PACKAGES, "missing", "1.0")


def test_find_package_wrong_version():
    """Test that wrong version raises ValueError."""
    with pytest.raises(ValueError):
        find_package(SAMPLE_PACKAGES, "pkg1", "9.9")


@patch("src.collector._read_local_file")
def test_fetch_apk_index_local_file(mock_read):
    """Test fetching from local file."""
    mock_read.return_value = "P:pkg\nV:1.0\nD:dep1\n\n"
    result = fetch_apk_index("/path/to/APKINDEX")
    assert len(result) == 1
    assert result[0]["name"] == "pkg"
    mock_read.assert_called_once_with("/path/to/APKINDEX")


@patch("src.collector._download_and_extract")
def test_fetch_apk_index_http_url(mock_download):
    """Test fetching from HTTP URL."""
    mock_download.return_value = "P:pkg\nV:1.0\nD:dep1\n\n"
    result = fetch_apk_index("http://example.com/repo")
    assert len(result) == 1
    mock_download.assert_called_once_with("http://example.com/repo")


@patch("src.collector.fetch_apk_index")
def test_get_direct_dependencies(mock_fetch):
    """Test getting direct dependencies."""
    mock_fetch.return_value = SAMPLE_PACKAGES
    result = get_direct_dependencies("http://test.com", "pkg1", "1.0")
    assert result == ["dep1", "dep2"]


@patch("src.collector.fetch_apk_index")
def test_get_direct_dependencies_not_found(mock_fetch):
    """Test error when package not found."""
    mock_fetch.return_value = SAMPLE_PACKAGES
    with pytest.raises(ValueError):
        get_direct_dependencies("http://test.com", "missing", "1.0")