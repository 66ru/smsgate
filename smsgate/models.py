import string
import random
from django.db import models
from django.contrib.auth.models import User


def randstring_creator(count):
    def _randstring():
        a = string.ascii_letters + string.digits
        return ''.join([random.choice(a) for _ in xrange(count)])
    return _randstring


class Partner(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='partner')
    code = models.CharField(max_length=20, unique=True,
                            default=randstring_creator(20))


class QueueItem(models.Model):
    phone_n = models.CharField(max_length=15)
    message = models.CharField(max_length=140)
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
