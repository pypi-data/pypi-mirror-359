import sys
import types

import pytest

from mooch import Require
from mooch.exceptions import RequirementError


def make_version_info(major: int, minor: int, micro: int = 0):
    return types.SimpleNamespace(
        major=major,
        minor=minor,
        micro=micro,
        __getitem__=lambda _, idx: (major, minor, micro)[idx],
    )


@pytest.mark.parametrize(
    ("required", "actual", "should_raise"),
    [
        ("3.8", (3, 8), False),
        ("3.7", (3, 8), False),
        ("3.8", (3, 7), True),
        ("3.9", (3, 8), True),
        ("2.7", (3, 8), False),
        ("3.8", (3, 9), False),
        ("3.8", (2, 7), True),
        ("4.0", (3, 8), True),
        ("3.13", (3, 13), False),
    ],
)
def test_python_version(monkeypatch, required, actual, should_raise):
    class FakeVersionInfo(tuple):
        def __new__(cls, major, minor, micro=0):
            return super().__new__(cls, (major, minor, micro))

        @property
        def major(self):
            return self[0]

        @property
        def minor(self):
            return self[1]

        @property
        def micro(self):
            return self[2]

        def __getitem__(self, idx):
            return super().__getitem__(idx)

    monkeypatch.setattr(sys, "version_info", FakeVersionInfo(*actual))
    if should_raise:
        with pytest.raises(RequirementError) as excinfo:
            Require.python_version(required)
        assert f"requires Python version {required}" in str(excinfo.value)
    else:
        Require.python_version(required)


@pytest.mark.parametrize(
    ("required_system", "platform_sys", "should_raise"),
    [
        ("Windows", "Windows", False),
        ("windows", "Windows", False),
        ("Linux", "linux", False),
        ("Windows", "linux", True),
        ("Darwin", "darwin", False),
        ("", "Windows", True),
    ],
)
def test_windows_os_platform(monkeypatch, required_system, platform_sys, should_raise):
    monkeypatch.setattr("platform.system", lambda: platform_sys)
    if should_raise:
        with pytest.raises(RequirementError) as excinfo:
            Require.operating_system(required_system)
        assert f"requires '{required_system}'" in str(excinfo.value)
        assert platform_sys in str(excinfo.value)
    else:
        Require.operating_system(required_system)
