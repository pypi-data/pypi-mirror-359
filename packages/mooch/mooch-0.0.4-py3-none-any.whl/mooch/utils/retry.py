import functools
import time
from typing import Callable


# Untested
def retry(
    times: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable:
    def decorator(fn: callable) -> callable:
        @functools.wraps(fn)
        def wrapper(*args: object, **kwargs: object) -> object:
            last_exception: BaseException | None = None
            for i in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:  # noqa: PERF203
                    last_exception = e
                    if i == times - 1:
                        raise
                    time.sleep(delay)
            return last_exception

        return wrapper

    return decorator
