
# models.py

from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Language(models.Model):
    name = models.CharField(max_length=100, default='')
    proficiency = models.CharField(max_length=50, default='')
    start_date = models.DateTimeField(default=now, blank=True)
    end_date = models.DateTimeField(default=now, blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
