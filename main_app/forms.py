from django import forms
from .models import DocumentTex

class DocumentForm(forms.ModelForm):
    class Meta:
        model = DocumentTex
        fields = ('filename', 'file',)
