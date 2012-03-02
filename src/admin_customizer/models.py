import sys

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import class_prepared
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.management import update_contenttypes
from django.db.models import get_apps, get_models, signals
from django.utils.encoding import smart_unicode
from django.utils.importlib import import_module

from .managers import AvailableFieldManager

class AdminSite(models.Model):
    slug = models.SlugField()
    def __unicode__(self):
        return u"admin:%s" % self.slug


class RegisteredModel(models.Model):
    model = models.ForeignKey("contenttypes.ContentType")
    admin_site = models.ForeignKey("AdminSite")
    list_display = models.ManyToManyField(
        "AvailableField",
        related_name = "registeredmodels_with_list_display",
        blank = True,
    )
    list_filter = models.ManyToManyField(
        "AvailableField",
        related_name = "registeredmodels_with_list_filter",
        blank = True,
    )
    search_fields = models.ManyToManyField(
        "AvailableField",
        related_name = "registeredmodels_with_search_fields",
        blank = True,
    )
    raw_id_fields = models.ManyToManyField("AvailableField",
        related_name = "+",
        limit_choices_to = {'type__in': ('oto', 'fk', 'mtm')},
        blank = True,
    )

class AvailableField(models.Model):
    model = models.ForeignKey("contenttypes.ContentType", related_name="+")
    name = models.TextField()
    RELATION_TYPES = ('fk', 'mtm', 'oto', 'rev')
    TYPES = (
        ('fk', _("Foreign key field")),
        ('mtm', _("Many to many field")),
        ('oto', _("One to one field")),
        ('rev', _("One to many (reverse foreign key) field")),
        #('span', _("Field from related model"))
        ('other', _("Other type of field"))
    )
    type = models.CharField(max_length=10, choices=TYPES)
    target = models.ForeignKey(
        "contenttypes.ContentType",
        null = True,
        blank = True,
        related_name = "+"
    )
    through = models.ForeignKey("self", null=True, blank=True)

    objects = AvailableFieldManager()

    def __unicode__(self):
        return u"AvailableField #%s '%s | %s | %s%s'" % (
            self.id,
            self.model.model,
            self.name,
            '%s: %s' % (self.type, self.target) if self.target else self.type,
            ' | through: #%s' % self.through.id if self.through else ''
        )