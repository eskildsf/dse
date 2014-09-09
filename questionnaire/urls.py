from django.conf.urls import patterns, url
from questionnaire import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<survey_id>\d+)/$', views.survey, name='survey'),
    url(r'^(?P<survey_id>\d+)/(?P<company_id>\d+)/$', views.company, name='company'),
#    url(r'^printing/(?P<survey_id>\d+)/$', views.printing, name='printing')
    url(r'^callback/$', views.callback, name='callback'),
)


