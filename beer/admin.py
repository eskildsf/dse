from django.contrib import admin
from beer.models import DseUser
class DseUserAdmin(admin.ModelAdmin):
    list_display = ('initials', 'name', 'phone_number', 'department', 'status', 'groups')
    list_filter = ('department', 'status',)
    readonly_fields = ('initials', 'name', 'phone_number', 'department', 'status','groups',)
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
admin.site.register(DseUser, DseUserAdmin)
