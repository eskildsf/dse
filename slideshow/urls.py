from django.conf.urls import patterns, url, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from slideshow import views

urlpatterns = patterns('',
    url(r'^api/json/(?P<apiKey>.*)/$', views.slideshowJsonByApiKey, name='slideshowAjaxByApiKey'),
    url(r'^api/log/(?P<apiKey>.*)/$', views.deviceLog, name='log'),
    url(r'^api/devices/$', views.devices, name='devices'),
)
