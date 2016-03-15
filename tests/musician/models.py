from django.db import models


class Instrument(models.Model):
    name = models.CharField(max_length=255)


class Musician(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Album(models.Model):
    artist = models.ForeignKey('Musician', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    release_date = models.DateField()
    num_stars = models.IntegerField()


class MusicianInstrument(models.Model):
    musician = models.ForeignKey('Musician', on_delete=models.CASCADE)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE)
