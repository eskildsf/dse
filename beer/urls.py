from django.conf.urls import patterns, url, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from beer import views

urlpatterns = patterns('',
    url(r'^api/lcd/$', views.lcdAPI, name='lcdAPI'),
    url(r'^barcodes/$', views.barcodes, name='barcodes'),
    url(r'^lcd/$', views.lcd, name='lcd'),
    url(r'^api/products/$', views.products, name='products'),
    url(r'^api/customers/$', views.customers, name='customers'),
    url(r'^api/accounts/$', views.accounts, name='accounts'),
    url(r'^api/purchase/create/$', views.makePurchase, name='makePurchase'),
    url(r'^api/purchase/delete/$', views.removePurchase, name='removePurchase'),
    url(r'^api/purchase/latest/(?P<initials>\w{3})/$', views.latestPurchase, name='latestPurchase'),
    url(r'^api/log/$', views.deviceLog, name='logAPI'),
    url(r'^log/$', views.log, name='log'),
)

