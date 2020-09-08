from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Organisation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='owner')
    name = models.CharField(max_length=50)
    website = models.CharField(max_length=50, default="https://www.")
    email_extension = models.CharField(max_length=50)   # e.g. gmail.com, ucl.ac.uk (without the @)
    company_description = models.TextField(default="")
    employees = models.ManyToManyField(User, blank=True)
    logo = models.FileField(default='logos/_.svg', upload_to='logos')

    def __str__(self):
        return self.name


class JobDescription(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='author')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, blank=True, null=True, related_name='job_org')

    title = models.CharField(max_length=50)
    salary = models.IntegerField()
    location = models.CharField(max_length=50)
    date_posted = models.DateTimeField(default=timezone.now)
    description_func = models.TextField(default="")
    description_non_func = models.TextField(default="")

    applicants = models.ManyToManyField(User, related_name='applicants', blank=True)
    recommended = models.ManyToManyField(User, related_name='recommended', blank=True)
    removed = models.ManyToManyField(User, related_name='removed', blank=True)

    # Insights from IBM about resume
    keywords = models.TextField(default='{}')
    keywords_req = models.TextField(default='[]')
    concepts = models.TextField(default='{}')
    category1 = models.CharField(max_length=100, default='None')
    category2 = models.CharField(max_length=100, default='None')
    category3 = models.CharField(max_length=100, default='None')

    # Insights from IBM based on question responses
    aggr_big5 = models.TextField(default='{}')
    aggr_openness = models.TextField(default='{}')
    aggr_conscien = models.TextField(default='{}')
    aggr_agreeabl = models.TextField(default='{}')
    aggr_extraver = models.TextField(default='{}')
    aggr_em_range = models.TextField(default='{}')
    needs = models.TextField(default='{}')
    values = models.TextField(default='{}')

    def __str__(self):
        return self.title


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, blank=True, null=True, related_name='account_org')
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, blank=True, null=True, related_name='job')
    job_start = models.IntegerField(default=0)
    education = models.TextField(default='[]')

    resume = models.FileField(default='resumes/_.pdf', upload_to='resumes')
    filename = models.CharField(max_length=50, default='my_resume.pdf')
    resume_plain_text = models.TextField(default="")

    # Insights from IBM about resume
    keywords = models.TextField(default='{}')
    concepts = models.TextField(default='{}')
    category1 = models.CharField(max_length=100, default='None')
    category2 = models.CharField(max_length=100, default='None')
    category3 = models.CharField(max_length=100, default='None')

    # Insights from IBM based on question responses
    pers_big5 = models.TextField(default='{}')
    pers_openness = models.TextField(default='{}')
    pers_conscien = models.TextField(default='{}')
    pers_agreeabl = models.TextField(default='{}')
    pers_extraver = models.TextField(default='{}')
    pers_em_range = models.TextField(default='{}')
    needs = models.TextField(default='{}')
    values = models.TextField(default='{}')

    def __str__(self):
        return self.user.username


class Question(models.Model):
    title = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.title


class QuestionResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.TextField(default="")
    language_tones = models.TextField(default="")
    social_tones = models.TextField(default="")

    def __str__(self):
        return self.user.username + " : " + self.question.title
