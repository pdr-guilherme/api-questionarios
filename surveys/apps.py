from django.apps import AppConfig


class SurveysConfig(AppConfig):
    name = "surveys"

    def ready(self) -> None:
        import surveys.signals  # noqa: F401
