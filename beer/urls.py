from django.conf.urls import patterns, url, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from beer import views

urlpatterns = patterns('',
    url(r'^api/in/$', views.apiIn, name='apiIn'),
    url(r'^api/out/$', views.apiOut, name='apiOut'),
    url(r'^barcodes/$', views.barcodes, name='barcodes'),
    url(r'^$', views.index, name='index'),
)

