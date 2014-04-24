from django.http import HttpResponse
from slideshow.models import Show, Device, DeviceLog, SlideGroup
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from slideshow.forms import LogMessageForm

@never_cache
def slideshowJsonByApiKey(request, apiKey):
    device = get_object_or_404(Device, api_key=apiKey)
    show = device.getSlideshow()
    slides = show.getSlides()
    timestamp = show.getLastModifiedTimestamp()
    if device.getLastModifiedTimestamp() > timestamp:
        timestamp = device.getLastModifiedTimestamp()
    context = {
              'slideshowVersion': '1382984863',
              'projectorVersion': timestamp,
              'slideshow': slides,
              'sync': show.getSync(),
              }
    return HttpResponse(json.dumps(context))

@csrf_exempt
def deviceLog(request, apiKey):
    device = get_object_or_404(Device, api_key=apiKey)
    form = LogMessageForm(request, device)
    if form.is_valid():
        form.save()
        return HttpResponse('Log message saved.')
    else:
        return HttpResponse(pprint.pformat(form.errors))
