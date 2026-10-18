"""Main entry point for the dependency graph visualizer."""
import argparse
import sys

VALID_EXTENSIONS = (".png", ".svg", ".txt")


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Dependency graph visualizer."
    )
    parser.add_argument(
        "--package",
        type=str,
        required=True,
        help="Name of the analyzed package"
    )
    parser.add_argument(
        "--repo-url",
        type=str,
        required=True,
        help="URL or path to test repository file"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Enable test repository working mode"
    )
    parser.add_argument(
        "--version",
        type=str,
        default="latest",
        help="Package version"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="graph.png",
        help="Name of the generated graph image file"
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="Output dependencies in ASCII-tree format"
    )
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate parsed arguments and handle errors."""
    if not args.package:
        print("Error: Package name cannot be empty.")
        sys.exit(1)
    if not args.repo_url:
        print("Error: Repository URL or path cannot be empty.")
        sys.exit(1)
    if not args.version:
        print("Error: Package version cannot be empty.")
        sys.exit(1)
    if not args.output_file.endswith(VALID_EXTENSIONS):
        print("Error: Output file must have .png, .svg, or .txt extension.")
        sys.exit(1)


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