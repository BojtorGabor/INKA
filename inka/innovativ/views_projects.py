from django.shortcuts import render
from django.contrib import messages


def egyes_szamu_projekt(request):
    cont = 'Hurrá'
    return render(request, 'project_proba.html', {'cont': cont})


def kettes_szamu_projekt(request):
    cont = 'Hurrá, hurrá'
    return render(request, 'project_proba.html', {'cont': cont})


def harmas_szamu_projekt(request):
    cont = 'Hurrá, hurrá, hurrá'
    return render(request, 'project_proba.html', {'cont': cont})