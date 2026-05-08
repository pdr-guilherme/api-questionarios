from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from apps.answers.api.views import (
    AdminSubmissionViewSet,
    AnswerViewSet,
    SubmissionViewSet,
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

urlpatterns = [
    path("admin/", include((admin_router.urls, "admin"))),
    *router.urls,
    *submission_router.urls,
]
