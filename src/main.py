"""Main entry point for the dependency graph visualizer."""
import argparse
import sys
import urllib.parse
from pathlib import Path

from .collector import get_direct_dependencies
from .graph import (
    build_dependency_graph,
    detect_cycles,
    get_transitive_dependencies,
)
from .test_loader import load_test_graph, get_test_dependencies
from .visualizer import (
    generate_plantuml,
    download_plantuml_png,
    generate_ascii_tree,
)

VALID_EXTENSIONS = (".png", ".svg", ".txt")
VALID_URL_SCHEMES = ("http://", "https://")
ERROR_EMPTY_PACKAGE = "Error: Package name cannot be empty."
ERROR_EMPTY_REPO = "Error: Repository URL or path cannot be empty."
ERROR_INVALID_URL = "Error: Invalid URL format."
ERROR_FILE_NOT_FOUND = "Error: Local file '{path}' does not exist."
ERROR_EMPTY_VERSION = "Error: Package version cannot be empty."
ERROR_BAD_EXTENSION = (
    "Error: Output file must have .png, .svg, or .txt extension."
)
ERROR_PLANTUML_FAILED = "Error: Failed to generate PNG image."


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Dependency graph visualizer."
    )
    parser.add_argument(
        "--package", type=str, required=True,
        help="Name of the analyzed package"
    )
    parser.add_argument(
        "--repo-url", type=str, required=True,
        help="URL or path to test repository file"
    )
    parser.add_argument(
        "--test-mode", action="store_true",
        help="Enable test repository working mode"
    )
    parser.add_argument(
        "--version", type=str, default="latest",
        help="Package version"
    )
    parser.add_argument(
        "--output-file", type=str, default="graph.png",
        help="Name of the generated graph image file"
    )
    parser.add_argument(
        "--ascii-tree", action="store_true",
        help="Output dependencies in ASCII-tree format"
    )
    return parser.parse_args()


def _validate_package(name: str) -> None:
    """Validate package name is not empty."""
    if not name:
        print(ERROR_EMPTY_PACKAGE)
        sys.exit(1)


def _validate_repo_url(url: str) -> None:
    """Validate repository URL or local file path."""
    if not url:
        print(ERROR_EMPTY_REPO)
        sys.exit(1)

    if url.startswith(VALID_URL_SCHEMES):
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc:
            print(ERROR_INVALID_URL)
            sys.exit(1)
    else:
        if not Path(url).exists():
            print(ERROR_FILE_NOT_FOUND.format(path=url))
            sys.exit(1)


def _validate_version(version: str) -> None:
    """Validate package version is not empty."""
    if not version:
        print(ERROR_EMPTY_VERSION)
        sys.exit(1)


def _validate_output_file(filename: str) -> None:
    """Validate output file has allowed extension."""
    if not filename.endswith(VALID_EXTENSIONS):
        print(ERROR_BAD_EXTENSION)
        sys.exit(1)


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate all parsed arguments."""
    _validate_package(args.package)
    _validate_repo_url(args.repo_url)
    _validate_version(args.version)
    _validate_output_file(args.output_file)


def print_dependencies(
    name: str, version: str, deps: list[str]
) -> None:
    """Print direct dependencies of a package."""
    print(f"\nDirect dependencies of {name}=={version}:")
    if not deps:
        print("  (no dependencies)")
        return
    for dep in deps:
        print(f"  - {dep}")


def print_graph(graph: dict[str, list[str]]) -> None:
    """Print dependency graph."""
    print("\nDependency Graph:")
    for package, deps in sorted(graph.items()):
        deps_str = ", ".join(deps) if deps else "(none)"
        print(f"  {package} -> {deps_str}")


def print_cycles(cycles: list[list[str]]) -> None:
    """Print detected cycles."""
    if not cycles:
        print("\nNo cycles detected.")
        return
    print(f"\nDetected {len(cycles)} cycle(s):")
    for i, cycle in enumerate(cycles, 1):
        cycle_str = " -> ".join(cycle)
        print(f"  Cycle {i}: {cycle_str}")


def print_transitive_deps(
    package: str, deps: set[str]
) -> None:
    """Print transitive dependencies."""
    print(f"\nTransitive dependencies of {package}:")
    if not deps:
        print("  (no transitive dependencies)")
        return
    for dep in sorted(deps):
        print(f"  - {dep}")


def print_ascii_tree(
    graph: dict[str, list[str]],
    package: str,
) -> None:
    """Print ASCII tree of dependencies."""
    print(f"\nASCII Tree for {package}:")
    tree = generate_ascii_tree(graph, package)
    print(tree)


def save_plantuml_and_png(
    graph: dict[str, list[str]],
    output_file: str,
) -> None:
    """Generate PlantUML text and download PNG image.

    Args:
        graph: Dependency graph as adjacency list.
        output_file: Path to save PNG file.
    """
    plantuml_text = generate_plantuml(graph)

    plantuml_file = output_file.rsplit(".", 1)[0] + ".puml"
    with open(plantuml_file, "w", encoding="utf-8") as file:
        file.write(plantuml_text)
    print(f"\nPlantUML diagram saved to: {plantuml_file}")

    if output_file.endswith(".png"):
        try:
            download_plantuml_png(plantuml_text, output_file)
            print(f"PNG image saved to: {output_file}")
        except OSError as error:
            print(f"Warning: {error}")
            print("PlantUML file saved, but PNG download failed.")


def run_test_mode(args: argparse.Namespace) -> None:
    """Run application in test mode."""
    graph = load_test_graph(args.repo_url)
    get_deps = get_test_dependencies(graph)

    print(f"\nTest Mode: Analyzing package '{args.package}'")
    print(f"Graph loaded from: {args.repo_url}")
    print(f"Total packages in graph: {len(graph)}")

    full_graph = build_dependency_graph(args.package, get_deps)
    print_graph(full_graph)

    cycles = detect_cycles(full_graph)
    print_cycles(cycles)

    if args.ascii_tree:
        print_ascii_tree(full_graph, args.package)

    save_plantuml_and_png(full_graph, args.output_file)

    trans_deps = get_transitive_dependencies(args.package, get_deps)
    print_transitive_deps(args.package, trans_deps)


def run_production_mode(args: argparse.Namespace) -> None:
    """Run application in production mode."""
    deps = get_direct_dependencies(
        args.repo_url, args.package, args.version
    )
    print_dependencies(args.package, args.version, deps)

    if args.ascii_tree:
        graph = {args.package: deps}
        print_ascii_tree(graph, args.package)


def main() -> None:
    """Main function to run the application."""
    args = parse_arguments()
    validate_arguments(args)

    try:
        if args.test_mode:
            run_test_mode(args)
        else:
            run_production_mode(args)
    except (ValueError, FileNotFoundError, OSError) as error:
        print(f"Error: {error}")
        sys.exit(1)

    print("\nStage 5 completed successfully.")


if __name__ == "__main__":
    main()