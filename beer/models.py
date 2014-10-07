#-*- encoding=UTF-8 -*-
import re
from django.db import models
import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)

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
