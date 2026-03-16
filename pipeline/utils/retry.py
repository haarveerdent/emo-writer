import time
import logging
import functools

logger = logging.getLogger(__name__)


def with_retry(max_attempts: int = 3, base_delay: float = 2.0):
    """
    Exponential backoff decorator: delays are 2s, 4s, 8s.
    Wraps individual LLM calls — not entire agent loops.
    A single story failing after max_attempts should be caught by the caller.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    delay = base_delay ** attempt
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed ({e}), "
                        f"retrying in {delay:.0f}s"
                    )
                    time.sleep(delay)
        return wrapper
    return decorator
