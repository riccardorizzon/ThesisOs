"""Optional shared beta access token — ADR-0048.

When BETA_ACCESS_TOKEN is unset, this middleware is a no-op (local DX).
When set, every path except /health and /ready requires X-Beta-Token.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

_OPEN_PATHS = frozenset({"/health", "/ready", "/metrics"})


class BetaAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        token = (settings.beta_access_token or "").strip()
        if not token:
            return await call_next(request)
        path = request.url.path.rstrip("/") or "/"
        if path in _OPEN_PATHS:
            return await call_next(request)
        provided = (request.headers.get("X-Beta-Token") or "").strip()
        if provided == token:
            return await call_next(request)
        return JSONResponse(
            status_code=401,
            content={
                "code": "beta_token_required",
                "message": "Missing or invalid X-Beta-Token (ADR-0048 shared beta gate)",
            },
        )
