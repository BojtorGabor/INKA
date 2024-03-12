from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms_members import LoginUserForm, RegisterUserForm, UpdatePasswordForm
from django.contrib.auth.models import User
# from .forms_members import UpdateUserForm, UserProfileForm
# from .models import UserProfile
from django_otp import verify_token, user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import Job
from django.contrib.auth.signals import user_logged_in



def login_user(request):
    if request.method == 'POST':
        form = LoginUserForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            otp_token = form.cleaned_data['otp_token']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user_has_device(user):
                    otp_device = TOTPDevice.objects.get(user=user)
                    verify_device = verify_token(user, otp_device.persistent_id, otp_token)
                    if otp_device == verify_device:
                        position = Job.objects.filter(user=user)
                        if position:
                            login(request, user)
                            messages.success(request, 'Sikeres bejelentkezés.')
                        else:
                            messages.success(request, 'Ehhez a felhasználó névhez még nem tartozik munkakör. '
                                                      'Kérj az adminisztrátortól, e nélkül nem tudsz belépni')
                        return redirect('home')
                    else:
                        messages.error(request, 'Érvénytelen Belépési token!')
                else:
                    messages.success(request, 'Ehhez a felhasználó névhez még nem kértél QR kódot'
                                              ' az adminisztrátortól. E nélkül nem tudsz belépni')
            else:
                messages.success(request, 'Hibás bejelentkezés. Próbáld újra')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = LoginUserForm()
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, 'Kijelentkezve.')
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            messages.success(request, f'Sikeres regisztráció. A {username} felhasználó névhez'
                                      f' tartozó QR kódot kérd az adminisztrátortól.')
            return redirect('home')
        else:
            messages.success(request, 'Hibás regisztráció. Próbáld újra')
            return redirect('register')
    else:
        form = RegisterUserForm()
    return render(request, 'register.html', {'form': form})


def update_password(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            form = UpdatePasswordForm(current_user, request.POST)
            if form.is_valid():
                password = form.cleaned_data['new_password1']
                otp_token = form.cleaned_data['otp_token']
                otp_device = TOTPDevice.objects.get(user=current_user)
                verify_device = verify_token(current_user, otp_device.persistent_id, otp_token)
                if otp_device == verify_device:
                    form.save()
                    login(request, current_user)
                    messages.success(request, 'Sikeres jelszó módosítás.')
                    return redirect('home')
                else:
                    messages.error(request, 'Érvénytelen Belépési token!')
                    return redirect('update-password')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                return redirect('update-password')
        else:
            form = UpdatePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, 'Nincs jogosultságod.')
        return redirect('login')
#
#
# def update_user(request):
#     if request.user.is_authenticated:
#         current_user = User.objects.get(id=request.user.id)
#         form = UpdateUserForm(request.POST or None, instance=current_user)
#         if form.is_valid():
#             form.save()
#             login(request, current_user)
#             messages.success(request, 'Sikeres módosítás.')
#             return redirect('home')
#         else:
#             return render(request, 'update_user.html', {'form': form})
#     else:
#         messages.success(request, 'Nincs jogosultságod.')
#         return redirect('login')

#
#
# def update_user_profile(request):
#     if not request.user.is_authenticated:
#         messages.success(request, 'Nincs jogosultságod.')
#         return redirect('login')
#
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Sikeres módosítás.')
#             return redirect('home')
#     else:
#         form = UserProfileForm(instance=user_profile)
#
#     return render(request, 'update_user_profile.html', {'form': form})
