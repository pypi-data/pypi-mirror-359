import time

import pytest

from mooch.decorators.retry import retry


def test_retry_success_first_try(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    def func():
        calls.append(1)
        return "ok"

    assert func() == "ok"
    assert len(calls) == 1


def test_retry_success_after_failures(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    def func():
        if len(calls) < 2:
            calls.append("fail")
            raise ValueError("fail")
        calls.append("ok")
        return "ok"

    assert func() == "ok"
    assert calls == ["fail", "fail", "ok"]


def test_retry_raises_after_all_attempts(monkeypatch):
    calls = []

    @retry(times=2, delay=0.01)
    def func():
        calls.append(1)
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError, match="fail"):
        func()
    assert len(calls) == 2


def test_retry_delay(monkeypatch):
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    @retry(times=3, delay=0.5)
    def func():
        raise Exception("fail")

    with pytest.raises(Exception):
        func()
    # Should sleep twice (times-1)
    assert sleep_calls == [0.5, 0.5]


def test_retry_returns_none_when_zero_times(monkeypatch):
    calls = []

    @retry(times=0, delay=0.01)
    def func():
        calls.append(1)
        return "should not be called"

    # Should not call the function at all, returns None
    assert func() is None
    assert calls == []


def test_retry_preserves_function_metadata():
    @retry(1)
    def my_func():
        """Docstring here."""
        return 42

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "Docstring here."


def test_retry_with_args_kwargs(monkeypatch):
    results = []

    @retry(times=2, delay=0.01)
    def func(a, b=2):
        results.append((a, b))
        if a != b:
            raise ValueError("fail")
        return a + b

    assert func(2, b=2) == 4
    assert results == [(2, 2)]


def test_retry_raises_last_exception_if_all_fail(monkeypatch):
    calls = []

    @retry(times=3, delay=0.01)
    def func():
        calls.append(1)
        if len(calls) < 2:
            raise Exception("fail")
        raise ValueError(f"fail {len(calls)}")

    with pytest.raises(ValueError, match="fail 3"):
        func()
    assert len(calls) == 3
