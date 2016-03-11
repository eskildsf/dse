from django.conf.urls import patterns, url
from . import views

urlpatterns = [#patterns('slideshow.views',
    url(r'^api/json/(?P<apiKey>.*)/$', views.slideshowJsonByApiKey, name='slideshowJsonByApiKey'),
    url(r'^api/log/(?P<apiKey>.*)/$', views.deviceLog, name='deviceLog'),
    url(r'^api/devices/$', views.devices, name='devices'),
]#)
