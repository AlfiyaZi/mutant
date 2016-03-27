import logging

import simplejson as json
from awards.history.models import HistoricalRecords
from django.db import models, connection
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from jsonfield import JSONField


class AuthorityKey(models.ForeignKey):
    description = "Authority key"

    def __init__(self, *args, **kwargs):
        super(AuthorityKey, self).__init__('Authority', db_constraint=False)


class PidField(models.CharField):
    description = "Persistent ID"

    def __init__(self, *args, **kwargs):
        kwargs['db_column'] = 'pid'
        kwargs['verbose_name'] = "Persistent ID"
        kwargs['max_length'] = 100
        super(PidField, self).__init__(*args, **kwargs)


class DeletedField(models.BooleanField):
    """
    Field that stores active/deleted status, but shows them as strings
    """
    ACTIVE = False
    DELETED = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', self.ACTIVE)
        super(DeletedField, self).__init__(*args, **kwargs)


@python_2_unicode_compatible
class Account(models.Model):

    class Meta:
        unique_together = ("pid", "authority")

    authority = AuthorityKey()
    pid = PidField()

    person = models.ForeignKey('Person', related_name='accounts')
    email = models.EmailField(max_length=254, blank=True)  # Django 1.8+ remove max_length
    username = models.CharField(max_length=100, blank=True)
    attributes = JSONField(blank=True)

    def __str__(self):
        return self.email or self.username


