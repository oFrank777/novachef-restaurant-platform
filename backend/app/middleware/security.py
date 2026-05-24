import time
from collections import defaultdict
from typing import Dict, List, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._cleanup_counter = 0

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = _client_ip(request)
        now = time.time()
        window = 60.0
        path = request.url.path
        is_auth = path.startswith("/api/auth/login") or path.startswith("/api/auth/register")
        limit = (
            settings.AUTH_RATE_LIMIT_PER_MINUTE
            if is_auth
            else settings.RATE_LIMIT_PER_MINUTE
        )
        bucket_key = f"{client_ip}:auth" if is_auth else client_ip

        self._cleanup_counter += 1
        if self._cleanup_counter >= 100:
            self._cleanup_counter = 0
            self._cleanup_old_entries(now, window)

        timestamps = self._requests[bucket_key]
        self._requests[bucket_key] = [ts for ts in timestamps if now - ts < window]

        if len(self._requests[bucket_key]) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas peticiones. Por favor, inténtelo de nuevo más tarde.",
                    "retry_after_seconds": 60,
                },
            )

        self._requests[bucket_key].append(now)
        return await call_next(request)

    def _cleanup_old_entries(self, now: float, window: float) -> None:
        stale_ips = []
        for ip, timestamps in self._requests.items():
            fresh = [ts for ts in timestamps if now - ts < window]
            if not fresh:
                stale_ips.append(ip)
            else:
                self._requests[ip] = fresh
        for ip in stale_ips:
            del self._requests[ip]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._seen_keys: Dict[str, float] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in ("POST", "PUT", "PATCH"):
            idemp_key = request.headers.get("Idempotency-Key", "").strip()[:128]
            if idemp_key:
                now = time.time()
                self._prune_keys(now)
                composite = f"{request.url.path}:{idemp_key}"
                if composite in self._seen_keys:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "detail": "Clave de idempotencia ya procesada. Envío duplicado prevenido."
                        },
                    )
                response = await call_next(request)
                if response.status_code < 500:
                    if len(self._seen_keys) >= settings.IDEMPOTENCY_MAX_KEYS:
                        self._seen_keys.clear()
                    self._seen_keys[composite] = now
                return response
        return await call_next(request)

    def _prune_keys(self, now: float) -> None:
        ttl = settings.IDEMPOTENCY_TTL_SECONDS
        stale = [k for k, ts in self._seen_keys.items() if now - ts > ttl]
        for k in stale:
            del self._seen_keys[k]
