from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django import forms
import cups
from django.conf import settings
import os

class PrintAdvertForm(forms.Form):
    id = forms.CharField(max_length=10)
    #id = forms.IntegerField(max_value = 1000, min_value = 0)

def index(request):
    context = {}
    if request.method == 'POST':
        context = {'error': 'Invalid advert number. Try again.',}
        form = PrintAdvertForm(request.POST)
        if form.is_valid():
            id = str(form.cleaned_data['id'])
            path = settings.MEDIA_ROOT+'printables/'+id+'.pdf'
            if os.path.isfile(path):
                c = cups.Connection()
                if settings.JOBBANK_PRINTER in c.getPrinters().keys():
                    c.printFile(settings.JOBBANK_PRINTER, path, 'Jobbank '+id, {})
                    return redirect(reverse('jobbank:printing'))
                else:
                    context = {'error': "The printer "+settings.JOBBANK_PRINTER+" doesn't exist.",}
            else:
                context = {'error': 'The advert does not exist. Try again.'+path,}
    return render(request, 'jobbank/index.html', context)

def printing(request):
    return render(request, 'jobbank/printing.html')
