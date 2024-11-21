# models.py

from django.db import models
from django.conf import settings

class Header(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    location = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
