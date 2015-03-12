from django.contrib import admin
from qrstand.models import Stand, Log

class StandAdmin(admin.ModelAdmin):
    model = Stand
    list_display = ('sid', 'top_scan_count', 'bottom_scan_count',)
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
