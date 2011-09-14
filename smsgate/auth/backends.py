from django.contrib.auth.models import User
from sms.smsgate.models import Partner

class PartnerTokenBackend:
    supports_anonymous_user = False
    supports_object_permissions = False
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
