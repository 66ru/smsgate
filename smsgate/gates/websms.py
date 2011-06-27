
SEND_ADDR = 'http://websms.ru/http_in5.asp'

# http_username
# http_password
# from_phone
# format: txt

class GateInterface(object):
    def __init__(self, config):
        self.config = config

    def send(self, queue_item):
        # TODO: собирать сообщения от сервера
        pass
