# plainx-sentry

Use [Sentry](https://sentry.io/) to monitor errors and performance in your Plain application.

![image](https://user-images.githubusercontent.com/649496/213781768-182322e6-edf0-4d98-8b37-ab564ef23c3b.png)

## Installation

```python
# settings.py
INSTALLED_PACKAGES = [
  # ...
  "plainx.sentry",
]

MIDDLEWARE = [
  # Put SentryMiddleware as early as possible in the middleware stack
  "plainx.sentry.SentryMiddleware",
  # ...
]
```

In your `base.html`, load `sentry` and include the `sentry_js` tag:

```html
<!-- base.html -->
<!doctype html>
<html lang="en">
  <head>
      ...
      {% sentry_js %}
  </head>
  <body>
      ...
  </body>
</html>
```

To enable Sentry in production, add the `SENTRY_DSN` to your environment.
In Heroku, for example:

```sh
heroku config:set SENTRY_DSN=<your-DSN>
```

## Configuration

[Look at the `default_settings.py` for all available settings.](./plainx/sentry/default_settings.py)

## Error page feedback widget

In your `500.html`, you can optionally use the `sentry_feedback` tag to show Sentry's feedback widget:

```html
<!-- base.html -->
<!doctype html>
<html lang="en">
  <head>
      ...
      {% sentry_feedback %}
  </head>
  <body>
      ...
  </body>
</html>
```

![image](https://user-images.githubusercontent.com/649496/213781811-418500fa-b7f8-43f1-8d28-4fde1bfe2b4b.png)
