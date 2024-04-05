from django import forms
from tinymce.widgets import TinyMCE
from .models import EmailTemplate


# CSV file kiválasztása az ügyfelek importjához
class CSVFileSelectForm(forms.Form):
    file = forms.FileField(label='Válassz ki egy új CSV fájlt',
                           widget=forms.ClearableFileInput(attrs={'accept': '.csv'}),
                           required=True)

    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            # # Max méret 5MB
            # if file.size > 5 * 1024 * 1024:
            #     raise forms.ValidationError('The file is too large (max. 5MB)')

            # Ellenőrizze, hogy a fájl CSV formátumban van-e
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('A kiválasztott file nem CSV formátum!')
        return file


class EmailTemplateForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(), label=False)

    class Meta:
        model = EmailTemplate
        fields = ['subject', 'content']
        labels = {'subject': ''}

    def __init__(self, *args, **kwargs):
        super(EmailTemplateForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs['class'] = 'form-control'
        # self.fields['subject'].widget.attrs['readonly'] = True
        self.fields['subject'].widget.attrs['style'] = 'width: 100%;'
