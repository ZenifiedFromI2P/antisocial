from django import forms

attr = {'class': 'form-control'}
imgattr = {'class': 'form-control btn btn-round btn-primary'}

class PostForm(forms.Form):
    name = forms.CharField(label='Your name', initial='anonymous', widget=forms.TextInput(attrs=attr))
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs=attr))
    image = forms.FileField(label='Images', widget=forms.ClearableFileInput(attrs=imgattr), required=False)
