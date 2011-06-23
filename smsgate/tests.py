#-*- coding: UTF-8 -*-
import json
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.utils import unittest
from django.test.client import Client
from smsgate.auth.backends import PartnerTokenBackend
from smsgate.models import QueueItem
from models import User, Partner

def post_and_get_json(to, args_dict, client=Client()):
    response_obj = client.post(to, args_dict)
    return json.loads(response_obj.content)


class _RestTC(unittest.TestCase):
    def setUp(self):
        partners_group = Group(name='partners')
        partners_group.save()

        qi_ct = ContentType.objects.get(app_label='smsgate', model='queueitem')
        can_add_permission = Permission.objects.get(codename='add_queueitem',
                                                    content_type=qi_ct)
        partners_group.permissions.add(can_add_permission)

        can_view_permission = Permission.objects.get(codename='view_queueitem',
                                                     content_type=qi_ct)
        partners_group.permissions.add(can_view_permission)

        self.partners_group = partners_group

        partner_user = User.objects.create_user('test', 'test', password='test')
        partner_user.groups.add(partners_group)
        self.partner_user = partner_user

        self.other_user = User.objects.create_user('other', 'other', password='other')

        self.partner_client = Client()
        self.partner_client.login(username='test', password='test')

        self.other_client = Client()
        self.other_client.login(username='other', password='other')

    def tearDown(self):
        self.partner_client.logout()
        self.partner_user.delete()
        self.partners_group.delete()
        self.other_user.delete()

class SendTestCase(_RestTC):
    def test_ok(self):
        """
        Полностью валидный вариант.
        """
        message = 'Some message for you man'

        addr = '/sms/send/'
        params = {
            'message': message,
            'phone_n': '79001234567',
        }

        _helper = lambda client: post_and_get_json(addr, params, client=client)

        # пытаемся отправить от партнера с правами
        partner_resp = _helper(self.partner_client)

        self.assertEqual(partner_resp['status'], 0)
        queue_id = partner_resp['id']

        qi = QueueItem.objects.get(pk=queue_id)
        self.assertEqual(message, qi.message)

        # пытаемся отправить от партнера без прав (должно вернуть 403)
        other_resp = self.other_client.post(addr, params)
        self.assertEquals(other_resp.status_code, 403)

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
        }, client=self.partner_client)

        queue_id = resp['id']
        qi = QueueItem.objects.get(pk=queue_id)
        self.assertEqual(qi.comment, comment)

    def test_invalid_form(self):
        resp = post_and_get_json('/sms/send/', {}, client=self.partner_client)
        self.assertEqual(resp['status'], 2)
        self.assertTrue('message' in resp['form_errors'])

    def test_invalid_method(self):
        # GET is not allowed
        resp = self.partner_client.get('/sms/send/')
        self.assertEqual(resp.status_code, 405)


class StatusTestCase(_RestTC):
    def setUp(self):
        super(StatusTestCase, self).setUp()
        
        qi = QueueItem(phone_n='79001234567', message='hello!', 
                       user=self.partner_user)
        qi.save()
        self.qi = qi

    def test_ok_id(self):
        resp = post_and_get_json('/sms/status/%s/' % self.qi.id, {},
                                 client=self.partner_client)
        self.assertEquals(resp['status'], '0')
        self.assertEquals(self.qi.status, '0')

    def test_bad_id(self):
        """
        Если указан неподходящий id, то
        должен вернуться код 404.
        """
        resp = self.partner_client.get('/sms/status/%s/' % 9000)
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
