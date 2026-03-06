# plainx-sentry changelog

## [0.12.0](https://github.com/davegaeddert/plainx-sentry/releases/v0.12.0) (2026-03-06)

### What's changed

- Updated `SentryMiddleware` to use the new `before_request` middleware API ([3ebad96](https://github.com/davegaeddert/plainx-sentry/commit/3ebad96))
- Updated Plain dependencies to latest versions ([700140e](https://github.com/davegaeddert/plainx-sentry/commit/700140e))

### Upgrade instructions

- No changes required.

## [0.11.0](https://github.com/davegaeddert/plainx-sentry/releases/v0.11.0) (2026-02-05)

### What's changed

- Added `SentryMiddleware` for automatic request and user context on Sentry events ([950df07](https://github.com/davegaeddert/plainx-sentry/commit/950df07))
- Now requires Python 3.13+ ([dbfb0d7](https://github.com/davegaeddert/plainx-sentry/commit/dbfb0d7))
- Added type annotations throughout the codebase ([dbfb0d7](https://github.com/davegaeddert/plainx-sentry/commit/dbfb0d7))

### Upgrade instructions

- Ensure you are running Python 3.13 or higher
- Add `SentryMiddleware` to your middleware stack after `SessionMiddleware` for automatic request/user context

## [0.7.0](https://github.com/davegaeddert/plainx-sentry/releases/plainx-sentry@0.7.0) (2025-07-19)

### What's changed

- Middleware was removed in favor of using the OpenTelemetry integration and new otel instrumentation in Plain.

### Upgrade instructions

- Remove `SentryMiddleware` and `SentryWorkerMiddleware` from your `app/settings.py`.
