from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^send/$', 'sms.smsgate.views.send'),
    url(r'^status/(?P<item_id>\d+)/$', 'sms.smsgate.views.status'),
)
