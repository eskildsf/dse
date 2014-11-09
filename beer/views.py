#-*- encoding=UTF-8 -*-
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError
from django import forms
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from beer.models import DseUser, Product, Purchase, getUsersInLyngby, DeviceLog
import json
import time
import barcode_generator as bg
from django.conf import settings
from django.utils import timezone
import smtplib
from email.mime.text import MIMEText

def sendConfirmationEmail(obj):
    amount = obj.amount
    customer = obj.customer
    product = Product.objects.get(barcode = obj.barcode)
    product_name = product.name
    price = product.price
    account_name = obj.get_account_display()

    gmail_user = 'esf@studerende.dk'
    gmail_pwd = 'dk1425505'
    SUBJECT = u'Køb af %s stk %s til i alt %s kr' % (amount, product_name, int(amount)*int(price))
    TEXT = SUBJECT + u'\nKøbt på: ' + account_name
    
    message = MIMEText(TEXT.encode('utf-8'), _charset='utf-8')
    message['Subject'] = SUBJECT
    message['From'] = 'beer@studerende.dk'
    message['To'] = '%s@studerende.dk' % customer.lower()
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(message['From'], [message['To']], message.as_string())
        server.close()
    except Exception as e:
        return e
    return True

lines = settings.LCD_NLINES

class LCDForm(forms.Form):
    def __init__(self, *args, **kwargs):
        nlines = kwargs.pop('nlines')
        super(LCDForm, self).__init__(*args, **kwargs)
        for i in range(1, nlines+1):
            k = 'line%s' % i
            self.fields[k] = forms.CharField(max_length=100)

@csrf_exempt
def lcdAPI(request):
    if request.method == 'POST':
        form = LCDForm(request.POST, nlines = lines)
        if form.is_valid():
            timeout = 60
            for key, value in form.cleaned_data.iteritems():
                cache.set(key, value, timeout)
            return HttpResponse('')
        else:
            return HttpResponseServerError()
    elif request.method == 'GET':
        context = {}
        for i in range(1, lines+1):
            k = 'line%s' % i
            context[k] = cache.get(k, '')
        return HttpResponse(json.dumps(context))

def lcd(request):
    return render(request, 'beer/lcd.html')

def barcodes(request):
    members = getUsersInLyngby()
    initials = [(member.initials(), member.initials()) for member in members]
    barcodes = bg.GenerateBarcodes(initials)
    return HttpResponse(barcodes.render())

def products(request):
    obj = Product.objects.exclude(Q(price='(None)'))
    context = {}
    for e in obj:
        context[e.barcode] = {'name': e.name, 'price': e.price}
    return HttpResponse(json.dumps(context))

def customers(request):
    members = getUsersInLyngby()
    context = [e.initials() for e in members]
    return HttpResponse(json.dumps(context))

def accounts(request):
    context = {}
    for k, v in Purchase.ACCOUNT_CHOICES:
        context[k] = v
    return HttpResponse(json.dumps(context))

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['customer', 'barcode', 'price', 'amount', 'account']

@csrf_exempt
def makePurchase(request):
    form = PurchaseForm(request.POST)
    if form.is_valid():
        obj = form.save()
        context = {
        'customer': obj.customer,
        'barcode': obj.barcode,
        'price': obj.price,
        'amount': obj.amount,
        'account': obj.account,
        'id': obj.id,
        }
        sendConfirmationEmail(obj)
        return HttpResponse(json.dumps(context))
    return HttpResponseServerError()

class PurchaseDeleteForm(forms.Form):
    id = forms.IntegerField()

@csrf_exempt
def removePurchase(request):
    form = PurchaseDeleteForm(request.POST)
    if form.is_valid():
       try:
           obj = Purchase.objects.get(id=form.cleaned_data['id'])
           obj.delete()
       except ObjectDoesNotExist:
           return HttpResponseServerError()
       return HttpResponse()
    return HttpResponseServerError()

def latestPurchase(request, initials):
    initials = initials.upper();
    key = 'Bruger:%s' % initials
    # Cheap way to check if user exists.
    member = get_object_or_404(DseUser, page=key)
    # If no purchases just return
    if Purchase.objects.filter(customer = initials).count() == 0:
        return HttpResponse()
    purchase = Purchase.objects.filter(customer = initials).order_by('-id')[0]
    product = Product.objects.get(barcode = purchase.barcode)
    context = {
    'customer': purchase.customer,
    'barcode': purchase.barcode,
    'product': product.name,
    'price': purchase.price,
    'amount': purchase.amount,
    'account': purchase.account,
    'id': purchase.id,
    }
    return HttpResponse(json.dumps(context))


class LogMessageForm(forms.ModelForm):
    class Meta:
        model = DeviceLog
        exclude = ('date', 'remote_ip', 'remote_host',)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(LogMessageForm, self).__init__(*args, **kwargs)
    def save(self, commit=True):
        instance = super(LogMessageForm, self).save(commit=False)
        instance.date = timezone.now()
        instance.remote_ip = self.request.META['REMOTE_ADDR']
        if getattr(settings, 'REMOTELOG_DNS_LOOKUP_ENABLED', False):
            hostname, aliaslist, ipaddrlist = \
              socket.gethostbyaddr(instance.remote_ip)
            instance.remote_host = hostname
        elif 'REMOTE_HOST' in self.request.META:
            instance.remote_host = self.request.META['REMOTE_HOST']
        # replace the string 'None' with None in the follow fields:
        for field in ('exc_info', 'exc_text', 'args'):
            if getattr(instance, field) == 'None':
                setattr(instance, field, None)
        if commit:
            instance.save()
        return instance

@csrf_exempt
def deviceLog(request):
    if request.method == 'POST':
        form = LogMessageForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return HttpResponse()
        else:
            return HttpResponseServerError()
    elif request.method == 'GET':
        log_records = DeviceLog.objects.order_by('-date')[:25]
        statements = []
        for record in log_records:
            obj = {'date': int(time.mktime(record.date.timetuple())), 'message': record.formatted_message, 'level': record.levelname}
            statements.append(obj)
        statements = statements[::-1]
        return HttpResponse(json.dumps(statements))

def log(request):
    return render(request, 'beer/log.html')
