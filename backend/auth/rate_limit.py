"""
Simple in-memory rate limiter for public API endpoints.
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException


class RateLimiter:
    """IP-based rate limiter using a sliding window."""

    def __init__(self):
        # {ip: [timestamp, timestamp, ...]}
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_ip(self, request: Request) -> str:
        return (
            request.headers.get("X-Real-IP")
            or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.client.host
        )

    def _clean(self, ip: str, window: int):
        cutoff = time.time() - window
        self._requests[ip] = [t for t in self._requests[ip] if t > cutoff]

    def check(self, request: Request, max_requests: int, window_seconds: int):
        """Raise 429 if the IP has exceeded max_requests in the window."""
        ip = self._get_ip(request)
        self._clean(ip, window_seconds)
        if len(self._requests[ip]) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        self._requests[ip].append(time.time())


rate_limiter = RateLimiter()
