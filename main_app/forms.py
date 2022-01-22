from django import forms
from .models import DocumentTex

# class UploadFileForm(forms.Form):
#     title = forms.CharField(max_length=50)
#     file = forms.FileField()


class DocumentForm(forms.ModelForm):
    class Meta:
        model = DocumentTex
        fields = ('name', 'upload',)
