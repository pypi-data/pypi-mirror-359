import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


def log_entry_exit(func: callable):  # noqa: ANN201
    @functools.wraps(func)
    def run_func(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        logger.info(f"[{func.__module__}] Entering: {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"[{func.__module__}] Exiting: {func.__name__}")
        return result

    @functools.wraps(func)
    async def async_run_func(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        logger.info(f"[{func.__module__}] Entering: {func.__name__} with args={args}, kwargs={kwargs}")
        result = await func(*args, **kwargs)
        logger.info(f"[{func.__module__}] Exiting: {func.__name__}")
        return result

    return async_run_func if asyncio.iscoroutinefunction(func) else run_func
