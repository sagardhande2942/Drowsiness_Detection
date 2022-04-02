from django.contrib import admin
from .models import Driver
from Session.models import Session, Log
# Register your models here.


class SessionInline(admin.TabularInline):
    model = Session
    readonly_fields = ('start_time', 'end_time')
    fields = ['start_time', 'end_time', 'hours']
    ordering = ('start_time', 'end_time',)

class DriverAdmin(admin.ModelAdmin):
    inlines = [
        SessionInline,
    ]


admin.site.register(Driver, DriverAdmin)