from django.db import models


class QueueItem(models.Model):
    phone_n = models.CharField(max_length=15)
    
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = (
        ('0', 'IN PROGRESS'),
        ('1', 'OK'),
        ('2', 'FAILED'),
    )
    status = models.CharField(max_length=1)
    status_message = models.TextField(blank=True)