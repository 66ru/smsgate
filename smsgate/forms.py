from django import forms

class SendForm(forms.Form):
    partner_id = forms.IntegerField()
    message = forms.CharField(max_length=140)
