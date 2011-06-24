import json
from django.http import HttpResponse

from models import QueueItem, SmsLog
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
            phone_n = form.cleaned_data['phone_n']

            item = QueueItem(phone_n=phone_n,
                             message=message,
                             comment=comment,
                             partner=request.user.get_profile())
            item.save()

            SmsLog.objects.create(item=item, text='Added: %s; phone_n: %s; message: %s' %
                                                  (request.user.id, phone_n, message,))

            return response_json({'status': 0, 'id': item.id})
        else:
            return response_json({'status': 1, 'message': 'form is invalid', 'form_errors': form.errors})
    else:
        return HttpResponse(status=405) # method not allowed


@permission_required_or_403('smsgate.view_queueitem')
def status(request, item_id):
    try:
        qi = QueueItem.objects.get(pk=item_id)
        if qi.partner != request.user.get_profile(): # something like object level permissions
            return HttpResponse(status=403)
        return response_json({'status': qi.status, 'status_message': qi.status_message})
    except QueueItem.DoesNotExist:
        return HttpResponse(status=404)