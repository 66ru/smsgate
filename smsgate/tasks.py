# -*- coding: utf-8 -*-
from celery.task import Task
from celery.registry import tasks
from smsgate.gates.exceptions import ProviderFailure
from smsgate.models import GateSettings, Partner, STATUS_SENDING, STATUS_OK, STATUS_PROVIDER_FAILURE, STATUS_INNER_FAILURE
from datetime import datetime

class SendSms(Task):
    """
        Отправляет sms сообщения через гейты.
    """
    def __init__(self):
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

    def run(self, queue_item):
        status_message = str(datetime.now())

        queue_item.status = STATUS_SENDING
        queue_item.status_message = status_message
        queue_item.save()

        gate = self.partners_gates[queue_item.partner_id]

        try:
            gate.send(queue_item)
            queue_item.status = STATUS_OK
            queue_item.status_message = ''
        except ProviderFailure as ex:
            queue_item.status = STATUS_PROVIDER_FAILURE
            queue_item.status_message = str(ex).decode('cp1251', 'ignore')
        except Exception as ex:
            queue_item.status = STATUS_INNER_FAILURE
            queue_item.status_message = str(ex).decode('cp1251', 'ignore')
        finally:
            queue_item.save()

tasks.register(SendSms)
