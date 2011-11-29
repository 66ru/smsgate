from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^send/$', 'smsgate.views.send'),
    url(r'^status/(?P<item_id>\d+)/$', 'smsgate.views.status'),
)
