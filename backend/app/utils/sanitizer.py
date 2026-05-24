import re
from app.utils.exceptions import ValidationError
_SQL_PATTERNS = [
    r"\bOR\s+1\s*=\s*1\b",
    r"\bOR\s+'1'\s*=\s*'1'\b",
    r"\bOR\s+\"1\"\s*=\s*\"1\"\b",
    r"\bOR\s+true\b",
    r"\bDROP\s+TABLE\b",
    r"\bDROP\s+DATABASE\b",
    r"\bUNION\s+SELECT\b",
    r"\bUNION\s+ALL\s+SELECT\b",
    r"\bINSERT\s+INTO\b",
    r"\bDELETE\s+FROM\b",
    r"\bUPDATE\s+\w+\s+SET\b",
    r"\bSELECT\s+\*\s+FROM\b",
    r"\bSELECT\s+.+\s+FROM\b",
    r";\s*DROP\b",
    r";\s*DELETE\b",
    r";\s*UPDATE\b",
    r"--\s",
    r"/\*.*\*/",
    r"\bEXEC\s*\(",
    r"\bEXECUTE\s*\(",
    r"\bxp_cmdshell\b",
    r"\bALTER\s+TABLE\b",
    r"\bCREATE\s+TABLE\b",
    r"\bTRUNCATE\s+TABLE\b",
    r"\bINFORMATION_SCHEMA\b",
    r"\bsys\.\w+\b",
    r"'\s*OR\s+'",
    r"\"\s*OR\s+\"",
    r"1\s*=\s*1",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _SQL_PATTERNS]

_XSS_PATTERNS = [
    r"<script\b",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe\b",
    r"<object\b",
    r"<embed\b",
]
_COMPILED_XSS = [re.compile(p, re.IGNORECASE) for p in _XSS_PATTERNS]

MAX_STRING_LENGTH = 2000


def sanitize_string(value: str) -> str:
    """Strip whitespace, remove null bytes, and limit length."""
    if not isinstance(value, str):
        return value
    value = value.strip()
    value = value.replace("\x00", "")
    if len(value) > MAX_STRING_LENGTH:
        value = value[:MAX_STRING_LENGTH]
    return value


def contains_xss(value: str) -> bool:
    if not isinstance(value, str):
        return False
    for pattern in _COMPILED_XSS:
        if pattern.search(value):
            return True
    return False


def contains_sql_injection(value: str) -> bool:
    """Return True if the value contains common SQL injection patterns."""
    if not isinstance(value, str):
        return False
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(value):
            return True
    return False


def sanitize_html(value: str) -> str:
    """Escape HTML special characters to prevent XSS."""
    if not isinstance(value, str):
        return value
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace('"', "&quot;")
    value = value.replace("'", "&#x27;")
    return value


_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
]
_COMPILED_TRAVERSAL = [re.compile(p) for p in _TRAVERSAL_PATTERNS]

def contains_path_traversal(value: str) -> bool:
    if not isinstance(value, str):
        return False
    for pattern in _COMPILED_TRAVERSAL:
        if pattern.search(value):
            return True
    return False


def validate_no_injection(value: str, field_name: str) -> None:
    """Raise ValidationError if malicious patterns are detected."""
    if contains_xss(value):
        raise ValidationError(
            detail=f"Contenido no permitido detectado en el campo '{field_name}'"
        )
    if contains_sql_injection(value):
        raise ValidationError(
            detail=f"Potentially malicious SQL content detected in field '{field_name}'"
        )
    if contains_path_traversal(value):
        raise ValidationError(
            detail=f"Path traversal attempt detected in field '{field_name}'"
        )
