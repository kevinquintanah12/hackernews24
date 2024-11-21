# models.py

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

class WorkExperience(models.Model):
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(default='')
    accomplishments = ArrayField(models.CharField(max_length=255), blank=True, default=list)  # ArrayField para el campo accomplishments
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.job_title} at {self.company}"
