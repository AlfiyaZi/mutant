from django.db import models


class Musician(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    instrument = models.CharField(max_length=255)


class Album(models.Model):
    artist = models.ForeignKey(othermodel='Musician')
    name = models.CharField(max_length=255)
    release_date = models.DateField()
    num_stars = models.IntegerField()
