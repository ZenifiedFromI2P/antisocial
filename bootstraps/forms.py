from django import forms

attr = {'class': 'form-control'}

class GroupSeedForm(forms.Form):
    seed = forms.CharField(label='Seed', max_length=1337, initial='none', widget=forms.TextInput(attrs=attr))

class UserSeedForm(forms.Form):
    pseudonym = forms.CharField(label='Pseudonym', min_length=3, widget=forms.TextInput(attrs=attr))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs=attr))
