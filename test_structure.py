#!/usr/bin/env python3
"""Structure test - verifies module organization without dependencies."""

import ast
import sys
from pathlib import Path


def check_module_structure(module_path: Path) -> bool:
    """Check that a Python module is syntactically valid."""
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        print(f"✓ {module_path.name}")
        return True
    except SyntaxError as e:
        print(f"✗ {module_path.name}: {e}")
        return False


def main():
    print("EMERGENCE Structure Validation")
    print("=" * 50)
    
    emergence_dir = Path(__file__).parent / "emergence"
    modules = [
        "__init__.py",
        "__main__.py",
        "cli.py",
        "tui_app.py",
        "tui_widgets.py",
        "neural.py",
        "reinforcement.py",
        "genetics.py",
        "entities.py",
        "world.py",
        "visualization.py",
        "stats.py",
        "graphs.py",
        "dashboard.py",
    ]
    
    all_valid = True
    for module in modules:
        path = emergence_dir / module
        if not path.exists():
            print(f"✗ {module}: NOT FOUND")
            all_valid = False
        else:
            all_valid &= check_module_structure(path)
    
    print("=" * 50)
    if all_valid:
        print("✓ All modules are syntactically valid!")
        print("\nTo run the simulator:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Launch interactive TUI: python -m emergence")
        print("  3. Legacy CLI: python -m emergence --cli")
        print("  4. Examples: python examples/quickstart.py")
        return 0
    else:
        print("✗ Some modules have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
