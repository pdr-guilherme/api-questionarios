from rest_framework.routers import SimpleRouter

from apps.users.api.views import RespondentViewSet

app_name = "users"

router = SimpleRouter()
router.register("respondents", RespondentViewSet, basename="respondent")

urlpatterns = router.urls
