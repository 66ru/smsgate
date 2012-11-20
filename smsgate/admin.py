from smsgate.models import *
from django.contrib import admin


class IPRangeInline(admin.TabularInline):
    model = IPRange


class PartnerAdmin(admin.ModelAdmin):
    inlines = [
        IPRangeInline,
    ]


class QueueItemAdmin(admin.ModelAdmin):
    list_display = ('phone_n', 'created', 'changed', 'status', 'status_message')
    list_filter = ('created', 'changed', 'status')


admin.site.register(QueueItem, QueueItemAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(GateSettings)
