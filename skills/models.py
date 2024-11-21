# models.py

from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=50)  # Por ejemplo: "Beginner", "Intermediate", "Advanced"
    description = models.TextField(default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
