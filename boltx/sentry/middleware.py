import sentry_sdk
from sentry_sdk.utils import capture_internal_exceptions
from sentry_sdk.tracing import TRANSACTION_SOURCE_TASK

from bolt.runtime import settings

try:
    from bolt.db import connection
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
            return event

        with sentry_sdk.configure_scope() as scope:
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

            # Set these after the request is handled,
            # so we can include it at the top of MIDDLEWARE
            # but also get the final context (user, request.unique_id, etc.)
            self.set_user_context(request)

        return response

    def set_user_context(self, request):
        if user := getattr(request, "user", None):
            if settings.SENTRY_PII_ENABLED:
                sentry_sdk.set_user(
                    {
                        "id": str(user.pk),
                        "email": user.email,
                        "username": user.get_username(),
                    }
                )
            else:
                sentry_sdk.set_user({"id": str(user.pk)})


class SentryWorkerMiddleware:
    def __init__(self, run_job):
        self.run_job = run_job

    def __call__(self, job):
        def event_processor(event, hint):
            with capture_internal_exceptions():
                # Attach it directly to any events
                extra = event.setdefault("extra", {})
                extra["bolt.worker"] = {"job": job.as_json()}
            return event

        with sentry_sdk.configure_scope() as scope:
            # Reset the scope (and breadcrumbs) for each job
            scope.clear()
            scope.add_event_processor(event_processor)

        with sentry_sdk.start_transaction(
            op="bolt.worker.job",
            name=f"job:{job.job_class}",
            source=TRANSACTION_SOURCE_TASK,
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
