from rest_framework.routers import SimpleRouter

from surveys.api.views import SurveyViewSet

app_name = "surveys"

router = SimpleRouter()
router.register("surveys", SurveyViewSet, basename="survey")

urlpatterns = router.urls
