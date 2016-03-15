from django.db import models


class Author(models.Model):
    username = models.CharField(primary_key=True, max_length=30)
    email = models.EmailField()
    password = models.CharField(max_length=255)
