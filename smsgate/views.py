import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from models import QueueItem
from forms import  SendForm

def response_json(response_dict):
    return HttpResponse(json.dumps(response_dict), mimetype='application/javascript')

@login_required
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

@login_required
def status(request, item_id):
    try:
        qi = QueueItem.objects.get(pk=item_id)
        return response_json({'status': qi.status, 'status_message': qi.status_message})
    except QueueItem.DoesNotExist:
        return HttpResponse(status=404)