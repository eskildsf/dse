from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
from django import forms
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from beer.models import DseUser, Product, Purchase, getUsersInLyngby
import json
import barcode_generator as bg
from django.conf import settings

lines = settings.LCD_NLINES

class LCDForm(forms.Form):
    def __init__(self, *args, **kwargs):
        nlines = kwargs.pop('nlines')
        super(LCDForm, self).__init__(*args, **kwargs)
        for i in range(1, nlines+1):
            k = 'line%s' % i
            self.fields[k] = forms.CharField(max_length=100)

@csrf_exempt
def lcdIn(request):
    form = LCDForm(request.POST, nlines = lines)
    if form.is_valid():
        timeout = 15
        for key, value in form.cleaned_data.iteritems():
            cache.set(key, value, timeout)
        return HttpResponse('')
    return HttpResponseServerError()

def lcdOut(request):
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
    barcodes = bg.GenerateBarcodes(initials, 200, 300)
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
        return HttpResponse()
    return HttpResponseServerError()

class PurchaseDeleteForm(forms.ModelForm):
    id = forms.IntegerField()

@csrf_exempt
def removePurchase(request):
    form = PurchaseForm(request.POST)
    if form.is_valid():
       try:
           obj = Purchase.objects.get(id=form.cleaned_data['id'])
           obj.delete()
       except ObjectDoesNotExist:
           return HttpResponseServerError()
       return HttpResponse()
    return HttpResponseServerError()
