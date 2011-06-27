#-*- coding: UTF-8 -*-
import ConfigParser
from _functools import partial
import io
import urllib
import urllib2
from smsgate.gates.exceptions import ProviderFailure
from smsgate.models import SmsLog

SEND_ADDR = 'http://websms.ru/http_in5.asp'

# http_username
# http_password
# from_phone
# format: txt

class GateInterface(object):
    def __init__(self, config):
        conf_get = partial(config.get, 'Provider')

        self.http_username = conf_get('http_username')
        self.http_password = conf_get('http_password')


    def send(self, queue_item, **params):
        d = {
            'http_username': self.http_username,
            'http_password': self.http_password,

            'message': queue_item.message.encode('cp1251'),
            'phone_list': queue_item.phone_n,
            'packet_id': queue_item.id,
        }

        from_phone = queue_item.partner.sms_from
        if from_phone:
            d['fromPhone'] = from_phone

        d.update(params)
        params = urllib.urlencode(d)

        resp = urllib2.urlopen('%s?%s' % (SEND_ADDR, params,))
        resp_cp = ConfigParser.RawConfigParser()
        resp_cp.readfp(resp)
        
        status = resp_cp.get('Common', 'error_num')
        if status == 'OK':
            SmsLog.objects.create(item=queue_item, text=u'Sent OK')
            return True
        else:
            errortext = 'Error sending: %s' % status
            SmsLog.objects.create(item=queue_item, text=errortext.decode('cp1251'))
            raise ProviderFailure(errortext)
