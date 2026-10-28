"""Main entry point for the dependency graph visualizer."""
import argparse
import sys
import urllib.parse
from pathlib import Path

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


def print_configuration(args: argparse.Namespace) -> None:
    """Print all user-configurable parameters in key-value format."""
    print("--- Configuration ---")
    print(f"Package: {args.package}")
    print(f"Repository: {args.repo_url}")
    print(f"Test Mode: {args.test_mode}")
    print(f"Version: {args.version}")
    print(f"Output File: {args.output_file}")
    print(f"ASCII Tree: {args.ascii_tree}")
    print("---------------------")


def main() -> None:
    """Main function to run the application."""
    args = parse_arguments()
    validate_arguments(args)
    print_configuration(args)
    print("Stage 1 completed successfully.")


if __name__ == "__main__":
    main()