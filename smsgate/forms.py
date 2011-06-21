from django import forms

class SendForm(forms.Form):
    phone_n = forms.CharField(max_length=15)
    partner_id = forms.IntegerField()
    message = forms.CharField(max_length=140)
    comment = forms.CharField(required=False)
