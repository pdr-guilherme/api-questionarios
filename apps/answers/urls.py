from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from apps.answers.api.views import (
    AdminSubmissionViewSet,
    AnswerViewSet,
    RespondentProgressViewSet,
    SubmissionViewSet,
    SurveyProgressViewSet,
)

app_name = "answers"

router = SimpleRouter()
router.register("submissions", SubmissionViewSet, basename="submission")

admin_router = SimpleRouter()
admin_router.register(
    "submissions", AdminSubmissionViewSet, basename="admin-submission"
)
submission_router = NestedSimpleRouter(router, "submissions", lookup="submission")
submission_router.register("answers", AnswerViewSet, basename="answer")

progress_router = SimpleRouter()
progress_router.register("surveys", SurveyProgressViewSet, basename="progress-survey")

progress_survey_router = NestedSimpleRouter(progress_router, "surveys", lookup="survey")
progress_survey_router.register(
    "respondents", RespondentProgressViewSet, basename="progress-respondent"
)

progress_urls = [
    *progress_router.urls,
    *progress_survey_router.urls,
]

urlpatterns = [
    path("admin/", include((admin_router.urls, "admin"))),
    path("progress/", include((progress_urls, "progress"), namespace="progress")),
    *router.urls,
    *submission_router.urls,
]
