from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from health_check.views import MainView


class HealthCheckJSONView(MainView):
    """
    The original `health_check` view uses format-attribute or headers to determine
    what response type is used. The HealthCheckJSONView can be used to ensure
    that a JSON Response is always used (for health check reporting).

    To apply it, in project's `urls.py`, add the custom JSON view in use like this:
    >>> # doctest: +SKIP
    ... import views
    ...
    ... urlpatterns = [
    ...     # ...
    ...     path(
    ...         r"healthz",
    ...         views.HealthCheckCustomView.as_view(),
    ...         name="health_check_custom",
    ...     ),
    ... ]
    """

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        subset = kwargs.get("subset", None)
        health_check_has_error = self.check(subset)
        status_code = 500 if health_check_has_error else 200
        return self.render_to_response_json(
            self.filter_plugins(subset=subset), status_code
        )
