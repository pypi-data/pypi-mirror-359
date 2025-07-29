import os
import sys
from pathlib import Path


class File:
    @staticmethod
    def config_path() -> Path:
        """Return the path to ~/AppData/Local or ~/.config."""
        if sys.platform.startswith("win"):
            config_path = Path(os.environ["USERPROFILE"]) / "AppData" / "Local"
        else:
            config_path = Path.home() / ".config"
        return config_path

    @staticmethod
    def desktop_path() -> Path:
        """Return the path to ~/Desktop."""
        if sys.platform.startswith("win"):
            config_path = Path(os.environ["USERPROFILE"])
        else:
            config_path = Path.home()
        return config_path / "Desktop"
