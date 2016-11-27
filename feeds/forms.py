from django import forms

attr = {'class': 'form-control'}

class FPForm(forms.Form):
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs=attr))
