from django.shortcuts import render
from qrstand.models import Stand
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def map(request):
    context = {}
    return render(request, 'qrstand/map.html', context)

def status(request):
    stands = Stand.objects.all()
    context = {stand.sid: [stand.top_scan_count, stand.bottom_scan_count] for stand in stands}
    return HttpResponse(json.dumps(context))

def reset(request,stand_sid):
    stand = get_object_or_404(Stand, sid=stand_sid)
    stand.reset(request)
    return HttpResponse(status=200)

def empty(request,stand_sid,location):
    stand = get_object_or_404(Stand, sid=stand_sid)
    stand.empty(request, location)
    context = {'msg': 'Tak for din henvendelse! Vi vil sikre os at standeren fyldes op snarest muligt.'}
    return render(request, 'qrstand/message.html', context)
