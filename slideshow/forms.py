import socket
import datetime

from django import forms
from django.conf import settings
from django.utils import timezone

from slideshow.models import Device, DeviceLog

class LogMessageForm(forms.ModelForm):
    class Meta:
        model = DeviceLog
        exclude = ('device', 'date', 'remote_ip', 'remote_host',)
    
    def __init__(self, request, device):
        self.request = request
        self.device = device
        super(LogMessageForm, self).__init__(request.REQUEST)
    
    def save(self, commit=True):
        instance = super(LogMessageForm, self).save(commit=False)
        instance.device = self.device
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
