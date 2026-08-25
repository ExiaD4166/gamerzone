import logging
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response

logger = logging.getLogger("app.request")

REQUEST_ID_HEADER = "X-Request-ID"


async def request_context_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Tag every request with an id, time it, and log the outcome.

    Middleware wraps the whole request/response cycle: everything before `call_next`
    runs on the way in, everything after runs on the way out.

    The id is stored on request.state so the exception handlers can put it in the error
    body, and echoed back in a header. When someone reports a problem, that one string
    is enough to find the exact request in the logs.
    """
    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
    request.state.request_id = request_id

    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s -> %d in %.1fms [req %s]",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )

    response.headers[REQUEST_ID_HEADER] = request_id
    return response
