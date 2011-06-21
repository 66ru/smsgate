#-*- coding: UTF-8 -*-
import json

from django.utils import unittest
from django.test.client import Client
from smsgate.models import Partner, QueueItem

client = Client()


def get_json(to, args_dict={}):
    str_response = client.post(to, args_dict)
    return json.loads(str_response.content)


class SendTestCase(unittest.TestCase):
    def setUp(self):
        p = Partner(name='test partner')
        p.save()

        self.partner_id = p.id

    def test_ok(self):
        """
        Полностью валидный вариант.
        """
        message = 'Some message for you man'

        resp = get_json('/sms/send/', {
            'partner_id': self.partner_id,
            'message': message,
            'phone_n': '79001234567',
        })

        # проверяем статус...
        self.assertEqual(resp['status'], 0)
        queue_id = resp['id']
        qi = QueueItem.objects.get(pk=queue_id)

        self.assertEqual(self.partner_id, qi.partner_id)
        self.assertEqual(message, qi.message)

    def test_bad_partner(self):
        """
        Невалидный ид партнера должен
        вызывать статус 1.
        """
        resp = get_json('/sms/send/', {
            'partner_id': 9000,
            'message': 'msg',
            'phone_n': '79001234567',
        })
        self.assertEqual(resp['status'], 1)

    def test_invalid_form(self):
        resp = get_json('/sms/send/', {})
        self.assertEqual(resp['status'], 2)
        self.assertTrue('message' in resp['form_errors'])


class StatusTestCase(unittest.TestCase):
    def setUp(self):
        p = Partner(name='test partner')
        p.save()

        qi = QueueItem(phone_n='79001234567', message='hello!', partner=p)
        qi.save()

        self.qi = qi

    def test_ok_id(self):
        resp = get_json('/sms/status/%s/' % self.qi.id)
        self.assertEquals(resp['status'], '0')
        self.assertEquals(self.qi.status, '0')

    def test_bad_id(self):
        """
        Если указан неподходящий id, то
        должен вернуться код 404.
        """
        resp = client.get('/sms/status/%s/' % 9000)
        self.assertEqual(resp.status_code, 404).
