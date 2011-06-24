import string
import random
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import IPAddressField


def randstring_creator(count):
    def _randstring():
        a = string.ascii_letters + string.digits
        return ''.join([random.choice(a) for _ in xrange(count)])
    return _randstring


class Partner(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='partner')
    token = models.CharField(max_length=20, unique=True,
                             default=randstring_creator(20))

    # messaging properties
    sms_from = models.CharField(max_length=11, blank=True) # TODO: websms = 11. others??
    sms_translit = models.BooleanField()

    def __unicode__(self):
        return '%s (partner)' % self.user.username


class IPRange(models.Model):
    ip_from = IPAddressField()
    ip_to = IPAddressField(blank=True, null=True)
    partner = models.ForeignKey(Partner, related_name='ips_allowed')

    @staticmethod
    def _ipv4_to_int(ip):
        """
        >>> f = IPRange._ipv4_to_int
        >>> f('0.0.0.0')
        0L
        >>> f('255.255.255.255')
        4294967295L
        """
        hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
        return long(hexn, 16)

    def in_range(self, ip_str):
        if self.ip_to:
            return IPRange._ipv4_to_int(self.ip_from) <= IPRange._ipv4_to_int(ip_str) <= IPRange._ipv4_to_int(self.ip_to)
        else:
            return ip_str == self.ip_from


class QueueItem(models.Model):
    phone_n = models.CharField(max_length=15)
    message = models.TextField()
    user = models.ForeignKey(User)
    comment = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = (
        ('0', 'IN PROGRESS'),
        ('1', 'OK'),
        ('2', 'FAILED'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default='0')
    status_message = models.TextField(blank=True)

    class Meta:
        permissions = (('view_queueitem', 'Can view queue items'),)


class SmsLog(models.Model):
    item = models.ForeignKey(QueueItem)
    time = models.DateTimeField(auto_now_add=True)
    text = models.TextField()