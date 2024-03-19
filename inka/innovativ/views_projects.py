import os
from django.conf import settings

from django.shortcuts import render
from django.contrib import messages

from .forms_projects import CSVFileSelectForm


def p_01_1_ugyfel_adat_import(request, project):
    if request.method == 'POST':
        form = CSVFileSelectForm(request.POST, request.FILES)
        if form.is_valid():
            file_name = request.FILES['file'].name
            file_path = os.path.join(settings.BASE_DIR, 'import')
            file_path = os.path.join(file_path, file_name)
            if not os.path.exists(file_path):
                messages.success(request, 'Az import könytárban nem találtam a kiválasztott fájlt!')
            else:
                # Itt továbbíthatod a fájlnévet a feldolgozó nézetnek
                return render(request, 'home.html', {})
    else:
        form = CSVFileSelectForm()
    return render(request, 'p_01_1_ugyfel_adat_import.html', {'project': project, 'form': form})


def p_02_1_elso_megkereses(request, project):
    cont = '02.1.'
    return render(request, 'project_proba.html', {'project': project})


def p_02_2_adatok_egyeztetese(request, project):
    cont = '02.2.'
    return render(request, 'project_proba.html', {'project': project})


def p_02_3_ugyfel_tipus_meghatarozasa(request, project):
    cont = '02.3.'
    return render(request, 'project_proba.html', {'project': project})


def p_03_1_palyazat_tipusainak_folyamatai(request, project):
    cont = '03.1.'
    return render(request, 'project_proba.html', {'project': project})