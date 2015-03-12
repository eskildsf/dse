from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', lambda x: HttpResponseRedirect(reverse('admin:index'))),
    url(r'^slideshow/', include('slideshow.urls', namespace='slideshow')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^files-widget/', include('topnotchdev.files_widget.urls')),
    url(r'^jobbank/', include('jobbank.urls', namespace='jobbank')),
    url(r'^questionnaire/', include('questionnaire.urls', namespace='questionnaire')),
    url(r'^beer/', include('beer.urls', namespace='beer')),
    url(r'^qrstand/', include('qrstand.urls', namespace='qrstand')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
