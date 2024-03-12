from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms


class LoginUserForm(AuthenticationForm):
    otp_token = forms.CharField(max_length=6, label='Belépési token')

    class Meta:
        model = User
        fields = ('username', 'password', 'otp_token')

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['otp_token'].widget.attrs['class'] = 'form-control'


class RegisterUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class UpdatePasswordForm(SetPasswordForm):
    otp_token = forms.CharField(max_length=6, label='Belépési token')

    class Meta:
        model = User
        fields = ['new_password1', 'new_password2', 'otp_token']

    def __init__(self, *args, **kwargs):
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['otp_token'].widget.attrs['class'] = 'form-control'

#
#
# class UpdateUserForm(UserChangeForm):
#     # Hide password
#     password = None
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
# #    first_name = forms.CharField(max_length=50, widget= forms.TextInput(attrs={'class': 'form-control'}))
# #    last_name = forms.CharField(max_length=50, widget= forms.TextInput(attrs={'class': 'form-control'}))
#
#     class Meta:
#         model = User
#         fields = ('username', 'email')
#
#     def __init__(self, *args, **kwargs):
#         super(UpdateUserForm, self).__init__(*args, **kwargs)
#
#         self.fields['username'].widget.attrs['class'] = 'form-control'

#
#
# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['address']
#
#     def __init__(self, *args, **kwargs):
#         super(UserProfileForm, self).__init__(*args, **kwargs)
#
#         self.fields['address'].widget.attrs['class'] = 'form-control'
