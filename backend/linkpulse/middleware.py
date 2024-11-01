import time
from asgi_correlation_id import correlation_id
import structlog

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.access_logger = structlog.get_logger("api.access")

    async def dispatch(self, request: Request, call_next) -> Response:
        structlog.contextvars.clear_contextvars()

        # These context vars will be added to all log entries emitted during the request
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter_ns()
        # If the call_next raises an error, we still want to return our own 500 response,
        # so we can add headers to it (process time, request ID...)
        response = Response(status_code=500)
        try:
            response = await call_next(request)
        except Exception:
            # TODO: Validate that we don't swallow exceptions (unit test?)
            structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
            raise
        finally:
            process_time_ms = (time.perf_counter_ns() - start_time) / 10**6

            self.access_logger.debug(
                "Request",
                http={
                    "url": str(request.url),
                    "query": dict(request.query_params),
                    "status_code": response.status_code,
                    "method": request.method,
                    "request_id": request_id,
                    "version": request.scope["http_version"],
                },
                client=(
                    {"ip": request.client.host, "port": request.client.port}
                    if request.client
                    else None
                ),
                duration="{:.2f}ms".format(process_time_ms),
            )

            # response.headers["X-Process-Time"] = str(process_time / 10 ** 9)

            return response
