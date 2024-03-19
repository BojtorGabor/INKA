from django import forms
from django.conf import settings


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
