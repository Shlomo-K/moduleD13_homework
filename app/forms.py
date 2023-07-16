from django.forms import ModelForm
from django import forms
from .models import Notice, Files


class InputForm(forms.Form):
    login = forms.CharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput())


class NoticeForm(ModelForm):
    class Meta:
        model = Notice
        fields = ['Notice_title', 'Notice_text']


class VideoFormEdit(ModelForm):
    class Meta:
        model = Files
        fields = ['File']
