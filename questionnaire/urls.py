from django.conf.urls import patterns, url
from questionnaire import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<survey_id>\d+)/$', views.survey, name='survey'),
    url(r'^export/(?P<survey_id>\d+)/$', views.export, name='export'),
#    url(r'^printing/(?P<survey_id>\d+)/$', views.printing, name='printing')
    url(r'^callback/$', views.callback, name='callback'),
)


