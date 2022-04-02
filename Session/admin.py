from cmath import log
from django.contrib import admin
from .models import Session, Log
# Register your models here.


class LogInline(admin.TabularInline):
    model = Log
    readonly_fields = ('timestamp',)
    ordering = ('timestamp',)
    
class SessionAdmin(admin.ModelAdmin):
    inlines = [
        LogInline,
    ]
    readonly_fields = ('start_time',)

admin.site.register(Session, SessionAdmin)
admin.site.register(Log)
