"""Module for graph visualization using PlantUML and ASCII tree."""

import zlib
import base64
import urllib.request
import urllib.error


def generate_plantuml(graph: dict[str, list[str]]) -> str:
    """Generate PlantUML diagram text from dependency graph.

    Args:
        graph: Dependency graph as adjacency list.

    Returns:
        PlantUML diagram as string.
    """
    lines = ["@startuml", "skinparam packageStyle rectangle", ""]

    for package in sorted(graph.keys()):
        dependencies = graph[package]
        if not dependencies:
            lines.append(f'package "{package}" {{')
            lines.append("}")
        else:
            for dep in dependencies:
                lines.append(f'"{package}" --> "{dep}"')

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


def encode_plantuml(text: str) -> str:
    """Encode PlantUML text for online server URL.

    Args:
        text: PlantUML diagram text.

    Returns:
        Encoded string for URL.
    """
    compressed = zlib.compress(text.encode("utf-8"))[2:-4]
    return base64.b64encode(compressed).decode("ascii").translate(
        str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      "abcdefghijklmnopqrstuvwxyz"
                      "0123456789",
                      "0123456789"
                      "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      "abcdefghijklmnopqrstuvwxyz")
    )


def download_plantuml_png(
        plantuml_text: str,
        output_path: str,
) -> None:
    """Download PNG image from PlantUML online server."""
    encoded = encode_plantuml(plantuml_text)

    # Пробуем несколько серверов
    servers = [
        f"https://www.plantuml.com/plantuml/png/{encoded}",
        f"https://plantuml.com/plantuml/png/{encoded}",
        f"http://www.plantuml.com/plantuml/png/{encoded}",
        f"https://kroki.io/plantuml/png/{encoded}",
    ]

    for url in servers:
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(output_path, "wb") as file:
                    file.write(response.read())
            return
        except urllib.error.URLError:
            continue

    raise OSError("Failed to download PNG from all PlantUML servers")


def generate_ascii_tree(
        graph: dict[str, list[str]],
        start_package: str,
) -> str:
    """Generate ASCII tree representation of dependencies.

    Args:
        graph: Dependency graph as adjacency list.
        start_package: Root package name.

    Returns:
        ASCII tree as string.
    """
    return _build_ascii_tree(graph, start_package, "", True, set(), True)


def _format_node_line(
    package: str, prefix: str, is_last: bool, is_root: bool
) -> str:
    """Format the line for a single node."""
    if is_root:
        return package
    connector = "\\-- " if is_last else "+-- "
    return f"{prefix}{connector}{package}"


def _format_cycle_line(prefix: str, is_last: bool, is_root: bool) -> str:
    """Format the cycle indicator line."""
    if is_root:
        return "(...)"
    indent = "    " if is_last else "|   "
    return f"{prefix}{indent}(...)"


def _get_child_prefix(prefix: str, is_last: bool, is_root: bool) -> str:
    """Calculate prefix for child nodes."""
    if is_root:
        return ""
    extension = "    " if is_last else "|   "
    return f"{prefix}{extension}"


def _build_ascii_tree(
    graph: dict[str, list[str]],
    package: str,
    prefix: str,
    is_last: bool,
    visited: set[str],
    is_root: bool,
) -> str:
    """Recursively build ASCII tree fragment.

    Args:
        graph: Dependency graph as adjacency list.
        package: Current package name.
        prefix: Current line prefix for indentation.
        is_last: Whether this is the last child.
        visited: Set of already visited packages.
        is_root: Whether this is the root package.

    Returns:
        ASCII tree fragment as string.
    """
    lines = [_format_node_line(package, prefix, is_last, is_root)]

    if package in visited:
        lines.append(_format_cycle_line(prefix, is_last, is_root))
        return "\n".join(lines)

    visited.add(package)
    dependencies = graph.get(package, [])

    for i, dep in enumerate(dependencies):
        is_last_dep = i == len(dependencies) - 1
        child_prefix = _get_child_prefix(prefix, is_last, is_root)
        child_tree = _build_ascii_tree(
            graph, dep, child_prefix, is_last_dep, visited.copy(), False
        )
        lines.append(child_tree)

    return "\n".join(lines)