#-*- coding: UTF-8 -*-
import json

from django.utils import unittest
from django.test.client import Client
from smsgate.auth.backends import PartnerTokenBackend
from smsgate.models import QueueItem
from models import User, Partner

def post_and_get_json(to, args_dict, client=Client()):
    str_response = client.post(to, args_dict)
    return json.loads(str_response.content)


class SendTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test', password='test')

        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_ok(self):
        """
        Полностью валидный вариант.
        """
        message = 'Some message for you man'

        resp = post_and_get_json('/sms/send/', {
            'message': message,
            'phone_n': '79001234567',
        }, client=self.client)

        # проверяем статус...
        self.assertEqual(resp['status'], 0)
        queue_id = resp['id']

        qi = QueueItem.objects.get(pk=queue_id)
        self.assertEqual(message, qi.message)

    def test_comment(self):
        """
        Комментарий не обязателен,
        но по желанию должен вставляться.
        """
        comment = 'A few words...'
        resp = post_and_get_json('/sms/send/', {
            'message': 'msg',
            'phone_n': '79001234567',
            'comment': comment
        }, client=self.client)

        queue_id = resp['id']
        qi = QueueItem.objects.get(pk=queue_id)
        self.assertEqual(qi.comment, comment)

    def test_invalid_form(self):
        resp = post_and_get_json('/sms/send/', {}, client=self.client)
        self.assertEqual(resp['status'], 2)
        self.assertTrue('message' in resp['form_errors'])

    def test_invalid_method(self):
        # GET is not allowed
        resp = self.client.get('/sms/send/')
        self.assertEqual(resp.status_code, 405)


class StatusTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test', password='test')
        
        qi = QueueItem(phone_n='79001234567', message='hello!', user=self.user)
        qi.save()
        self.qi = qi

        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        self.user.delete()
        self.qi.delete()
        self.client.logout()

    def test_ok_id(self):
        resp = post_and_get_json('/sms/status/%s/' % self.qi.id, {}, client=self.client)
        self.assertEquals(resp['status'], '0')
        self.assertEquals(self.qi.status, '0')

    def test_bad_id(self):
        """
        Если указан неподходящий id, то
        должен вернуться код 404.
        """
        resp = self.client.get('/sms/status/%s/' % 9000)
        self.assertEqual(resp.status_code, 404)


class TokenAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test', password='test')

        self.token = 'test'
        self.partner = Partner(user=self.user, token=self.token)
        self.partner.save()

    def tearDown(self):
        self.user.delete()
        self.partner.delete()

    def test_backend_authenticate(self):
        backend = PartnerTokenBackend()
        u = backend.authenticate(id=self.user.id, token=self.token)
        self.assertEqual(u, self.user)

    def test_auth(self):
        client = Client()
        resp = post_and_get_json('/sms/send/', {
            'token': self.token,
            'id': self.user.id,
            'message': 'msg',
            'phone_n': '79001234567',
        }, client=client)
        self.assertEqual(resp['status'], 0)
