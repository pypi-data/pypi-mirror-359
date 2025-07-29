import os
import sys
from pathlib import Path

import pytest

from mooch.utils.file import File


@pytest.mark.parametrize(
    "platform,env_key,expected",
    [
        ("win32", "USERPROFILE", Path("C:/Users/TestUser/AppData/Local")),
        ("linux", None, Path.home() / ".config"),
        ("darwin", None, Path.home() / ".config"),
    ],
)
def test_config_path(monkeypatch, platform, env_key, expected):
    monkeypatch.setattr(sys, "platform", platform)
    if env_key:
        monkeypatch.setitem(os.environ, "USERPROFILE", "C:/Users/TestUser")
    result = File.config_path()
    assert result == expected


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
    result = File.desktop_path()
    assert result == expected
