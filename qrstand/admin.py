from django.contrib import admin
from adminbuttons.django_admin_buttons import ButtonAdmin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from qrstand.models import Stand, Log

class StandAdmin(ButtonAdmin):
    model = Stand
    list_display = ('sid', 'top_scan_count', 'bottom_scan_count',)
    def mapView(self, request):
        return redirect(reverse('qrstand:map'))
    mapView.short_description = 'View map'
    list_buttons = [mapView]
    ordering = ('sid',)
admin.site.register(Stand, StandAdmin)

class LogAdmin(admin.ModelAdmin):
    model = Log
    list_display = ('stand', 'action', 'ip')
    list_filter = ('stand', 'action',)
    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields]
    def has_add_permission(self, request, obj=None):
        return False
admin.site.register(Log, LogAdmin)
