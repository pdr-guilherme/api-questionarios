from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from apps.surveys.api.views import (
    AssignedSurveyViewSet,
    OptionViewSet,
    QuestionImageViewSet,
    QuestionViewSet,
    SurveyViewSet,
)

app_name = "surveys"

router = SimpleRouter()
router.register("surveys", SurveyViewSet, basename="survey")
router.register("questions", QuestionViewSet, basename="question")
router.register("assigned-surveys", AssignedSurveyViewSet, basename="assigned-survey")

questions_router = NestedSimpleRouter(router, "questions", lookup="question")
questions_router.register("images", QuestionImageViewSet, basename="image")
questions_router.register("options", OptionViewSet, basename="option")

urlpatterns = [
    *router.urls,
    *questions_router.urls,
]
