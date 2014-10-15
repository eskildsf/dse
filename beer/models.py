#-*- encoding=UTF-8 -*-
import re
from django.db import models
from django.db.models import Q
import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)

def getUsersInLyngby():
    return DseUser.objects.filter(department='lyngby').exclude(Q(status='emeritus')|Q(status='udmeldt')|Q(status='passiv'))

class DseUser(models.Model):
    name = models.CharField(max_length = 255, editable = False, db_column = 'navn')
    page = models.CharField(max_length = 255, editable = False, db_column = '_page', primary_key = True)
    phone_number = models.CharField(max_length = 255, editable = False, db_column = 'telefon')
    department = models.CharField(max_length = 255, editable = False, db_column = 'afdeling')
    status = models.CharField(max_length =255, editable = False, db_column = 'status')
    group = models.CharField(max_length =255, editable = False, db_column = 'grupper')
    def initials(self):
        return self.page[7:10]
    def group_list(self):
        regex = '\\[\\[(.*?)\\]\\]'
        rg = re.compile(regex, re.IGNORECASE|re.DOTALL)
        h = self.group
        if self.group is not None:
            result = rg.findall(self.group)
        else:
            result = []
        return result
    def groups(self):
        return ', '.join(self.group_list())
    class Meta:
        db_table = 'Brugerboks'
        in_db = 'wikidata'
        verbose_name = 'DSE User'
        verbose_name_plural = 'DSE Users'

class Product(models.Model):
    name = models.CharField(max_length = 255, editable = False, db_column = 'navn')
    price = models.CharField(max_length = 255, editable = False, db_column = 'pris')
    barcode = models.CharField(max_length = 255, editable = False, db_column = 'ean')
    class Meta:
        db_table = u'Ølklubsvare'
        in_db = 'wikidata'

def barcode_choices():
    products = Product.objects.all()
    return [(e.barcode, e.name) for e in products]

class Purchase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=255)
    barcode = models.CharField(max_length=255, choices = barcode_choices())
    price = models.IntegerField()
    amount = models.IntegerField(default=1)
    ACCOUNT_CHOICES = (
    ('E', 'Egen konto'),
    ('R', u'Rengøringsøl'),
    )
    account = models.CharField(max_length=10, choices = ACCOUNT_CHOICES, default = 'E')

class DeviceLog(models.Model):
    date = models.DateTimeField()
    remote_ip = models.CharField(max_length=40)
    remote_host = models.CharField(max_length=255)

    levelno = models.IntegerField()
    levelname = models.CharField(max_length=255)

    name = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    pathname = models.CharField(max_length=255)
    funcName = models.CharField(max_length=255)
    lineno = models.IntegerField()

    msg = models.TextField()
    exc_info = models.TextField(null=True, blank=True)
    exc_text = models.TextField(null=True, blank=True)
    args = models.TextField(null=True, blank=True)

    threadName = models.CharField(max_length=255)
    thread = models.FloatField()
    created = models.FloatField()
    process = models.IntegerField()
    relativeCreated = models.FloatField()
    msecs = models.FloatField()
    class Meta:
        ordering = ('-date',)
    def __unicode__(self):
        return '%s: %s' % (self.date, self.formatMessage())
    def _get_short_msg(self):
        msg = self.msg[0:60]
        if len(self.msg) > 60:
            msg += '...'
        return msg
    short_msg = property(_get_short_msg)
    def formatMessage(self):
        msg = self.msg
        if len(self.args) > 2:
            msg = msg.replace('%d', '%s')
            msg = msg.replace('%f', '%s')
            withoutParen = self.args[1:-2]
            # Split by comma and remove whitespace
            arg = [x.strip() for x in withoutParen.split(',')]
            return msg % tuple(arg)
        return msg
    formatted_message = property(formatMessage)
