from functools import wraps
from threading import Lock
from time import monotonic

from flask import request

from utils.logs import logger

REQUESTS_PER_WINDOW = 5
WINDOW_SECONDS = 60

_lock = Lock()
_requests: dict[str, list[float]] = {}


def check_rate_limit(key: str) -> bool:
    now = monotonic()
    window_start = now - WINDOW_SECONDS
    with _lock:
        timestamps = [t for t in _requests.get(key, []) if t > window_start]
        if len(timestamps) >= REQUESTS_PER_WINDOW:
            _requests[key] = timestamps
            logger.warning(f"rate limit exceeded for {key}")
            return False
        timestamps.append(now)
        _requests[key] = timestamps
        return True


def reset_rate_limits() -> None:
    with _lock:
        _requests.clear()


def rate_limit(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr or "unknown"
        if not check_rate_limit(f"{request.path}:{client_ip}"):
            return {"error": "too many requests"}, 429
        return fn(*args, **kwargs)
    return wrapper
