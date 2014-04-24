from django.conf.urls import patterns, url
from jobbank import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^printing/$', views.printing, name='printing'),
)
