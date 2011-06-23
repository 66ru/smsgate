from django.contrib.auth import authenticate
from smsgate.auth import ip_in_range


class PartnerPostTokenMiddleware(object):
    def process_request(self, request):
        def _post_missing(*args):
            return any([arg not in request.POST
                        for arg in args])

        if request.method != 'POST' or \
           _post_missing('id', 'token'):
            return
        else:
            id = int(request.POST['id'])
            token = request.POST['token']
            user = authenticate(id=id, token=token)
            if not user:
                return

            partner = user.get_profile()
            ip_ranges = partner.ips_allowed.get_query_set()
            if not ip_ranges:
                request.user = user
                return

            for ipr in ip_ranges:
                if ip_in_range(request.META['REMOTE_ADDR'],
                               ipr.ip_from,
                               ipr.ip_to):
                    request.user = user
                    return
