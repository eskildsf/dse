from django.contrib import admin
from slideshow.models import Show, SlideGroup, Resolution, Device, DeviceLog
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.conf.urls import patterns, url
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.actions import delete_selected
from admin_buttons import ButtonAdmin
import math, datetime

class SlidegroupInline(admin.TabularInline):
    verbose_name = "slide group"
    model = SlideGroup
    extra = 1

class ShowAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [SlidegroupInline]
    def currentlyShownOn(self):
        devices = self.getDevices()
        deviceLinks = []
        for device in devices:
            url = reverse('admin:slideshow_device_change',args=[device.id])
            str = '<a href="%s">%s</a>' % (url, device)
            deviceLinks.append(str)
        return ", ".join(deviceLinks)
    def showOnAllDevices(self):
        url = reverse('admin:setActiveOnAll', args=[self.id])
        return u"<a href='%s'>Show on all devices</a>" % url
    def syncLink(self):
        url = reverse('admin:sync', args=[self.id])
        return u"<a href='%s'>Sync all devices</a>" % url
    currentlyShownOn.short_description = 'Slideshow is currently shown on'
    showOnAllDevices.short_description = ''
    showOnAllDevices.allow_tags = True
    syncLink.short_description = ''
    syncLink.allow_tags = True
    currentlyShownOn.allow_tags = True
    list_display = ('name', currentlyShownOn, showOnAllDevices, syncLink)
    def setActiveOnAll(self, request, showId):
        show = get_object_or_404(Show, pk=showId)
        show.setActiveOnAllDevices()
        return redirect(reverse('admin:slideshow_show_changelist'))
    def sync(self, request, showId):
        show = get_object_or_404(Show, pk=showId)
        show.setSync();
        return redirect(reverse('admin:slideshow_show_changelist'))
    def get_urls(self):
        urls = super(ShowAdmin, self).get_urls()
        newUrls = patterns('',
                           url(
                               r'set_active/(?P<showId>\d+)/$',
                               self.admin_site.admin_view(self.setActiveOnAll),
                               name = 'setActiveOnAll',
                               ),
                            url(
                               r'sync/(?P<showId>\d+)/$',
                               self.admin_site.admin_view(self.sync),
                               name = 'sync',
                               ),
                  )
        return newUrls+urls
admin.site.register(Show, ShowAdmin)

class ResolutionAdmin(admin.ModelAdmin):
    fields = ['x', 'y']
admin.site.register(Resolution, ResolutionAdmin)

class DeviceAdmin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        def if_editing(*args):
            return args if obj else ()
        return [
            (None, {
                 'classes': ('wide',),
                 'fields': ('name', 'active_show', 'resolution') + if_editing('api_key',),}
            ),
        ]
    readonly_fields = ['api_key']
    def activeSlideshow(self):
        url = reverse('admin:slideshow_show_change', args=[self.active_show.id])
        return u'<a href="%s">%s</a>' % (url, self.active_show)
    activeSlideshow.short_description = 'Active slideshow'
    activeSlideshow.allow_tags = True
    def isActive(self):
        return self.is_active
    isActive.boolean = True
    isActive.short_description = 'Active'
    list_display = ('name', activeSlideshow, 'resolution',  isActive)
admin.site.register(Device, DeviceAdmin)

class AgeListFilter(SimpleListFilter):
    title = 'Records from the past'
    parameter_name = 'age'
    def lookups(self, request, model_admin):
        return (
               ('30sec', '30 seconds',),
               ('1min', 'minute',),
               ('5min', '5 minutes',),
               )
    def queryset(self, request, queryset):

        if self.value() == '30sec':
            delta = datetime.datetime.now() - datetime.timedelta(seconds=30)
            return queryset.filter(date__gte = delta)
        elif self.value() == '1min':
            delta = datetime.datetime.now() - datetime.timedelta(seconds=60)
            return queryset.filter(date__gte = delta)
        elif self.value() == '5min':
            delta = datetime.datetime.now() - datetime.timedelta(minutes=5)
            return queryset.filter(date__gte = delta)

class LevelFilter(SimpleListFilter):
    title = 'level'
    parameter_name = 'level'
    def lookups(self, request, model_admin):
        return (
               ('10', 'Debug',),
               ('20', 'Info',),
               ('30', 'Warning',),
               ('40', 'Error',),
               )
    def queryset(self, request, queryset):
        if self.value() in ['10', '20', '30', '40',]:
            return queryset.filter(levelno__gte = self.value())

class DeviceLogAdmin(ButtonAdmin):
    model = DeviceLog
    def clearLogs(self, request):
        # Deletes all log entries
        result = DeviceLog.objects.all()
        action = delete_selected(self, request, result)
        if action is None:
            return redirect(reverse('admin:slideshow_devicelog_changelist'))
        else:
            return action
    clearLogs.short_description = 'Clear logs'
    list_buttons = [clearLogs]
    def timeWithMsPrecision(self):
        timeInSeconds = math.floor(self.created[-5])
        timeInMiliSeconds = math.floor(self.msecs*1000)
        timeAsString = '%s.%s' % (int(timeInSeconds), int(timeInMiliSeconds))
        return timeAsString[0:15]
    timeWithMsPrecision.short_description = 'Time the log was filed'
    list_display = ('device','formatted_message','date',)
    list_filter = ('device', AgeListFilter, LevelFilter,)
    readonly_fields = []
    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(DeviceLog, DeviceLogAdmin)
