"""EMERGENCE entry point for python -m emergence."""

import sys

from emergence.tui_app import run_tui


def main() -> None:
    """Main entry point - launches TUI by default."""
    # Check for --cli flag to use old CLI
    if "--cli" in sys.argv:
        from emergence.cli import main as cli_main

        cli_main()
    else:
        # Launch the new TUI
        run_tui()


if __name__ == "__main__":
    main()
