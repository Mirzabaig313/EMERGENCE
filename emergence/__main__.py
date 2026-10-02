"""EMERGENCE entry point for python -m emergence."""

from emergence.cli import EmergenceCLI, build_world, parse_args


def main() -> None:
    """Launch the TUI by default, or the classic CLI with --cli."""
    args = parse_args()
    world = build_world(args)
    if args.cli:
        EmergenceCLI(world).run()
    else:
        # Imported lazily so `--cli` works without textual installed.
        from emergence.tui_app import EmergenceApp

        EmergenceApp(world=world).run()


if __name__ == "__main__":
    main()
