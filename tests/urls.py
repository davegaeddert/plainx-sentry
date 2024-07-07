from plain.urls import path
from plain.views import TemplateView


class ErrorView(TemplateView):
    template_name = "index.html"  # Won't actually render this, will error instead

    def get_context(self, **kwargs):
        raise Exception("Test!")


urlpatterns = [
    path("error/", ErrorView),
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
]
