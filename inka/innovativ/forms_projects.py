from django import forms
from django.core.exceptions import ObjectDoesNotExist
from tinymce.widgets import TinyMCE
from .models import EmailTemplate, Customer


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


class CustomerHandInputForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['surname', 'name', 'email','phone', 'address', 'surface',]
        labels = {'surname': 'Vezetéknév', 'name': 'Keresztnév', 'email': 'Email', 'phone': 'Telefon',
                  'address': 'Cím', 'surface': 'Felület',}

    def __init__(self, *args, **kwargs):
        super(CustomerHandInputForm, self).__init__(*args, **kwargs)
        self.fields['surname'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['phone'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['surface'].widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            Customer.objects.get(email=email)
            raise forms.ValidationError("Ez az email cím már létezik az adatbázisban!")
        except ObjectDoesNotExist:
            return email


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['surname', 'name', 'email','phone', 'address', 'surface', 'installation_address']
        labels = {'surname': 'Vezetéknév', 'name': 'Keresztnév', 'email': 'Email', 'phone': 'Telefon',
                  'address': 'Cím', 'surface': 'Felület', 'installation_address': 'Telepítési cím'}

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['surname'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['phone'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['surface'].widget.attrs['class'] = 'form-control'
        self.fields['installation_address'].widget.attrs['class'] = 'form-control'


class CustomerDelete(forms.Form):
    reason = forms.CharField(label='Indoklás', max_length=150, required=True)

    def __init__(self, *args, **kwargs):
        super(CustomerDelete, self).__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs['class'] = 'form-control'