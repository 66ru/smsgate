import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

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
            return response_json({'status': 2, 'message': 'form is invalid', 'form_errors': form.errors})
    return response_json({})

# TODO: Auth*
def status(request, item_id):
    qi = get_object_or_404(QueueItem, pk=item_id)
    return response_json({'status': qi.status, 'status_message': qi.status_message})