import json
from django.http import HttpResponse

from models import QueueItem
from forms import  SendForm
from smsgate.auth import permission_required_or_403

def response_json(response_dict):
    return HttpResponse(json.dumps(response_dict), mimetype='application/javascript')

@permission_required_or_403('smsgate.add_queueitem')
def send(request):
    if request.method == 'POST':
        form = SendForm(request.POST)

        if form.is_valid():
            message = form.cleaned_data['message']
            comment = form.cleaned_data['comment']

            item = QueueItem(message=message, user=request.user, comment=comment)
            item.save()

            return response_json({'status': 0, 'id': item.id})
        else:
            return response_json({'status': 2, 'message': 'form is invalid', 'form_errors': form.errors})
    else:
        return HttpResponse(status=405) # method not allowed

@permission_required_or_403('smsgate.view_queueitem')
def status(request, item_id):
    try:
        qi = QueueItem.objects.get(pk=item_id)
        return response_json({'status': qi.status, 'status_message': qi.status_message})
    except QueueItem.DoesNotExist:
        return HttpResponse(status=404)