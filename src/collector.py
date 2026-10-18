"""Module for collecting package data from Alpine Linux repositories."""

import io
import tarfile
from urllib.request import urlopen

from .apk_index import parse_apk_index

APK_INDEX_FILENAME = "APKINDEX"
APK_INDEX_ARCHIVE = "APKINDEX.tar.gz"


def fetch_apk_index(url: str) -> list[dict]:
    """Fetch and parse APKINDEX from a repository URL or local file.

    Args:
        url: HTTP(S) URL or local file path.

    Returns:
        List of parsed package dictionaries.
    """
    content = _load_index_content(url)
    return parse_apk_index(content)


def _load_index_content(url: str) -> str:
    """Load APKINDEX content from URL or local file.

    Args:
        url: HTTP(S) URL or local file path.

    Returns:
        APKINDEX file content as string.
    """
    if url.startswith(("http://", "https://")):
        return _download_and_extract(url)
    return _read_local_file(url)


def _download_and_extract(url: str) -> str:
    """Download APKINDEX.tar.gz and extract APKINDEX.

    Args:
        url: HTTP(S) URL to the repository.

    Returns:
        APKINDEX file content as string.
    """
    archive_url = _build_archive_url(url)
    with urlopen(archive_url) as response:
        data = response.read()
    return _extract_apk_index(data)


def _build_archive_url(url: str) -> str:
    """Build full URL to APKINDEX.tar.gz.

    Args:
        url: Repository base URL.

    Returns:
        Full URL to APKINDEX.tar.gz.
    """
    if url.endswith("/"):
        return url + APK_INDEX_ARCHIVE
    return url + "/" + APK_INDEX_ARCHIVE


def _extract_apk_index(archive_data: bytes) -> str:
    """Extract APKINDEX from tar.gz archive in memory.

    Args:
        archive_data: Raw tar.gz archive bytes.

    Returns:
        APKINDEX file content as string.
    """
    with tarfile.open(fileobj=io.BytesIO(archive_data)) as tar:
        for member in tar.getmembers():
            if member.name.endswith(APK_INDEX_FILENAME):
                file_obj = tar.extractfile(member)
                if file_obj is None:
                    continue
                return file_obj.read().decode("utf-8")
    raise FileNotFoundError(f"{APK_INDEX_FILENAME} not found in archive")


def _read_local_file(path: str) -> str:
    """Read APKINDEX content from a local file.

    Args:
        path: Path to local APKINDEX file.

    Returns:
        File content as string.
    """
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def find_package(packages: list[dict], name: str, version: str) -> dict:
    """Find a package by name and version.

    Args:
        packages: List of parsed packages.
        name: Package name to find.
        version: Package version to find.

    Returns:
        Package dictionary if found.

    Raises:
        ValueError: If package not found.
    """
    for package in packages:
        if package["name"] == name and package["version"] == version:
            return package
    raise ValueError(f"Package {name}=={version} not found")


def get_direct_dependencies(
    url: str, name: str, version: str
) -> list[str]:
    """Get direct dependencies of a package.

    Args:
        url: Repository URL or local file path.
        name: Package name.
        version: Package version.

    Returns:
        List of direct dependency names.
    """
    packages = fetch_apk_index(url)
    package = find_package(packages, name, version)
    return package["dependencies"]