from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<survey_id>\d+)/$', views.survey, name='survey'),
    url(r'^export/(?P<survey_id>\d+)/$', views.export, name='export'),
    url(r'^callback/$', views.callback, name='callback'),
]


