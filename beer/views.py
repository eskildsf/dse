from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
from django import forms
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from beer.models import DseUser
import json
import barcode_generator as bg

lines = 4

class ApiForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        for i in range(1, kwargs['nlines']+1):
            k = 'line%s' % i
            v = forms.CharField(max_length=100)
            self.fields[k] = v

@csrf_exempt
def apiIn(request):
    form = ApiForm(request.POST, nlines = lines)
    if form.is_valid():
        timeout = 15
        for key, value in form.cleaned_data.iteritems():
            cache.set(key, value, timeout)
        return HttpResponse('')
    return HttpResponseServerError()

def apiOut(request):
    context = {}
    for i in range(1, lines+1):
        k = 'line%s' % i
        context[k] = cache.get(k, '')
    return HttpResponse(json.dumps(context))

def index(request):
    return render(request, 'beer/index.html')

def barcodes(request):
    members = DseUser.objects.filter(department='lyngby').exclude(Q(status='emeritus')|Q(status='udmeldt')|Q(status='passiv'))
    initials = [(member.initials(), member.initials()) for member in members]
    barcodes = bg.GenerateBarcodes(initials, 200, 300)
    return HttpResponse(barcodes.render())
