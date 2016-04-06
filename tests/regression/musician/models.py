from django.db import models


class Musician(models.Model):
    class Meta:
        verbose_name_plural = "Musicians"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Album(models.Model):
    class Meta:
        verbose_name_plural = "Albums"

    artist = models.ForeignKey("Musician", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    release_date = models.DateField()
    num_stars = models.IntegerField()


class Instrument(models.Model):
    class Meta:
        verbose_name_plural = "Instruments"

    name = models.CharField(max_length=255)


class MusicianInstrument(models.Model):
    class Meta:
        verbose_name_plural = "MusicianInstruments"

    musician = models.ForeignKey("Musician", primary_key=True, on_delete=models.CASCADE)
    instrument = models.ForeignKey("Instrument", primary_key=True, on_delete=models.CASCADE)
