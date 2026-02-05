from typing import Any

import sentry_sdk
from jinja2.runtime import Context
from plain.auth import get_request_user
from plain.runtime import settings
from plain.templates import register_template_extension
from plain.templates.jinja.extensions import InclusionTagExtension


@register_template_extension
class SentryJSExtension(InclusionTagExtension):
    tags = {"sentry_js"}
    template_name = "sentry/js.html"

    def get_context(
        self, context: Context, *args: Any, **kwargs: Any
    ) -> Context | dict[str, Any]:
        if not settings.SENTRY_DSN:
            return {}

        sentry_public_key = settings.SENTRY_DSN.split("//")[1].split("@")[0]

        sentry_context = {
            "sentry_public_key": sentry_public_key,
            "sentry_init": {
                "release": settings.SENTRY_RELEASE,
                "environment": settings.SENTRY_ENVIRONMENT,
                "sendDefaultPii": bool(settings.SENTRY_PII_ENABLED),
            },
            "csp_nonce": context["request"].csp_nonce,
        }

        if user := get_request_user(context["request"]):
            sentry_context["sentry_init"]["initialScope"] = {"user": {"id": user.id}}
            if settings.SENTRY_PII_ENABLED:
                if email := getattr(user, "email", None):
                    sentry_context["sentry_init"]["initialScope"]["user"]["email"] = (
                        email
                    )
                if username := getattr(user, "username", None):
                    sentry_context["sentry_init"]["initialScope"]["user"][
                        "username"
                    ] = username

        return sentry_context


@register_template_extension
class SentryFeedbackExtension(SentryJSExtension):
    tags = {"sentry_feedback"}

    def get_context(
        self, context: Context, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        parent_result = super().get_context(context, *args, **kwargs)
        result: dict[str, Any] = dict(parent_result)
        result["sentry_dialog_event_id"] = sentry_sdk.last_event_id()
        return result
