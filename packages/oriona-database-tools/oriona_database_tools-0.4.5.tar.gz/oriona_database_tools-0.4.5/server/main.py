#!/usr/bin/env python3
"""DXT entry point for Oriona Database Tools MCP server."""

import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir / "src"))

if __name__ == "__main__":
    from database_tools.server import main
    main()