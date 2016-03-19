from django.db import models


class Musician(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Album(models.Model):
    artist = models.ForeignKey('Musician', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    release_date = models.DateField()
    num_stars = models.IntegerField()


class Instrument(models.Model):
    name = models.CharField(max_length=255)


class MusicianInstrument(models.Model):
    musician = models.ForeignKey('Musician', primary_key=True, on_delete=models.CASCADE)
    instrument = models.ForeignKey('Instrument', primary_key=True, on_delete=models.CASCADE)
