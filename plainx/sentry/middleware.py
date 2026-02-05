from typing import Any

import sentry_sdk
from plain.auth import get_request_user
from plain.http import HttpMiddleware
from plain.http.request import Request
from plain.http.response import Response
from sentry_sdk.scope import should_send_default_pii


def _build_request_info(request: Request) -> dict[str, Any]:
    """Build request context dictionary for Sentry events."""
    try:
        url = request.build_absolute_uri()
    except Exception:
        url = request.path

    request_info = {
        "method": request.method,
        "url": url,
        "query_string": request.query_string,
    }

    if should_send_default_pii():
        request_info["headers"] = dict(request.headers)
        request_info["cookies"] = dict(request.cookies)

    return request_info


def _build_user_info(user: Any) -> dict[str, Any]:
    """Build user context dictionary for Sentry events."""
    user_info = {"id": str(user.id)}

    if should_send_default_pii():
        if email := getattr(user, "email", None):
            user_info["email"] = email
        if username := getattr(user, "username", None):
            user_info["username"] = username

    return user_info


class SentryMiddleware(HttpMiddleware):
    """
    Middleware that registers a Sentry event processor for request/user context.

    Add this to your MIDDLEWARE setting after SessionMiddleware:

        MIDDLEWARE = [
            ...
            "plain.sessions.middleware.SessionMiddleware",
            "plainx.sentry.middleware.SentryMiddleware",
            ...
        ]
    """

    def process_request(self, request: Request) -> Response:
        def event_processor(
            event: dict[str, Any], hint: dict[str, Any]
        ) -> dict[str, Any]:
            if "request" not in event:
                event["request"] = _build_request_info(request)

            if "user" not in event:
                user = get_request_user(request)
                if user:
                    event["user"] = _build_user_info(user)

            return event

        sentry_sdk.get_current_scope().add_event_processor(event_processor)
        return self.get_response(request)
