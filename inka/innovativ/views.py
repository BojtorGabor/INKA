from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone


def home(request):
    # Aktuális év
    now = timezone.now()
    current_year = now.year

    return render(request, 'home.html', {'current_year': current_year, })