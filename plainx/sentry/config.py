import sentry_sdk
from plain.packages import PackageConfig
from plain.runtime import settings


class PlainxSentryConfig(PackageConfig):
    name = "plainx.sentry"
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
                **settings.SENTRY_INIT_KWARGS,
            )
