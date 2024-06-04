from django import forms
from django.core.exceptions import ObjectDoesNotExist
from tinymce.widgets import TinyMCE
from .models import EmailTemplate, Customer, CustomerProject, Target, Financing, Task, Specify


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
        fields = ['surname', 'name', 'email','phone', 'address', 'surface']
        labels = {'surname': 'Vezetéknév', 'name': 'Keresztnév', 'email': 'Email', 'phone': 'Telefon',
                  'address': 'Cím', 'surface': 'Felület'}

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
    installation_address = forms.CharField(max_length=150, required=True,
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    request = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 3, 'maxlength': 1000, 'class': 'form-control'}), max_length=1000, required=True)
    target = forms.ModelChoiceField(queryset=Target.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Válassz egy projektet --")
    financing = forms.ModelChoiceField(queryset=Financing.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Válassz egy finanszírozást --")

    class Meta:
        model = Customer
        fields = ['surname', 'name', 'email','phone', 'address', 'surface']
        labels = {'surname': 'Vezetéknév', 'name': 'Keresztnév', 'email': 'Email', 'phone': 'Telefon',
                  'address': 'Cím', 'surface': 'Felület'}

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['surname'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['phone'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['surface'].widget.attrs['class'] = 'form-control'


class CustomerProjectForm(forms.ModelForm):
    class Meta:
        model = CustomerProject
        fields = ['target', 'financing', 'installation_address', 'request']
        labels = {'target': 'Ügyfél project', 'financing': 'Finanszírozás', 'installation_address': 'Telepítés címe',
                  'request': 'Kérés, igény'}

    def __init__(self, *args, **kwargs):
        super(CustomerProjectForm, self).__init__(*args, **kwargs)
        self.fields['target'].widget.attrs['class'] = 'form-control'
        self.fields['financing'].widget.attrs['class'] = 'form-control'
        self.fields['installation_address'].widget.attrs['class'] = 'form-control'
        self.fields['request'].widget.attrs['class'] = 'form-control'
        self.fields['request'].widget.attrs['rows'] = 3


class ReasonForm(forms.Form):
    reason = forms.CharField(label='Üzenet', max_length=1000, required=True, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, **kwargs):
        super(ReasonForm, self).__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs['class'] = 'form-control'


class DeadlineForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['deadline']
        labels = {'deadline': 'Határidő'}
        widgets = {'deadline': forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'},
                                                       format='%Y-%m-%d')}


    def __init__(self, *args, **kwargs):
        super(DeadlineForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs['class'] = 'form-control'
        if self.instance and self.instance.pk and self.instance.deadline:
            self.fields['deadline'].initial = self.instance.deadline.strftime('%Y-%m-%d')


class SpecifyDateTimeForm(forms.ModelForm):
    class Meta:
        model = Specify
        fields = ['specify_date']
        labels = {'specify_date': 'Időpont'}
        widgets = {'specify_date': forms.widgets.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M')}

    def __init__(self, *args, **kwargs):
        super(SpecifyDateTimeForm, self).__init__(*args, **kwargs)
        self.fields['specify_date'].widget.attrs['class'] = 'form-control'
        if self.instance and self.instance.pk and self.instance.specify_date:
            self.fields['specify_date'].initial = self.instance.specify_date.strftime('%Y-%m-%dT%H:%M')


class DateInputForm(forms.Form):
    dateinput = forms.DateField(label='Időpont', widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'))

    def __init__(self, *args, **kwargs):
        super(DateInputForm, self).__init__(*args, **kwargs)
        self.fields['dateinput'].widget.attrs['class'] = 'form-control'
        if 'initial' in kwargs and 'dateinput' in kwargs['initial']:
            self.fields['dateinput'].initial = kwargs['initial']['dateinput'].strftime('%Y-%m-%d')