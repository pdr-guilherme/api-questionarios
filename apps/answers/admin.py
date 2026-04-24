from django.contrib import admin

from apps.answers.models import Answer, Submission, SurveyAccess

admin.site.register(SurveyAccess)
admin.site.register(Submission)
admin.site.register(Answer)
