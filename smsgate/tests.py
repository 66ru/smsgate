#-*- coding: UTF-8 -*-
import json
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from django.utils import unittest
from django.test.client import Client
from smsgate.auth.backends import PartnerTokenBackend
from smsgate.models import QueueItem, IPRange, SmsLog
from models import User, Partner


class IPRangesTest(unittest.TestCase):
    def test_all_the_range(self):
        ipr1 = IPRange(ip_from='0.0.0.0', ip_to='255.255.255.255')
        self.assertTrue(ipr1.in_range('127.0.0.1'))

    def test_127_to_end(self):
        ipr1 = IPRange(ip_from='127.0.0.0', ip_to='255.255.255.255')
        self.assertTrue(ipr1.in_range('127.0.0.1'))

    def test_100_to_end(self):
        ipr1 = IPRange(ip_from='100.1.1.1', ip_to='255.255.255.255')
        self.assertTrue(ipr1.in_range('127.0.0.1'))

    def test_exact_ip(self):
        ipr1 = IPRange(ip_from='127.0.0.1')
        self.assertTrue(ipr1.in_range('127.0.0.1'))
        self.assertFalse(ipr1.in_range('127.0.0.0'))
        self.assertFalse(ipr1.in_range('127.0.0.2'))
        self.assertFalse(ipr1.in_range('255.255.255.255'))


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

        partner = Partner(token='partner_token', user=partner_user)
        partner.save()
        self.partner = partner

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
        SmsLog.objects.all().delete()


class SendTestCase(_RestTC):
    def test_ok(self):
        """
        Полностью валидный вариант.
        """
        message = 'Some message for you man'

        addr = '/sms/send/'
        phone_n = '79001234567'
        params = {
            'message': message,
            'phone_n': phone_n,
            }

        _helper = lambda client: post_and_get_json(addr, params, client=client)

        # пытаемся отправить от партнера с правами
        partner_resp = _helper(self.partner_client)

        self.assertEqual(partner_resp['status'], 0)
        queue_id = partner_resp['id']

        qi = QueueItem.objects.get(pk=queue_id)
        self.assertEqual(message, qi.message)
        self.assertEqual(phone_n, qi.phone_n)

        # log appended:
        self.assertTrue(SmsLog.objects.filter(item=qi).exists())

        # пытаемся отправить от партнера без прав (должно вернуть 403)
        other_resp = self.other_client.post(addr, params)
        self.assertEquals(other_resp.status_code, 403)

        # пытаемся отправить от анонимуса
        annon_client = Client()
        annon_resp = annon_client.post(addr, params)
        self.assertEqual(annon_resp.status_code, 403)

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
        self.assertEqual(resp['status'], 1)
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
        addr = '/sms/status/%s/' % self.qi.id
        params = {}
        resp = post_and_get_json(addr, params,
                                 client=self.partner_client)
        self.assertEquals(resp['status'], '0')
        self.assertEquals(self.qi.status, '0')

        resp_to_other = self.other_client.post(addr, params)
        self.assertEquals(resp_to_other.status_code, 403)

    def test_bad_id(self):
        """
        Если указан неподходящий id, то
        должен вернуться код 404.
        """
        resp = self.partner_client.post('/sms/status/%s/' % 9000)
        self.assertEqual(resp.status_code, 404)


class TokenAuthTestCase(_RestTC):
    def _assert_status_check(self, status_code, partner_id=None, token=None):
        c = Client()
        # good token
        resp = c.post('/sms/status/9000/', {
            'id': partner_id or self.partner.id,
            'token': token or self.partner.token,
            })
        self.assertEqual(resp.status_code, status_code)

    def setUp(self):
        super(TokenAuthTestCase, self).setUp()
        self.backend = PartnerTokenBackend()

    def test_backend_authenticate(self):
        u = self.backend.authenticate(id=self.partner_user.id,
                                      token=self.partner.token)
        self.assertEqual(u, self.partner_user)

    def test_full_cycle_authnticate(self):
        # good token
        self._assert_status_check(404)

        # bad token
        self._assert_status_check(403, token='bad_token')


class IPTests(TokenAuthTestCase):
    def setUp(self):
        super(IPTests, self).setUp()
        self.ipr = None

    def tearDown(self):
        super(IPTests, self).tearDown()
        if self.ipr is not None:
            self.ipr.delete()

    def test_ip_only_one_allowed_ok(self):
        self.ipr = IPRange.objects.create(ip_from='127.0.0.1', partner=self.partner)
        self.ipr.save()

        self.test_full_cycle_authnticate()

    def test_ip_only_one_allowed_other(self):
        self.ipr = IPRange.objects.create(ip_from='127.0.0.0', partner=self.partner)
        self.ipr.save()

        self._assert_status_check(403)

    def test_ip_range_allowed_ok(self):
        self.ipr = IPRange.objects.create(ip_from='127.0.0.1', ip_to='255.255.0.0', partner=self.partner)
        self.ipr.save()

        self.test_full_cycle_authnticate()

    def test_ip_range_allowed_other(self):
        self.ipr = IPRange.objects.create(ip_from='127.0.0.2', ip_to='255.255.0.0', partner=self.partner)
        self.ipr.save()
        self._assert_status_check(403)