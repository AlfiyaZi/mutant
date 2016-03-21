from django.db import models


class Author(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=255)
    username = models.CharField(primary_key=True, max_length=30)
