#-*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from smsgate.gates.exceptions import ProviderFailure
from smsgate.models import QueueItem, GateSettings, Partner, STATUS_IN_PROGRESS, STATUS_OK, STATUS_PROVIDER_FAILURE, STATUS_INNER_FAILURE

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
        for qi in QueueItem.objects.filter(status=STATUS_IN_PROGRESS):
            gate = self.partners_gates[qi.partner_id]
            try:
                gate.send(qi)
                qi.status = STATUS_OK
            except ProviderFailure:
                qi.status = STATUS_PROVIDER_FAILURE
            except Exception as ex:
                print ex
                qi.status = STATUS_INNER_FAILURE
            qi.save()
