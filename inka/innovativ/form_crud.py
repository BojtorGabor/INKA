from django import forms
from .models import Product, ProductGroup, PriceOffer


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


class PriceOfferItemAmountForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Mennyiség')

    def __init__(self, *args, **kwargs):
        super(PriceOfferItemAmountForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['class'] = 'form-control'


class PriceOfferItemPriceForm(forms.Form):
    price = forms.DecimalField(max_digits=10, decimal_places=2, label='Egységár')

    def __init__(self, *args, **kwargs):
        super(PriceOfferItemPriceForm, self).__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['class'] = 'form-control'


class PriceOfferCommentForm(forms.ModelForm):
    class Meta:
        model = PriceOffer
        fields = ['comment',]
        labels = {'comment': 'Megjegyzés'}
        widgets = {'comment': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super(PriceOfferCommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs['class'] = 'form-control'
