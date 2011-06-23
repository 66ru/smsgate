from django.contrib.auth import authenticate


class PartnerPostTokenMiddleware(object):
    def process_request(self, request):
        if request.method != 'POST' or 'id' not in request.POST or 'token' not in request.POST:
            return
        else:
            id = int(request.POST['id'])
            token = request.POST['token']
            user = authenticate(id=id, token=token)
            if user:
                request.user = user