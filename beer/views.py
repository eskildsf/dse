from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
from django import forms
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from beer.models import DseUser
import json

class ApiForm(forms.Form):
    line1 = forms.CharField(max_length=100)
    line2 = forms.CharField(max_length=100)
    line3 = forms.CharField(max_length=100)
    line4 = forms.CharField(max_length=100)

@csrf_exempt
def apiIn(request):
    form = ApiForm(request.POST)
    if form.is_valid():
        cache.set('lcd_1', form.cleaned_data['line1'])
        cache.set('lcd_2', form.cleaned_data['line2'])
        cache.set('lcd_3', form.cleaned_data['line3'])
        cache.set('lcd_4', form.cleaned_data['line4'])
        return HttpResponse('')
    return HttpResponseServerError()

def apiOut(request):
    context = {'line1': cache.get('lcd_1', ''),
               'line2': cache.get('lcd_2', ''),
               'line3': cache.get('lcd_3', ''),
               'line4': cache.get('lcd_4', '')}
    return HttpResponse(json.dumps(context))

def index(request):
    return render(request, 'beer/index.html')

def barcodes(request):
    members = DseUser.objects.filter(all()
    initials = [member.initials() for member in members]
    return HttpResponse(initials)
