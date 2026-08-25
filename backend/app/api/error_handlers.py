import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import GamerZoneError

logger = logging.getLogger("app.errors")


def _error_body(request: Request, detail: str, code: str) -> dict[str, str]:
    """Every error leaves the API in the same shape, whatever raised it.

    `detail` is for a person to read, `code` is for the frontend to branch on - it
    stays stable even if the wording changes - and `request_id` ties the response to a
    line in the logs.
    """
    return {
        "detail": detail,
        "code": code,
        "request_id": getattr(request.state, "request_id", "unknown"),
    }


def register_error_handlers(app: FastAPI) -> None:
    """Attach the handlers that turn exceptions into responses."""

    @app.exception_handler(GamerZoneError)
    async def handle_domain_error(request: Request, exc: GamerZoneError) -> JSONResponse:
        """Business rules that said no. Expected, so logged only at info level."""
        logger.info("Domain error: %s (%s)", exc.code, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(request, exc.detail, exc.code),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        """HTTPExceptions raised in the API layer (mostly auth checks in deps.py).

        Reshaped so they match everything else. exc.headers is preserved because 401s
        carry WWW-Authenticate, which clients rely on.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(request, str(exc.detail), f"http_{exc.status_code}"),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Bad request bodies. FastAPI's own format is a bare list, so it's wrapped to
        match, with the per-field details kept under `errors` for form highlighting."""
        body = _error_body(request, "The submitted data is invalid.", "validation_error")
        body["errors"] = exc.errors()  # type: ignore[assignment]
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        """Last resort: a genuine bug.

        The traceback goes to our logs, never to the client - a stack trace exposes
        file paths, library versions and local state, all of which help an attacker.
        The client gets the request_id instead, which is enough for us to find it.
        """
        logger.exception(
            "Unhandled error on %s %s [req %s]",
            request.method,
            request.url.path,
            getattr(request.state, "request_id", "unknown"),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(request, "Internal server error.", "internal_error"),
        )
