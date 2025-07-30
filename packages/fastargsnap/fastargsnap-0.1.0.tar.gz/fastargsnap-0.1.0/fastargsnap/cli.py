"""
CLI tool for FastArgSnap
"""

import argparse
import subprocess
from .core import generate_snapshot


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FastArgSnap - Fast argument completion using snapshots"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a snapshot from an existing CLI tool"
    )
    generate_parser.add_argument(
        "cli_name",
        help="Name of the CLI tool to generate snapshot for"
    )
    generate_parser.add_argument(
        "output_path",
        help="Path to save the snapshot JSON file"
    )

    # Register command
    register_parser = subparsers.add_parser(
        "register",
        help="Register completion for a CLI tool"
    )
    register_parser.add_argument(
        "cli_name",
        help="Name of the CLI tool to register"
    )

    # List command
    subparsers.add_parser(
        "list",
        help="List registered completions"
    )

    # Unregister command
    unregister_parser = subparsers.add_parser(
        "unregister",
        help="Remove completion registration for a CLI tool"
    )
    unregister_parser.add_argument(
        "cli_name",
        help="Name of the CLI tool to unregister"
    )

    args = parser.parse_args()

    if args.command == "generate":
        generate_snapshot_for_cli(args.cli_name, args.output_path)
    elif args.command == "register":
        register_completion(args.cli_name)
    elif args.command == "list":
        list_completions()
    elif args.command == "unregister":
        unregister_completion(args.cli_name)


def generate_snapshot_for_cli(cli_name: str, output_path: str):
    """Generate a snapshot for an existing CLI tool"""
    try:
        # Try to import the CLI module
        import importlib
        module = importlib.import_module(cli_name)

        # Look for a parser or main function
        if hasattr(module, 'parser'):
            parser = module.parser
        elif hasattr(module, 'create_parser'):
            parser = module.create_parser()
        elif hasattr(module, 'main'):
            # Try to extract parser from main function
            # This is a simplified approach
            print(f"Warning: Could not find parser in {cli_name}")
            print("You may need to manually create a parser and call generate_snapshot()")
            return
        else:
            print(f"Error: Could not find parser in {cli_name}")
            return

        generate_snapshot(parser, output_path)
        print(f"Successfully generated snapshot for {cli_name}")

    except ImportError:
        print(f"Error: Could not import {cli_name}")
        print("Make sure the CLI tool is installed and accessible")


def register_completion(cli_name: str):
    """Register shell completion for a CLI tool"""
    try:
        # Use register-python-argcomplete
        result = subprocess.run(
            ["register-python-argcomplete", cli_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"Successfully registered completion for {cli_name}")
            print("You may need to restart your shell or source your profile")
        else:
            print(f"Error registering completion: {result.stderr}")

    except FileNotFoundError:
        print("Error: register-python-argcomplete not found")
        print("Make sure argcomplete is installed")


def list_completions():
    """List registered completions"""
    # This would need to check the shell configuration files
    # For now, just provide guidance
    print("Registered completions are typically stored in:")
    print("- ~/.bashrc or ~/.bash_profile (for bash)")
    print("- ~/.zshrc (for zsh)")
    print("- ~/.config/fish/config.fish (for fish)")
    print("\nLook for lines containing 'register-python-argcomplete'")


def unregister_completion(cli_name: str):
    """Remove completion registration for a CLI tool"""
    print(f"To unregister completion for {cli_name}:")
    print("1. Edit your shell configuration file:")
    print("   - ~/.bashrc or ~/.bash_profile (for bash)")
    print("   - ~/.zshrc (for zsh)")
    print("   - ~/.config/fish/config.fish (for fish)")
    print(f"2. Remove the line containing 'register-python-argcomplete {cli_name}'")
    print("3. Restart your shell or source your profile")


if __name__ == "__main__":
    main()
