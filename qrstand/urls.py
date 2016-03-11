from django.conf.urls import url
from . import views

urlpatterns = [#patterns('',
    url(r'^$', views.map, name='map'),
    url(r'^status/$', views.status, name='status'),
    url(r'^reset/(?P<stand_sid>\d+)/$', views.reset, name='reset'),
    url(r'^empty/(?P<stand_sid>\d+)/(?P<location>[UD])/$', views.empty, name='empty'),
]#)
