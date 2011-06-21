from django.db import models


class Partner(models.Model):
    name = models.CharField(max_length=20)


class QueueItem(models.Model):
    phone_n = models.CharField(max_length=15)
    message = models.CharField(max_length=140)
    partner = models.ForeignKey(Partner)
    comment = models.TextField(blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = (
        ('0', 'IN PROGRESS'),
        ('1', 'OK'),
        ('2', 'FAILED'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
    status_message = models.TextField(blank=True)