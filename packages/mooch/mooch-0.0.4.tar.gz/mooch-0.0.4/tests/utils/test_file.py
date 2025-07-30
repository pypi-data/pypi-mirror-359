import os
import sys
from pathlib import Path

import pytest

from mooch.utils.paths import desktop_path


@pytest.mark.parametrize(
    "platform,env_key,expected",
    [
        ("win32", "USERPROFILE", Path("C:/Users/TestUser/Desktop")),
        ("linux", None, Path.home() / "Desktop"),
        ("darwin", None, Path.home() / "Desktop"),
    ],
)
def test_desktop_path(monkeypatch, platform, env_key, expected):
    monkeypatch.setattr(sys, "platform", platform)
    if env_key:
        monkeypatch.setitem(os.environ, "USERPROFILE", "C:/Users/TestUser")
    result = desktop_path()
    assert result == expected