@python_2_unicode_compatible
class Authority(models.Model):

    class Meta:
        verbose_name_plural = 'Authorities'

    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Award(models.Model):

    class Meta:
        unique_together = ('pid', 'authority')

    history = HistoricalRecords()

    authority = AuthorityKey()
    pid = PidField()
    deleted = DeletedField()

    parent = models.ForeignKey('self', null=True, blank=True)
    number = models.CharField(max_length=64)
    full_number = models.CharField(max_length=96, null=True)
    sub_award = models.CharField(max_length=10, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    project_start = models.DateField("When project started", null=True, blank=True)
    project_end = models.DateField("When project completed", null=True, blank=True)
    budget_start = models.DateField(null=True, blank=True)
    budget_end = models.DateField(null=True, blank=True)
    fiscal_year = models.PositiveSmallIntegerField(null=True, blank=True)
    attributes = JSONField(blank=True)
    funding_institution = models.ForeignKey('FundingInstitution')

    prefetch = ('persons', 'awardees')

    def __str__(self):
        return self.title


class AwardAwardeeManager(models.Manager):

    class Meta:
        default_permissions = tuple()


    def create(self, award, awardee):
        if not awardee.pk:
            raise Exception("Awardee has not been saved")

        if isinstance(award, Award):
            award_id = award.pk
        else:
            award_id = award

        if not award_id:
            raise Exception("Award has not been saved / specified")

        cursor = connection.cursor()

        params = {
            "table": self.model._meta.db_table,
            "award_field": self.model.award.field.attname,
            "awardee_field": self.model.awardee.field.attname,
            "award_id": award_id,
            "awardee_id": awardee.pk,
        }

        sql = "INSERT INTO %(table)s (%(award_field)s, %(awardee_field)s) " \
              "SELECT %(award_id)d, %(awardee_id)d " \
              "WHERE NOT EXISTS (SELECT 1 FROM %(table)s " \
              "WHERE %(award_field)s=%(award_id)d " \
              "AND %(awardee_field)s=%(awardee_id)d)" % params

        return cursor.execute(sql)


@python_2_unicode_compatible
class AwardAwardee(models.Model):

    class Meta:
        unique_together = ('award', 'awardee')

    objects = AwardAwardeeManager()

    award = models.ForeignKey('Award', related_name='awardees', db_constraint=False)
    awardee = models.ForeignKey('Awardee', related_name='awards', db_constraint=False)

    def __str__(self):
        return "%s - %s" % (self.award, self.awardee)


@python_2_unicode_compatible
class Awardee(models.Model):
    """
    Award recipient
    """
    class Meta:
        unique_together = ("pid", "authority")

    authority = AuthorityKey()
    pid = PidField()
    deleted = DeletedField()

    name = models.CharField(max_length=255, null=True)
    attributes = JSONField(blank=True)

    def __str__(self):
        return self.name


class AwardPersonManager(models.Manager):

    class Meta:
        default_permissions = tuple()


    def create(self, award, person, role):
        """
        Creates link between award, person and role ONLY if not exists
        award, person, role parameters can be instances or integers
        """
        cursor = connection.cursor()

        params = {
            "table": self.model._meta.db_table,
            "award_id": getattr(award, "pk", award),
            "person_id": getattr(person, "pk", person),
            "role_id": getattr(role, "pk", role)
        }

        sql = "INSERT INTO %(table)s (award_id, person_id, role_id) " \
              "SELECT %(award_id)d, %(person_id)d, %(role_id)d " \
              "WHERE NOT EXISTS (SELECT 1 FROM %(table)s " \
              "WHERE award_id=%(award_id)d " \
              "AND person_id=%(person_id)d " \
              "AND role_id=%(role_id)d)" % params

        return cursor.execute(sql)


@python_2_unicode_compatible
class AwardPerson(models.Model):
    """
    Person's role in an award
    """

    class Meta:
        unique_together = ('award', 'person', 'role')

    objects = AwardPersonManager()

    # disabled history for the model
    # history = HistoricalRecords()

    award = models.ForeignKey('Award', related_name='persons', db_constraint=False)
    person = models.ForeignKey('Person', related_name='awards', db_constraint=False)
    role = models.ForeignKey('Role', related_name='awards', db_constraint=False)

    def __str__(self):
        return "%s (%s) - %s" % (self.person, self.role, self.award)


class BatchManager(models.Manager):

    def pending(self):
        """
        Fetch requests pending for processing
        """
        return self.filter(status=Batch.STATUS_NEW)


@python_2_unicode_compatible
class Batch(models.Model):

    class Meta:
        ordering = ['pk']

    objects = BatchManager()

    STATUS_NEW = 0
    STATUS_PROCESSED = 1
    STATUS_DECLINED = 2
    STATUSES = (
        (STATUS_NEW, "Pending"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_DECLINED, "Declined")
    )

    data = JSONField("Input data")
    status = models.PositiveSmallIntegerField(choices=STATUSES, default=STATUS_NEW)
    result = JSONField("Result of batch processing")
    errors = models.PositiveIntegerField("Number of errors", default=0)

    def ready_for_process(self):
        return self.status == Batch.STATUS_NEW

    def __str__(self):
        return "Batch %d" % self.pk

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class FundingInstitution(models.Model):
    CATEGORY_COUNTRY = 'COUNTRY'
    CATEGORY_TYPE = 'TYPE'
    CATEGORY_DEPARTMENT = 'DEPARTMENT'
    CATEGORY_AGENCY = 'AGENCY'
    CATEGORY_UNIT = 'FUNDING_UNIT'

    CATEGORIES = (
        (CATEGORY_COUNTRY, "Country"),
        (CATEGORY_TYPE, "Type"),
        (CATEGORY_DEPARTMENT, "Department"),
        (CATEGORY_AGENCY, "Agency"),
        (CATEGORY_UNIT, "Funding unit")
    )

    code = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey('self', null=True)
    name = models.CharField("Canonical name", max_length=100)
    standalone_name = models.BooleanField("Prefix with parent name if true", default=False)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    ancestor_or_self = JSONField(blank=True)

    def __str__(self):
        if self.standalone_name and self.parent:
            return "%s - %s" % (self.parent.name, self.name)
        return self.name

    @staticmethod
    def dump_ancestor(ancestor_or_self):
        return json.dumps(ancestor_or_self)

    @staticmethod
    def load_ancestor(ancestor_or_self):
        return json.loads(ancestor_or_self or '[]')

    def recursive_ancestor_or_self(self):
        if self.parent is not None:
            return [self.code] + self.parent.recursive_ancestor_or_self()
        else:
            return [self.code]


@receiver(post_save, sender=FundingInstitution, dispatch_uid="update_ancestor")
def update_ancestor(sender, instance, **kwargs):
    if kwargs['created'] or not kwargs['update_fields'] or 'parent' in kwargs['update_fields']:
        ancestor_or_self = instance.recursive_ancestor_or_self()
        if instance.ancestor_or_self != ancestor_or_self:
            FundingInstitution.objects.filter(id=instance.id).update(
                ancestor_or_self=ancestor_or_self
            )
        if not kwargs['raw']:
            for child in instance.fundinginstitution_set.all():
                post_save.send(
                    sender=sender,
                    instance=child,
                    raw=kwargs['raw'],
                    created=kwargs['created'],
                    using=kwargs['using'],
                    update_fields=kwargs['update_fields'],
                )


@python_2_unicode_compatible
class Person(models.Model):

    class Meta:
        unique_together = ("pid", "authority")

    history = HistoricalRecords()

    authority = AuthorityKey()
    pid = PidField()
    deleted = DeletedField()

    first_name = models.CharField(max_length=100, blank=True)
    given_names = models.CharField("Given names", max_length=255, blank=True)
    last_name = models.CharField("Family name", max_length=100, blank=True)

    prefetch = ('accounts',)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


@python_2_unicode_compatible
class Role(models.Model):

    class Meta:
        unique_together = ("pid", "authority")

    authority = AuthorityKey()
    pid = PidField()

    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
