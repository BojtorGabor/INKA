from django.shortcuts import render
from django.contrib import messages


def p_01_1_ugyfel_adat_import(request):
    cont = '01.1.'
    return render(request, 'project_proba.html', {'cont': cont})


def p_02_1_elso_megkereses(request):
    cont = '02.1.'
    return render(request, 'project_proba.html', {'cont': cont})


def p_02_2_adatok_egyeztetese(request):
    cont = '02.2.'
    return render(request, 'project_proba.html', {'cont': cont})


def p_02_3_ugyfel_tipus_meghatarozasa(request):
    cont = '02.3.'
    return render(request, 'project_proba.html', {'cont': cont})


def p_03_1_palyazat_tipusainak_folyamatai(request):
    cont = '03.1.'
    return render(request, 'project_proba.html', {'cont': cont})