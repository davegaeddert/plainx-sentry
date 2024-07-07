import sentry_sdk
from plain.runtime import settings
from plain.templates.jinja.extensions import InclusionTagExtension


class SentryJSExtension(InclusionTagExtension):
    tags = {"sentry_js"}
    template_name = "sentry/js.html"

    def get_context(self, context, *args, **kwargs):
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
        }

        if "request" in context:
            # Use request.user by default (avoids accidental "user" variable confusion)
            user = getattr(context["request"], "user", None)
        else:
            # Get user directly if no request (like in server error context)
            user = context.get("user", None)

        if user:
            sentry_context["sentry_init"]["initialScope"] = {"user": {"id": user.id}}
            if settings.SENTRY_PII_ENABLED:
                if email := getattr(user, "email", None):
                    sentry_context["sentry_init"]["initialScope"]["user"][
                        "email"
                    ] = email
                if username := getattr(user, "username", None):
                    sentry_context["sentry_init"]["initialScope"]["user"][
                        "username"
                    ] = username

        return sentry_context


class SentryFeedbackExtension(SentryJSExtension):
    tags = {"sentry_feedback"}

    def get_context(self, context, *args, **kwargs):
        context = super().get_context(context, *args, **kwargs)
        context["sentry_dialog_event_id"] = sentry_sdk.last_event_id()
        return context


extensions = [
    SentryJSExtension,
    SentryFeedbackExtension,
]
