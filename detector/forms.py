from django import forms

class EmailForm(forms.Form):
    sender = forms.CharField(max_length=255, required=True)
    subject = forms.CharField(max_length=512, required=False)
    body = forms.CharField(widget=forms.Textarea, required=False)
