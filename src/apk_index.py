"""Module for parsing Alpine Linux APKINDEX format."""

KEY_PACKAGE = "P"
KEY_VERSION = "V"
KEY_DEPENDENCIES = "D"


def parse_apk_index(content: str) -> list[dict]:
    """Parse APKINDEX content into a list of package dictionaries.

    Args:
        content: Raw APKINDEX file content.

    Returns:
        List of dicts with keys 'name', 'version', 'dependencies'.
    """
    packages = []
    blocks = content.split("\n\n")
    for block in blocks:
        if not block.strip():
            continue
        package = _parse_package_block(block)
        if package:
            packages.append(package)
    return packages


def _parse_package_block(block: str) -> dict:
    """Parse a single package block from APKINDEX.

    Args:
        block: Text block describing one package.

    Returns:
        Dict with package info or empty dict if invalid.
    """
    data = {}
    for line in block.split("\n"):
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key] = value.strip()

    if KEY_PACKAGE not in data or KEY_VERSION not in data:
        return {}

    return {
        "name": data[KEY_PACKAGE],
        "version": data[KEY_VERSION],
        "dependencies": _parse_dependencies(
            data.get(KEY_DEPENDENCIES, "")
        ),
    }


def _parse_dependencies(dep_string: str) -> list[str]:
    """Parse dependency string into a list of dependency names.

    Args:
        dep_string: Space-separated dependency string.

    Returns:
        List of dependency names.
    """
    if not dep_string.strip():
        return []
    return dep_string.split()