from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class JobDescription(models.Model):
    title = models.CharField(max_length=50)
    salary = models.IntegerField()
    location = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='author')
    date_posted = models.DateTimeField(default=timezone.now)
    description_func = models.TextField(default="")
    description_non_func = models.TextField(default="")
    applicants = models.ManyToManyField(User)

    # Separate requests for keywords
    keywords_func = models.TextField(default="")
    keywords_non_func = models.TextField(default="")
    # Joint request for concepts + categories
    concepts = models.TextField(default="")
    categories = models.TextField(default="")

    def __str__(self):
        return self.title


class Applicant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(default='resumes/CV.pdf', upload_to='resumes')
    filename = models.CharField(max_length=50, default='my_resume.pdf')
    resume_plain_text = models.TextField(default="")

    keywords = models.TextField(default="")
    concepts = models.TextField(default="")
    categories = models.TextField(default="")

    def __str__(self):
        return self.user.username
