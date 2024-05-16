from django import forms
from .models import Product, ProductGroup, PriceOffer, PriceOfferItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['group', 'name', 'unit', 'price', 'comment', 'output_power']
        labels = {'group': 'Termék csoport név', 'name': 'Termék név', 'unit': 'Mértékegység',
                  'price': 'Egységár', 'comment': 'Megjegyzés', 'output_power': 'Kimeneti teljesítmény (kW)'}

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['group'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['unit'].widget.attrs['class'] = 'form-control'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['comment'].widget.attrs['class'] = 'form-control'
        self.fields['comment'].widget.attrs['rows'] = 3
        self.fields['output_power'].widget.attrs['class'] = 'form-control'


class ProductGroupForm(forms.ModelForm):
    class Meta:
        model = ProductGroup
        fields = ['group_name',]
        labels = {'group_name': 'Termék csoport név'}

    def __init__(self, *args, **kwargs):
        super(ProductGroupForm, self).__init__(*args, **kwargs)
        self.fields['group_name'].widget.attrs['class'] = 'form-control'


class PriceOfferItemAmountForm(forms.ModelForm):
    class Meta:
        model = PriceOfferItem
        fields = ['amount',]
        labels = {'amount': 'Mennyiség'}

    def __init__(self, *args, **kwargs):
        super(PriceOfferItemAmountForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['class'] = 'form-control'


class PriceOfferItemPriceForm(forms.ModelForm):
    class Meta:
        model = PriceOfferItem
        fields = ['price']
        labels = {'price': 'Egységár'}

    def __init__(self, *args, **kwargs):
        currency = kwargs.pop('currency', None)
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




class PriceOfferChangeForm(forms.ModelForm):
    class Meta:
        model = PriceOffer
        fields = ['change_rating',]
        labels = {'change_rating': '1 valuta egység'}

    def __init__(self, *args, **kwargs):
        super(PriceOfferChangeForm, self).__init__(*args, **kwargs)
        self.fields['change_rating'].widget.attrs['class'] = 'form-control'
