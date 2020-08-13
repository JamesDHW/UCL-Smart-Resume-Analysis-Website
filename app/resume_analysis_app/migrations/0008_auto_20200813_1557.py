# Generated by Django 3.0.8 on 2020-08-13 15:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resume_analysis_app', '0007_auto_20200813_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobdescription',
            name='applicants',
            field=models.ManyToManyField(blank=True, related_name='applicants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='employees',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
