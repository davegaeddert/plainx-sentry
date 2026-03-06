SECRET_KEY = "secret"

DEBUG = True

INSTALLED_PACKAGES = [
    "plain.auth",
    "plain.sessions",
    "plainx.sentry",
]

MIDDLEWARE = [
    "plain.middleware.security.SecurityMiddleware",
    "plain.sessions.middleware.SessionMiddleware",
    "plain.middleware.common.CommonMiddleware",
    "plain.csrf.middleware.CsrfViewMiddleware",
    "plain.middleware.clickjacking.XFrameOptionsMiddleware",
    "plainx.sentry.middleware.SentryFeedbackMiddleware",
]

POSTGRES_DATABASE = "plainx-sentry-test"

ROOT_URLCONF = "urls"

USE_TZ = True
