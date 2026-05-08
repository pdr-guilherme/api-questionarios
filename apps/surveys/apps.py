from django.apps import AppConfig


class SurveysConfig(AppConfig):
    name = "apps.surveys"

    def ready(self) -> None:
        import apps.surveys.signals  # noqa: F401
