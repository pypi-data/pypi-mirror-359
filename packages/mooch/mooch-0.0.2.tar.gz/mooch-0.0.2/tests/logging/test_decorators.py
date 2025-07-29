import asyncio

import pytest

from mooch.logging.decorators import log_entry_exit


class DummyLogger:
    def __init__(self):
        self.records = []

    def log(self, msg, level):
        self.records.append((msg, level))


@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    dummy_logger = DummyLogger()
    monkeypatch.setattr("mooch.logging.decorators.logger", dummy_logger)
    return dummy_logger


def test_log_entry_exit_sync(patch_logger):
    calls = []

    @log_entry_exit
    def foo(a, b, c=None):
        calls.append((a, b, c))
        return a + b

    result = foo(1, 2, c=3)
    assert result == 3
    assert calls == [(1, 2, 3)]
    logs = patch_logger.records
    assert logs[0][0].startswith("BEGIN: ")
    assert "foo()" in logs[0][0]
    assert logs[1][0].startswith("Args: (1, 2, 'c = 3')")
    assert logs[2][0].startswith("END: ")


def test_log_entry_exit_sync_kwargs(patch_logger):
    @log_entry_exit
    def bar(x, y=10):
        return x * y

    result = bar(2, y=5)
    assert result == 10
    logs = patch_logger.records
    assert "Args:" in logs[1][0]
    assert "y = 5" in logs[1][0]


@pytest.mark.asyncio
async def test_log_entry_exit_async(patch_logger):
    calls = []

    @log_entry_exit
    async def baz(a, b):
        calls.append((a, b))
        await asyncio.sleep(0)
        return a * b

    result = await baz(3, 4)
    assert result == 12
    assert calls == [(3, 4)]
    logs = patch_logger.records
    assert logs[0][0].startswith("BEGIN: ")
    assert "baz()" in logs[0][0]
    assert logs[1][0].startswith("Args: (3, 4)")
    assert logs[2][0].startswith("END: ")


def test_log_entry_exit_preserves_signature():
    @log_entry_exit
    def foo(a, b):
        return a + b

    assert foo.__name__ == "foo"
    assert foo.__qualname__.endswith("foo")
