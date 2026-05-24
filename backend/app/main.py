import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware, IdempotencyMiddleware
from app.routers import auth, cart, delivery, inventory, menu, orders, payments, reports
from app.utils.exceptions import AppException
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("restaurante_delivery_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando base de datos …")
    init_db()
    from app.seed import seed_menu_items
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        seed_menu_items(db)
    finally:
        db.close()
    logger.info("Restaurante Delivery API v1.0 está lista.")
    yield
_docs = "/docs" if settings.ENABLE_API_DOCS else None
_redoc = "/redoc" if settings.ENABLE_API_DOCS else None

app = FastAPI(
    title="Restaurante Delivery API",
    description="API de calidad de producción para la gestión y entrega de restaurantes",
    version="1.0.0",
    docs_url=_docs,
    redoc_url=_redoc,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "Accept"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(delivery.router)
app.include_router(payments.router)
app.include_router(inventory.router)
app.include_router(reports.router)


@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException):
    logger.warning("AppException %d: %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "message": err.get("msg", "Validation error")})
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Restaurante Delivery API v1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
