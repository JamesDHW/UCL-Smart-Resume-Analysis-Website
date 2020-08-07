from django.contrib import admin

from .models import Applicant
from .models import JobDescription

admin.site.register(Applicant)
admin.site.register(JobDescription)

