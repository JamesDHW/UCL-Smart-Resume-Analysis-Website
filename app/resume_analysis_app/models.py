from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Organisation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='owner')
    name = models.CharField(max_length=50)
    email_extension = models.CharField(max_length=50)   # e.g. gmail.com, ucl.ac.uk (without the @)
    company_description = models.TextField(default="")
    employees = models.ManyToManyField(User, blank=True)

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
    current_employees = models.ManyToManyField(User, related_name='employees')

    # Separate requests for keywords
    keywords_func = models.TextField(default="")
    keywords_non_func = models.TextField(default="")
    # Joint request for concepts + categories
    concepts = models.TextField(default="")
    categories = models.TextField(default="")

    def __str__(self):
        return self.title


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, blank=True, null=True, related_name='account_org')
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, blank=True, null=True, related_name='job')

    resume = models.FileField(default='resumes/_.pdf', upload_to='resumes')
    filename = models.CharField(max_length=50, default='my_resume.pdf')
    resume_plain_text = models.TextField(default="")

    keywords = models.TextField(default="")
    concepts = models.TextField(default="")
    categories = models.TextField(default="")
    personality = models.TextField(default="")

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
    tones = models.TextField(default="")

    def __str__(self):
        return self.user.username + " : " + self.question.title
