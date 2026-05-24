import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./restaurant.db"
    SECRET_KEY: str = secrets.token_urlsafe(64)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT_PER_MINUTE: int = 100
    AUTH_RATE_LIMIT_PER_MINUTE: int = 20
    BASE_DELIVERY_FEE: float = 2.0
    DELIVERY_RATE_PER_KM: float = 1.5
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 20
    ALLOWED_PAYMENT_METHODS: list[str] = ["credit_card", "debit_card", "cash"]
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:3000"
    )
    ENABLE_API_DOCS: bool = True
    IDEMPOTENCY_TTL_SECONDS: int = 86400
    IDEMPOTENCY_MAX_KEYS: int = 10000

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
