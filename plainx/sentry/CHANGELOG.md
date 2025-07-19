# plainx-sentry changelog

## [0.7.0](https://github.com/davegaeddert/plainx-sentry/releases/plainx-sentry@0.7.0) (2025-07-19)

### What's changed

- Middleware was removed in favor of using the OpenTelemetry integration and new otel instrumentation in Plain.

### Upgrade instructions

- Remove `SentryMiddleware` and `SentryWorkerMiddleware` from your `app/settings.py`.
