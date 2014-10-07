from django.contrib import admin
from beer.models import DseUser, Product
from django.shortcuts import render
import barcode_generator as bg
from django.utils.html import mark_safe

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
