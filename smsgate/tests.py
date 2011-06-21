#-*- coding: UTF-8 -*-
import json

from django.utils import unittest
from django.test.client import Client
from smsgate.models import Partner, QueueItem

class SendTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        p = Partner(name='test partner')
        p.save()

        self.partner_id = p.id


    def get_json(self, to, args_dict):
        str_response = self.client.post(to, args_dict)
        return json.loads(str_response.content)


    def test_ok(self):
        """
        Полностью валидный вариант.
        """
        message = 'Some message for you man'

        resp = self.get_json('/sms/send/', {
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
        Невалидный ид партнера должен вызывать статус 1.
        """
        resp = self.get_json('/sms/send/', {
            'partner_id': 9000,
            'message': 'msg',
            'phone_n': '79001234567',
        })
        self.assertEqual(resp['status'], 1)


    def test_invalid_form(self):
        resp = self.get_json('/sms/send/', {})
        self.assertEqual(resp['status'], 2)
        self.assertTrue('message' in resp['form_errors'])
        