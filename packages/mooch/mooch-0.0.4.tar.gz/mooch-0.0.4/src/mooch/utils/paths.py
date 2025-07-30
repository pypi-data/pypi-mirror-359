import os
import sys
from pathlib import Path


def desktop_path() -> Path:
    """Return the path to ~/Desktop."""
    if sys.platform.startswith("win"):
        path = Path(os.environ["USERPROFILE"])
    else:
        path = Path.home()
    return path / "Desktop"
