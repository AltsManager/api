"""Minimal in-process rate limiter.

Single-process, in-memory sliding window keyed by caller. Good enough to blunt
online brute-force/credential-stuffing against a single self-hosted instance.
It does *not* share state across multiple worker processes or machines -- a
deployment running several API workers behind a load balancer should replace
this with a shared store (e.g. Redis) instead.
"""

import time
from collections import defaultdict
from threading import Lock

_attempts: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def is_rate_limited(key: str, *, max_attempts: int, window_seconds: int) -> bool:
    """Record an attempt for `key` and return True if it should be rejected."""
    now = time.monotonic()
    with _lock:
        attempts = _attempts[key]
        attempts[:] = [t for t in attempts if now - t < window_seconds]
        if len(attempts) >= max_attempts:
            return True
        attempts.append(now)
        return False
