from django import forms
from .models import ProductGroup


class ProductGroupForm(forms.ModelForm):
    class Meta:
        model = ProductGroup
        fields = ['group_name',]
        labels = {'group_name': 'Termék csoport név'}

    def __init__(self, *args, **kwargs):
        super(ProductGroupForm, self).__init__(*args, **kwargs)
        self.fields['group_name'].widget.attrs['class'] = 'form-control'
