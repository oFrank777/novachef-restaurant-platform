import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("restaurant_api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request with timestamp, method, path, status and duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                "method=%s path=%s status=500 duration_ms=%.2f error=%s",
                request.method,
                request.url.path,
                duration_ms,
                str(exc),
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)
        status_code = response.status_code

        log_message = (
            f"method={request.method} path={request.url.path} "
            f"status={status_code} duration_ms={duration_ms}"
        )

        if status_code >= 500:
            logger.error(log_message)
        elif status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response
