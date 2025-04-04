import sentry_sdk
from plain.runtime import settings
from sentry_sdk.tracing import TransactionSource
from sentry_sdk.utils import capture_internal_exceptions

try:
    from plain.models.db import connection
except ImportError:
    connection = None

import logging

logger = logging.getLogger(__name__)


def trace_db(execute, sql, params, many, context):
    with sentry_sdk.start_span(op="db", description=sql) as span:
        # Mostly borrowed from the Sentry Django integration...
        data = {
            "db.params": params,
            "db.executemany": many,
            "db.system": connection.vendor,
            "db.name": connection.settings_dict.get("NAME"),
            "db.user": connection.settings_dict.get("USER"),
            "server.address": connection.settings_dict.get("HOST"),
            "server.port": connection.settings_dict.get("PORT"),
        }

        sentry_sdk.add_breadcrumb(message=sql, category="query", data=data)

        for k, v in data.items():
            span.set_data(k, v)

        result = execute(sql, params, many, context)

    return result


class SentryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Don't do anything if Sentry is not active
        if not sentry_sdk.get_client().is_active():
            return self.get_response(request)

        def event_processor(event, hint):
            # request gets attached directly to an event,
            # not necessarily in the "context"
            request_info = event.setdefault("request", {})
            request_info["url"] = request.build_absolute_uri()
            request_info["method"] = request.method
            request_info["query_string"] = request.META.get("QUERY_STRING", "")
            # Headers and env need some PII filtering, ideally,
            # among other filters... similar for GET/POST data?
            # request_info["headers"] = dict(request.headers)
            try:
                request_info["data"] = request.body.decode("utf-8")
            except Exception:
                pass

            if user := getattr(request, "user", None):
                event["user"] = {"id": str(user.pk)}
                if settings.SENTRY_PII_ENABLED:
                    if email := getattr(user, "email", None):
                        event["user"]["email"] = email
                    if username := getattr(user, "username", None):
                        event["user"]["username"] = username

            return event

        with sentry_sdk.isolation_scope() as scope:
            # Reset the scope (and breadcrumbs) for each request
            scope.clear()
            scope.add_event_processor(event_processor)

            # Sentry's Django integration patches the WSGIHandler.
            # We could make our own WSGIHandler and patch it or call it directly from gunicorn,
            # but putting our middleware at the top of MIDDLEWARE is pretty close and easier.
            with sentry_sdk.start_transaction(
                op="http.server", name=request.path_info
            ) as transaction:
                if connection:
                    # Also get spans for db queries
                    with connection.execute_wrapper(trace_db):
                        response = self.get_response(request)
                else:
                    # No db presumably
                    response = self.get_response(request)

                if resolver_match := getattr(request, "resolver_match", None):
                    # Rename the transaction using a pattern,
                    # and attach other url/views tags we can use to filter
                    transaction.name = f"route:{resolver_match.route}"
                    transaction.set_tag("url_namespace", resolver_match.namespace)
                    transaction.set_tag("url_name", resolver_match.url_name)
                    transaction.set_tag("view_name", resolver_match.view_name)
                    transaction.set_tag("view_class", resolver_match._func_path)
                    # Don't need to filter on this, but do want the context to view
                    transaction.set_context(
                        "url_params",
                        {
                            "args": resolver_match.args,
                            "kwargs": resolver_match.kwargs,
                        },
                    )

                transaction.set_http_status(response.status_code)

            return response


class SentryWorkerMiddleware:
    def __init__(self, run_job):
        self.run_job = run_job

    def __call__(self, job):
        # Don't do anything if Sentry is not active
        if not sentry_sdk.get_client().is_active():
            return self.run_job(job)

        def event_processor(event, hint):
            with capture_internal_exceptions():
                # Attach it directly to any events
                extra = event.setdefault("extra", {})
                extra["plain.worker"] = {"job": job.as_json()}
            return event

        with sentry_sdk.isolation_scope() as scope:
            # Reset the scope (and breadcrumbs) for each request
            scope.clear()
            scope.add_event_processor(event_processor)

            with sentry_sdk.start_transaction(
                op="plain.worker.job",
                name=f"job:{job.job_class}",
                source=TransactionSource.TASK,
            ) as transaction:
                if connection:
                    # Also get spans for db queries
                    with connection.execute_wrapper(trace_db):
                        job_result = self.run_job(job)
                else:
                    # No db presumably
                    job_result = self.run_job(job)

                with capture_internal_exceptions():
                    # Don't need to filter on this, but do want the context to view
                    transaction.set_context("job", job.as_json())

                transaction.set_status("ok")

            return job_result
