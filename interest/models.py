# models.py

from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Interest(models.Model):
    name = models.CharField(max_length=100, default='')
    description = models.TextField(default='')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
