class AppException(Exception):
    """Base application exception with HTTP status code and detail message."""

    def __init__(self, status_code: int = 500, detail: str = "Internal server error"):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class ValidationError(AppException):
    """Raised when input validation fails (422)."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=422, detail=detail)


class NotFoundError(AppException):
    """Raised when a requested resource is not found (404)."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedError(AppException):
    """Raised when authentication fails (401)."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(AppException):
    """Raised when user lacks required permissions (403)."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class ConflictError(AppException):
    """Raised when a resource conflict occurs (409)."""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=409, detail=detail)


class BadRequestError(AppException):
    """Raised when the request is malformed or logically invalid (400)."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)


class RateLimitError(AppException):
    """Raised when the rate limit is exceeded (429)."""

    def __init__(self, detail: str = "Too many requests"):
        super().__init__(status_code=429, detail=detail)
