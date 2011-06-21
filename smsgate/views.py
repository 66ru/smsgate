import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from models import Partner, QueueItem
from forms import  SendForm

def response_json(response_dict):
    return HttpResponse(json.dumps(response_dict), mimetype='application/javascript')

def send(request):
    if request.method == 'POST':
        form = SendForm(request.POST)

        if form.is_valid():
            message = form.cleaned_data['message']

            try:
                partner = Partner.objects.get(pk=form.cleaned_data['partner_id'])
            except Partner.DoesNotExist:
                return response_json({'status': 1, 'message': 'no partner with specified id'})

            item = QueueItem(message=message, partner=partner)
            item.save()

            return response_json({'status': 0, 'id': item.id})
        else:
            pass
    return response_json({})