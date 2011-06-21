from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^send/$', 'smsgate.views.send', name='send'),
)