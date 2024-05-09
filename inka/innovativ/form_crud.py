from django import forms
from .models import Product, ProductGroup


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['group', 'name', 'unit', 'price', 'comment']
        labels = {'group': 'Termék csoport név', 'name': 'Termék név', 'unit': 'Mértékegység',
                  'price': 'Egységár', 'comment': 'Megjegyzés'}

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['group'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['unit'].widget.attrs['class'] = 'form-control'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['comment'].widget.attrs['class'] = 'form-control'
        self.fields['comment'].widget.attrs['rows'] = 3


class ProductGroupForm(forms.ModelForm):
    class Meta:
        model = ProductGroup
        fields = ['group_name',]
        labels = {'group_name': 'Termék csoport név'}

    def __init__(self, *args, **kwargs):
        super(ProductGroupForm, self).__init__(*args, **kwargs)
        self.fields['group_name'].widget.attrs['class'] = 'form-control'


# class PriceOfferItemForm(forms.Form):
#     amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Mennyiség')
#     price = forms.DecimalField(max_digits=10, decimal_places=2, label='Egységár')
#     comment = forms.CharField(required=False, label='Megjegyzés')
#
#     def __init__(self, *args, **kwargs):
#         super(PriceOfferItemForm, self).__init__(*args, **kwargs)


# class PriceOfferItemForm(forms.ModelForm):
#     class Meta:
#         model = PriceOfferItem
#         fields = ['product', 'amount', 'price', 'comment']
#
#     def __init__(self, *args, **kwargs):
#         super(PriceOfferItemForm, self).__init__(*args, **kwargs)
#         self.fields['product'].widget.attrs['class'] = 'form-control'
#         self.fields['amount'].widget.attrs['class'] = 'form-control'
#         self.fields['price'].widget.attrs['class'] = 'form-control'
#         self.fields['comment'].widget.attrs['class'] = 'form-control'
