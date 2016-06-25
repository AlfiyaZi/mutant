from django.db import models


class Authority(models.Model):
    class Meta:
        verbose_name_plural = "Authorities"

    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)


class FundingInstitution(models.Model):
    class Meta:
        verbose_name_plural = "Funding Institutions"
    CATEGORY_COUNTRY = "COUNTRY"
    CATEGORY_TYPE = "TYPE"
    CATEGORY_DEPARTMENT = "DEPARTMENT"
    CATEGORY_AGENCY = "AGENCY"
    CATEGORY_FUNDING_UNIT = "FUNDING_UNIT"
    CATEGORIES = (
        (CATEGORY_COUNTRY, "Country"),
        (CATEGORY_TYPE, "Type"),
        (CATEGORY_DEPARTMENT, "Department"),
        (CATEGORY_AGENCY, "Agency"),
        (CATEGORY_FUNDING_UNIT, "Funding unit"),
    )

    code = models.CharField(unique=True, max_length=10)
    parent = models.ForeignKey("FundingInstitution", null=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Canonical name", max_length=100)
    standalone_name = models.BooleanField(default=False, verbose_name="Prefix with parent name it true")
    category = models.CharField(choices=CATEGORIES, max_length=20)
    ancestor_or_self = models.CharField(blank=True, max_length=255)


class Award(models.Model):
    class Meta:
        verbose_name_plural = "Awards"

    authority = models.ForeignKey("Authority", on_delete=models.CASCADE)
    pid = models.CharField(verbose_name="Persistent ID", max_length=100)
    parent = models.ForeignKey("Award", on_delete=models.CASCADE)
    number = models.CharField(max_length=64)
    full_number = models.CharField(max_length=96)
    project_start = models.DateTimeField()
    project_end = models.DateTimeField()
    fiscal_year = models.CharField(max_length=255)
    budget_start = models.DateTimeField()
    budget_end = models.DateTimeField()
    title = models.CharField(max_length=256)
    funding_institution = models.ForeignKey("FundingInstitution", on_delete=models.CASCADE)
    attributes = models.CharField(max_length=1024)


class Person(models.Model):
    class Meta:
        verbose_name_plural = "People"

    pid = models.CharField(verbose_name="Persistent ID", max_length=100)
    first_name = models.CharField(max_length=100)
    given_names = models.CharField(max_length=256)
    last_name = models.CharField(max_length=100)


class Account(models.Model):
    class Meta:
        unique_together = ['pid', 'authority']
        verbose_name_plural = "Accounts"

    pid = models.CharField(verbose_name="Persistent ID", max_length=100)
    authority = models.ForeignKey("Authority", on_delete=models.CASCADE)
    email = models.EmailField()
    username = models.CharField(max_length=100)
    attributes = models.CharField(max_length=1024)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)


class Awardee(models.Model):
    class Meta:
        verbose_name_plural = "Awardees"

    pid = models.CharField(verbose_name="Persistent ID", max_length=100)
    name = models.CharField(max_length=256)
    award_id = models.IntegerField()
    attributes = models.CharField(max_length=1024)


class AwardAwardee(models.Model):
    class Meta:
        verbose_name_plural = "AwardAwardees"

    award = models.ForeignKey("Award", primary_key=True, on_delete=models.CASCADE)
    awardee = models.ForeignKey("Awardee", primary_key=True, on_delete=models.CASCADE)


class AwardPerson(models.Model):
    class Meta:
        verbose_name_plural = "AwardPeople"

    award = models.ForeignKey("Award", primary_key=True, on_delete=models.CASCADE)
    person = models.ForeignKey("Person", primary_key=True, on_delete=models.CASCADE)
