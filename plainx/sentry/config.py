import sentry_sdk
from opentelemetry import trace
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from plain.packages import PackageConfig, register_config
from plain.runtime import settings
from sentry_sdk.integrations.opentelemetry import SentryPropagator, SentrySpanProcessor


@register_config
class PlainxSentryConfig(PackageConfig):
    label = "plainxsentry"

    def ready(self):
        if settings.SENTRY_DSN and settings.SENTRY_AUTO_INIT:
            sentry_sdk.init(
                settings.SENTRY_DSN,
                release=settings.SENTRY_RELEASE,
                environment=settings.SENTRY_ENVIRONMENT,
                send_default_pii=settings.SENTRY_PII_ENABLED,
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
                instrumenter="otel",
                **settings.SENTRY_INIT_KWARGS,
            )

            # Set up OpenTelemetry tracing with Sentry
            if trace.get_tracer_provider() and not isinstance(
                trace.get_tracer_provider(), trace.ProxyTracerProvider
            ):
                raise RuntimeError(
                    "A tracer provider already exists. Sentry's OpenTelemetry integration requires a clean tracer provider."
                )

            provider = TracerProvider()
            provider.add_span_processor(SentrySpanProcessor())
            trace.set_tracer_provider(provider)
            set_global_textmap(SentryPropagator())
