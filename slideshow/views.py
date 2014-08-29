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
    device.setActive()
    context = {
              'slides': slides,
              'sync': show.getSync(),
              }
    return HttpResponse(json.dumps(context))

@csrf_exempt
def deviceLog(request, apiKey):
    device = get_object_or_404(Device, api_key=apiKey)
    form = LogMessageForm(request, device)
    if form.is_valid():
        form.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)

def devices(request):
    query = DeviceLog.objects.raw('SELECT a.* FROM slideshow_devicelog a LEFT JOIN slideshow_devicelog b ON (a.device_id = b.device_id AND a.id < b.id) WHERE b.id IS NULL')
    ips = []
    for e in query:
        interfaces = eval(e.network_interfaces, {'__builtins__':None}, {})
        interface = interfaces[0][1]['addr']
        ips.append({'name': e.device.name, 'ip': interface})
    return HttpResponse(json.dumps(ips))
