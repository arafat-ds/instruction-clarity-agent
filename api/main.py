"""
api/main.py — FastAPI application factory with middleware and exception handlers.
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.core.config import get_settings
from api.core.logging import setup_logging
from api.routes import health, process
from api.schemas.response import ErrorDetail, ErrorResponse

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
settings = get_settings()
setup_logging(debug=settings.debug)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A hybrid instruction processing agent that extracts actions, "
            "deadlines, and priorities — or asks clarifying questions when needed."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # --- Middleware -----------------------------------------------------------

    @app.middleware("http")
    async def request_timing_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.perf_counter()

        logger.info(
            "→ %s %s [req_id=%s]",
            request.method,
            request.url.path,
            request_id,
        )

        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "← %s %s [req_id=%s] status=%d time=%sms",
            request.method,
            request.url.path,
            request_id,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms}ms"
        return response

    # --- Exception handlers --------------------------------------------------

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Extract the first validation error message
        first_error = exc.errors()[0] if exc.errors() else {}
        message = first_error.get("msg", "Invalid request")
        logger.warning("Validation error on %s: %s", request.url.path, message)
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error=ErrorDetail(message=message, code="VALIDATION_ERROR")
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=ErrorDetail(
                    message="An internal error occurred. Please try again.",
                    code="INTERNAL_ERROR",
                )
            ).model_dump(),
        )

    # --- Routers -------------------------------------------------------------
    app.include_router(health.router)
    app.include_router(process.router)

    logger.info("'%s' v%s started", settings.app_name, settings.app_version)
    return app


app = create_app()
