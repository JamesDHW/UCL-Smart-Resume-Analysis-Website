from django.contrib import admin

from .models import Account, JobDescription, Organisation, Question, QuestionResponse

admin.site.register(Account)
admin.site.register(JobDescription)
admin.site.register(Organisation)
admin.site.register(Question)
admin.site.register(QuestionResponse)

