from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict, List
import asyncio

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        async with self.lock:
            now = time.time()
            # Purani requests remove karo
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < window_seconds
            ]
            if len(self.requests[key]) >= max_requests:
                return False
            self.requests[key].append(now)
            return True

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    # Client IP lo
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path

    # Auth endpoints pe strict limit
    if "/auth/login" in path or "/auth/register" in path:
        allowed = await rate_limiter.is_allowed(
            key=f"auth:{client_ip}",
            max_requests=10,
            window_seconds=60
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please wait 1 minute."}
            )

    # Upload endpoint pe limit
    if "/resumes/upload" in path:
        allowed = await rate_limiter.is_allowed(
            key=f"upload:{client_ip}",
            max_requests=5,
            window_seconds=60
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Upload limit reached. Please wait."}
            )

    # General API limit
    allowed = await rate_limiter.is_allowed(
        key=f"general:{client_ip}",
        max_requests=100,
        window_seconds=60
    )
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please slow down."}
        )

    response = await call_next(request)
    return response

def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    return add_security_headers(response)