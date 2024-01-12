from os import environ

SENTRY_AUTO_INIT: bool = environ.get("SENTRY_AUTO_INIT", "true").lower() in (
    "true",
    "1",
    "yes",
)
SENTRY_INIT_KWARGS: dict = {}

SENTRY_DSN: str = environ.get("SENTRY_DSN", "")
SENTRY_RELEASE: str = environ.get("SENTRY_RELEASE", "")
SENTRY_ENVIRONMENT: str = environ.get("SENTRY_ENVIRONMENT", "production")

SENTRY_TRACES_SAMPLE_RATE: float = float(environ.get("SENTRY_TRACES_SAMPLE_RATE", 0.0))

SENTRY_PROFILES_SAMPLE_RATE: float = float(
    environ.get("SENTRY_PROFILES_SAMPLE_RATE", 0.0)
)

SENTRY_PII_ENABLED: bool = environ.get("SENTRY_PII_ENABLED", "true").lower() in (
    "true",
    "1",
    "yes",
)
