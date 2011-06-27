#-*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from smsgate.gates.exceptions import InnerFailure, ProviderFailure
from smsgate.models import QueueItem, GateSettings, Partner

class Command(BaseCommand):
    """
    Берет сообщения из очереди и отправляет.
    """
    help = 'Берет сообщения из очереди и отправляет.'

    def __init__(self):
        super(Command, self).__init__()

        self.gate_interfaces = {}

        for gs in GateSettings.objects.all():
            config = gs.get_config_parser()
            module_name = gs.gate_module

            module = __import__(module_name, globals(), locals(), ['GateInterface'], level=0)
            cls = getattr(module, 'GateInterface')
            gi = cls(config)

            self.gate_interfaces[module_name] = gi

        self.partners_gates = {}
        for p in Partner.objects.select_related().filter(gate__isnull=False):
            self.partners_gates[p.id] = self.gate_interfaces[p.gate.gate_module]


    def handle(self, *args, **options):
        for qi in QueueItem.objects.filter(status='0'):
            gate = self.partners_gates[qi.partner_id]
            try:
                gate.send(qi)
                qi.status = '1'
            except InnerFailure:
                qi.status = '2'
            except ProviderFailure:
                qi.status = '3'
            qi.save()
