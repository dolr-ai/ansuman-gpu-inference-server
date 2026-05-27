"""Request ID middleware."""

from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from backend.utils.ids import generate_request_id

REQUEST_ID_HEADER = "x-request-id"


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Attach a request ID to request state and response headers."""
    request_id = request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response
