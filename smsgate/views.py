import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from models import Partner, QueueItem
from forms import  SendForm

def response_json(response_dict):
    return HttpResponse(json.dumps(response_dict), mimetype='application/javascript')

# TODO: Auth*

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
    else:
        return HttpResponse(status=405) # method not allowed

def status(request, item_id):
    try:
        qi = QueueItem.objects.get(pk=item_id)
        return response_json({'status': qi.status, 'status_message': qi.status_message})
    except QueueItem.DoesNotExist:
        return HttpResponse(status=404)