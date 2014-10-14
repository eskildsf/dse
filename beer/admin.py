from django.contrib import admin
from beer.models import DseUser, Product, Purchase, DeviceLog
from django.shortcuts import render
import barcode_generator as bg
from django.utils.html import mark_safe
from django.contrib.admin import SimpleListFilter
from adminbuttons.django_admin_buttons import ButtonAdmin

class DseUserAdmin(admin.ModelAdmin):
    list_display = ('initials', 'name', 'phone_number', 'department', 'status', 'groups')
    list_filter = ('department', 'status',)
    readonly_fields = ('initials', 'name', 'phone_number', 'department', 'status','groups',)
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    actions = ['barcodes']
    def barcodes(self, request, queryset):
        opts = self.model._meta
        app_label = opts.app_label
        selected = [(e.initials(), e.initials()) for e in queryset.all()]
        barcodes = bg.GenerateBarcodes(selected, 200, 300)
        context = {
        'app_label': app_label,
        'opts': opts,
        'title': 'Barcodes',
        'barcodes': mark_safe(barcodes.render()),
        }
        return render(request, 'beer/barcodes.html', context)
admin.site.register(DseUser, DseUserAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'barcode',)
    readonly_fields = ('name', 'price', 'barcode',)
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    actions = ['barcodes']
    def barcodes(self, request, queryset):
        opts = self.model._meta
        app_label = opts.app_label
        selected = [(e.barcode, e.name) for e in queryset.all()]
        barcodes = bg.GenerateBarcodes(selected, 200, 300, 0.4)
        context = {
        'app_label': app_label,
        'opts': opts,
        'title': 'Barcodes',
        'barcodes': mark_safe(barcodes.render()),
        }
        return render(request, 'beer/barcodes.html', context)
admin.site.register(Product, ProductAdmin)

class PurchaseAdmin(admin.ModelAdmin):
    pass
admin.site.register(Purchase, PurchaseAdmin)

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
            return redirect(reverse('admin:beer_devicelog_changelist'))
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
    list_display = ('formatted_message','date','levelname')
    list_filter = (LevelFilter,)
    readonly_fields = []
    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(DeviceLog, DeviceLogAdmin)
