#-*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from smsgate.models import QueueItem

class Command(BaseCommand):
    """
    Берет сообщения из очереди и отправляет.
    """
    help = 'Берет сообщения из очереди и отправляет.'

    def handle(self, *args, **options):
        for qi in QueueItem.objects.filter(status='0'):
            profile = qi.user.get_profile()
            gate = profile.gate

            module = __import__(gate.gate_module)
            print module
