from django.contrib.auth.models import User
from smsgate.models import Partner

class PartnerTokenBackend:
    def authenticate(self, id=None, token=None):
        if id and token:
            try:
                p = Partner.objects.get(pk=id, token=token)
                return p.user
            except Partner.DoesNotExist:
                pass
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
