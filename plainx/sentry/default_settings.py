from os import environ

SENTRY_AUTO_INIT: bool = True
SENTRY_INIT_KWARGS: dict = {}
SENTRY_PII_ENABLED: bool = True

# Re-use the standard Sentry env vars
SENTRY_DSN: str = environ.get("SENTRY_DSN", "")
SENTRY_RELEASE: str = environ.get("SENTRY_RELEASE", "")
SENTRY_ENVIRONMENT: str = environ.get("SENTRY_ENVIRONMENT", "production")

# These aren't built in as Sentry env vars?
SENTRY_TRACES_SAMPLE_RATE: float = float(environ.get("SENTRY_TRACES_SAMPLE_RATE", 0.0))
SENTRY_PROFILES_SAMPLE_RATE: float = float(
    environ.get("SENTRY_PROFILES_SAMPLE_RATE", 0.0)
)
