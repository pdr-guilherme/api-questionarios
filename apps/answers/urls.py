from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from apps.answers.api.views import AnswerViewSet, SubmissionViewSet

app_name = "answers"

router = SimpleRouter()
router.register("submissions", SubmissionViewSet, basename="submission")

submission_router = NestedSimpleRouter(router, "submissions", lookup="submission")
submission_router.register("answers", AnswerViewSet, basename="answer")

urlpatterns = [
    *router.urls,
    *submission_router.urls,
]
