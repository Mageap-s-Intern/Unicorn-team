from django import forms
from django.core.exceptions import ValidationError


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        filename = self.cleaned_data['file']
        if str(filename)[-4:] != '.xml':
            raise ValidationError('Only .xml file required.')

        return filename
